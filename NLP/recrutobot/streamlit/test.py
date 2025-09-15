import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import os
import gdown
import traceback

# =======================
# Configuration des fichiers Google Drive
# =======================
files = {
    "embedding.npy": "176y-qT1aYgry5m6hT2dRyEV4J-CcOlKj",
    "jobs_catalogue2.json": "1gzZCk3mtDXp8Y_siloYpCOJiJVCHY663"
}

# =======================
# Fonctions utilitaires
# =======================
def import_json(json_path):
    with open(json_path, "r", encoding="utf-8") as fp:
        return json.load(fp)

def download_files():
    """Télécharge les fichiers depuis Google Drive si absents"""
    for filename, file_id in files.items():
        if not os.path.exists(filename):
            try:
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
                gdown.download(url, filename, quiet=False)
            except Exception as e:
                st.error(f"❌ Erreur avec {filename}: {e}")
                return False
    return True

# =======================
# Configuration Streamlit
# =======================
st.set_page_config(
    page_title="RecrutoBot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =======================
# Styles CSS
# =======================
st.markdown("""
<style>
    .offer-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4b8bbe;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .offer-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #1f4e79;
        margin-bottom: 8px;
    }
    .offer-description {
        font-size: 0.9em;
        color: #444444;
        line-height: 1.5;
    }
    .offer-score {
        font-size: 0.8em;
        color: #6c757d;
        text-align: right;
        margin-top: 5px;
    }
    .pagination-info {
        font-size: 0.9em;
        color: #6c757d;
        text-align: center;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #4b8bbe;
        color: white;
    }
    .stButton>button:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# =======================
# Pagination
# =======================
def go_to_first_page():
    st.session_state.page_number = 0

def go_to_previous_page():
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1

def go_to_next_page():
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    if st.session_state.page_number < total_pages - 1:
        st.session_state.page_number += 1

def go_to_last_page():
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    st.session_state.page_number = total_pages - 1

# =======================
# Affichage des offres
# =======================
def display_offers_page():
    """Affiche une page d'offres avec un style amélioré"""
    if not st.session_state.current_results:
        return

    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number

    start_idx = current_page * results_per_page
    end_idx = min((current_page + 1) * results_per_page, len(st.session_state.current_results))

    st.markdown(f"**📋 Résultats {start_idx + 1}-{end_idx} sur {len(st.session_state.current_results)}**")

    for i in range(start_idx, end_idx):
        offer = st.session_state.current_results[i]
        st.markdown(f"""
        <div class="offer-card">
            <div class="offer-title">{offer['intitule']}</div>
            <div class="offer-description">{offer['description'][:250]}...</div>
            <div class="offer-score">Pertinence: {offer['score']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pagination-info">
        Page {current_page + 1} sur {total_pages}
    </div>
    """, unsafe_allow_html=True)

def display_pagination_controls():
    """Affiche les contrôles de pagination"""
    if not st.session_state.current_results:
        return

    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number
    search_key = st.session_state.last_search.replace(" ", "_")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.button("⏪ Première",
                 disabled=current_page == 0,
                 on_click=go_to_first_page,
                 key=f"first_page_{search_key}")

    with col2:
        st.button("◀️ Précédente",
                 disabled=current_page == 0,
                 on_click=go_to_previous_page,
                 key=f"prev_page_{search_key}")

    with col3:
        st.button("Suivante ▶️",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_next_page,
                 key=f"next_page_{search_key}")

    with col4:
        st.button("Dernière ⏩",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_last_page,
                 key=f"last_page_{search_key}")

# =======================
# Main App
# =======================
def main():
    st.title("💼 RecrutoBot")
    st.markdown("*Version 100% locale sans API externe*")

    # Init session state
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0
    if "current_results" not in st.session_state:
        st.session_state.current_results = []
    if "last_search" not in st.session_state:
        st.session_state.last_search = ""
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "model" not in st.session_state:
        st.session_state.model = None
    if "offers" not in st.session_state:
        st.session_state.offers = []
    if "offers_emb" not in st.session_state:
        st.session_state.offers_emb = None

    # Chargement des données (une seule fois)
    if not st.session_state.data_loaded:
        with st.spinner("Chargement des données..."):
            try:
                if not download_files():
                    st.error("❌ Impossible de télécharger les fichiers nécessaires")
                    return

                embedding = np.load("embedding.npy", allow_pickle=True)
                st.session_state.offers_emb = torch.tensor(embedding.astype(np.float16))  # stockage en float16

                st.info("🤖 Chargement du modèle...")
                st.session_state.model = SentenceTransformer("all-mpnet-base-v2", device="cpu")

                st.info("📋 Chargement des offres d'emploi...")
                st.session_state.offers = import_json("jobs_catalogue2.json")

                st.session_state.data_loaded = True
                st.write(f"📈 {len(st.session_state.offers)} offres chargées")

            except Exception as e:
                st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
                st.code(traceback.format_exc())
                return

    # Historique chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Affichage résultats existants
    if st.session_state.current_results:
        with st.chat_message("assistant"):
            if st.session_state.last_search:
                st.markdown(f"Voici les offres correspondant à votre recherche '{st.session_state.last_search}':")
        display_offers_page()
        display_pagination_controls()

    # Input utilisateur
    if prompt := st.chat_input("Ex: 'Développeur Python junior à Paris'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.page_number = 0
        st.session_state.last_search = prompt

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Recherche en cours..."):
                try:
                    if not st.session_state.data_loaded:
                        error_msg = "Erreur recherche : Données non chargées"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        st.session_state.current_results = []
                    else:
                        # Encoder la requête en float16
                        query_emb = st.session_state.model.encode(
                            prompt, convert_to_tensor=True
                        ).to(torch.float16)

                        cos_scores = util.cos_sim(query_emb, st.session_state.offers_emb)[0]
                        good_indices = [i for i, score in enumerate(cos_scores) if score > 0.4]

                        if not good_indices:
                            no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler ?"
                            st.markdown(no_results_msg)
                            st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                            st.session_state.current_results = []
                        else:
                            st.session_state.current_results = []
                            for i in good_indices:
                                score = cos_scores[i]
                                offer = st.session_state.offers[i]
                                st.session_state.current_results.append({
                                    "intitule": offer.get("intitule") or "Titre non disponible",
                                    "description": offer.get("description") or "Description non disponible",
                                    "score": float(score)
                                })
                            st.session_state.current_results.sort(key=lambda x: x["score"], reverse=True)

                            st.markdown(f"Voici les offres correspondant à votre recherche '{prompt}':")
                            display_offers_page()
                            display_pagination_controls()

                            results_count = len(st.session_state.current_results)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"J'ai trouvé {results_count} offres correspondant à '{prompt}'"
                            })
                except Exception as e:
                    error_msg = f"Erreur lors de la recherche: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.current_results = []

if __name__ == "__main__":
    main()
