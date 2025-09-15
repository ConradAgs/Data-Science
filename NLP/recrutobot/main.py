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
        data = json.load(fp)
    return data

def download_file_once(filename, file_id):
    """Télécharge un fichier depuis Google Drive seulement s'il n'existe pas déjà."""
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        gdown.download(url, filename, quiet=False)
    return filename

# =======================
# Mise en cache des ressources lourdes
# =======================
@st.cache_resource
def load_model():
    return SentenceTransformer("all-mpnet-base-v2", device="cpu")

@st.cache_data
def load_embeddings():
    path = download_file_once("embedding.npy", files["embedding.npy"])
    embedding = np.load(path, allow_pickle=True)
    return torch.tensor(embedding.astype(np.float32))

@st.cache_data
def load_offers():
    path = download_file_once("jobs_catalogue2.json", files["jobs_catalogue2.json"])
    return import_json(path)

# =======================
# Configuration de la page
# =======================
st.set_page_config(
    page_title="RecrutoBot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =======================
# Styles CSS personnalisés
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
# Callbacks pagination
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
    if not st.session_state.current_results:
        return

    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.button("⏪ Première",
                 disabled=current_page == 0,
                 on_click=go_to_first_page,
                 use_container_width=True)

    with col2:
        st.button("◀️ Précédente",
                 disabled=current_page == 0,
                 on_click=go_to_previous_page,
                 use_container_width=True)

    with col3:
        st.button("Suivante ▶️",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_next_page,
                 use_container_width=True)

    with col4:
        st.button("Dernière ⏩",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_last_page,
                 use_container_width=True)

# =======================
# Main
# =======================
def main():
    st.title("💼 RecrutoBot")
    st.markdown("*Version optimisée avec cache (pas de retéléchargement)*")

    # Initialisation session_state
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0
    if "current_results" not in st.session_state:
        st.session_state.current_results = []
    if "last_search" not in st.session_state:
        st.session_state.last_search = ""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

    # Chargement unique des ressources
    try:
        model = load_model()
        offers_emb = load_embeddings()
        offers = load_offers()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        st.code(traceback.format_exc())
        return

    # Afficher l'historique du chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Afficher les résultats si dispo
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
                    # Encoder la requête
                    query_emb = model.encode(prompt, convert_to_tensor=True)

                    # Similarité cosinus (conversion en numpy)
                    cos_scores = util.cos_sim(query_emb, offers_emb)[0].cpu().numpy()

                    # Filtrer les résultats > 0.4
                    good_indices = [i for i, score in enumerate(cos_scores) if score > 0.4]

                    if not good_indices:
                        no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler votre recherche ?"
                        st.markdown(no_results_msg)
                        st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                        st.session_state.current_results = []
                    else:
                        st.session_state.current_results = []
                        for i in good_indices:
                            score = cos_scores[i]
                            offer = offers[i]
                            title = offer.get("intitule") or "Titre non disponible"
                            text = offer.get("description") or "Description non disponible"
                            st.session_state.current_results.append({
                                "intitule": title,
                                "description": text,
                                "score": float(score)
                            })

                        # Trier par score décroissant
                        st.session_state.current_results.sort(key=lambda x: x["score"], reverse=True)

                        st.markdown(f"Voici les offres correspondant à votre recherche '{prompt}':")
                        display_offers_page()

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
