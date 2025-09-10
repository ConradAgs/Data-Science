import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import os
import requests
from io import BytesIO
import time

# =======================
# URLs des fichiers sur Google Drive
# =======================
EMBEDDINGS_DRIVE_URL = "https://drive.google.com/file/d/16LJE9fzGhbnM6ydlGL0pYW4ammaahGX1/view?usp=drive_link"
JOBS_DRIVE_URL = "https://drive.google.com/file/d/1aWcq2k1uttNFfk4btxOLkPB-vf4UnGgH/view?usp=drive_link"

# =======================
# Fonctions de téléchargement
# =======================
def download_file_from_drive(url, max_retries=3):
    """Télécharge un fichier depuis Google Drive avec gestion des erreurs"""
    for attempt in range(max_retries):
        try:
            session = requests.Session()
            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.warning(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
            time.sleep(2)
    return None

def import_json_from_drive(url):
    """Charge un JSON depuis Google Drive"""
    content = download_file_from_drive(url)
    if content:
        return json.loads(content.decode('utf-8'))
    return None

def load_npy_from_drive(url):
    """Charge un fichier .npy depuis Google Drive avec allow_pickle=True"""
    content = download_file_from_drive(url)
    if content:
        return np.load(BytesIO(content), allow_pickle=True)
    return None

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
# Callbacks pour la pagination
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
# Fonctions d'affichage
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
            <div class="offer-title">{offer['title']}</div>
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

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.button("⏪ Première", disabled=current_page == 0, on_click=go_to_first_page, use_container_width=True)

    with col2:
        st.button("◀️ Précédente", disabled=current_page == 0, on_click=go_to_previous_page, use_container_width=True)

    with col3:
        st.button("Suivante ▶️", disabled=current_page >= total_pages - 1, on_click=go_to_next_page, use_container_width=True)

    with col4:
        st.button("Dernière ⏩", disabled=current_page >= total_pages - 1, on_click=go_to_last_page, use_container_width=True)

# =======================
# Application principale
# =======================
def main():
    st.title("💼 RecrutoBot")
    st.markdown("*Version 100% locale sans API externe*")

    # Initialisation de la session state
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

    # Chargement des données
    if not st.session_state.data_loaded:
        with st.spinner("Chargement des données depuis Google Drive..."):
            try:
                # Charger les embeddings
                st.info("📥 Téléchargement des embeddings...")
                embeddings_data = load_npy_from_drive(EMBEDDINGS_DRIVE_URL)
                if embeddings_data is None:
                    st.error("❌ Impossible de charger les embeddings depuis Google Drive")
                    return
                
                st.session_state.offers_emb = torch.tensor(embeddings_data, dtype=torch.float32)
                
                # Charger le modèle
                st.info("🤖 Chargement du modèle...")
                st.session_state.model = SentenceTransformer("all-mpnet-base-v2", device="cpu")
                
                # Charger les offres d'emploi
                st.info("📋 Téléchargement des offres d'emploi...")
                offers_dict = import_json_from_drive(JOBS_DRIVE_URL)
                if offers_dict is None:
                    st.error("❌ Impossible de charger les offres d'emploi depuis Google Drive")
                    return
                
                st.session_state.offers = list(offers_dict.values())
                st.session_state.data_loaded = True
                st.success("✅ Données chargées avec succès!")

            except Exception as e:
                st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
                return

    # Interface chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.current_results:
        with st.chat_message("assistant"):
            if st.session_state.last_search:
                st.markdown(f"Voici les offres correspondant à votre recherche '{st.session_state.last_search}':")
            display_offers_page()
        display_pagination_controls()

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
                        query_emb = st.session_state.model.encode(prompt, convert_to_tensor=True)
                        cos_scores = util.cos_sim(query_emb, st.session_state.offers_emb)[0]
                        good_indices = [i for i, score in enumerate(cos_scores) if score > 0.4]

                        if not good_indices:
                            no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler votre recherche ?\n\nEx : 'Développeur Python junior à Paris'"
                            st.markdown(no_results_msg)
                            st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                            st.session_state.current_results = []
                        else:
                            st.session_state.current_results = []
                            for i in good_indices:
                                score = cos_scores[i]
                                offer = st.session_state.offers[i]
                                title = offer.get("TITLE") or offer.get("title") or "Titre non disponible"
                                text = offer.get("SUMMARY") or offer.get("text") or "Description non disponible"
                                st.session_state.current_results.append({
                                    "title": title,
                                    "description": text,
                                    "score": float(score)
                                })

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