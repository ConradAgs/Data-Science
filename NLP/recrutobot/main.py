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
# Téléchargement et chargement avec cache
# =======================
@st.cache_data
def download_files():
    """Télécharge les fichiers si absents (cache persistant)"""
    for filename, file_id in files.items():
        if not os.path.exists(filename):
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            gdown.download(url, filename, quiet=False)
    return True

@st.cache_resource
def load_model():
    return SentenceTransformer("all-mpnet-base-v2", device="cpu")

@st.cache_data
def load_embeddings(path: str):
    embedding = np.load(path, allow_pickle=True)
    return torch.tensor(embedding.astype(np.float32))

@st.cache_data
def load_offers(path: str):
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)

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
# CSS
# =======================
st.markdown("""
<style>
    .offer-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4b8bbe;
    }
    .offer-title { font-size: 1.2em; font-weight: bold; color: #1f4e79; margin-bottom: 8px; }
    .offer-description { font-size: 0.9em; color: #444444; line-height: 1.5; }
    .offer-score { font-size: 0.8em; color: #6c757d; text-align: right; margin-top: 5px; }
    .pagination-info { font-size: 0.9em; color: #6c757d; text-align: center; margin: 10px 0; }
    .stButton>button { width: 100%; background-color: #4b8bbe; color: white; }
    .stButton>button:disabled { background-color: #cccccc; color: #666666; }
</style>
""", unsafe_allow_html=True)

# =======================
# Pagination
# =======================
def go_to_first_page(): st.session_state.page_number = 0
def go_to_previous_page(): st.session_state.page_number = max(0, st.session_state.page_number - 1)
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
# Affichage
# =======================
def display_offers_page():
    if not st.session_state.current_results:
        return
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number
    start_idx = current_page * results_per_page
    end_idx = min((current_page + 1) * results_per_page, len(st.session_state.current_results))
    st.markdown(f"**📋 Résultats {start_idx+1}-{end_idx} sur {len(st.session_state.current_results)}**")
    for i in range(start_idx, end_idx):
        offer = st.session_state.current_results[i]
        st.markdown(f"""
        <div class="offer-card">
            <div class="offer-title">{offer['intitule']}</div>
            <div class="offer-description">{offer['description'][:250]}...</div>
            <div class="offer-score">Pertinence: {offer['score']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"<div class='pagination-info'>Page {current_page+1} sur {total_pages}</div>", unsafe_allow_html=True)

def display_pagination_controls():
    if not st.session_state.current_results:
        return
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("⏪ Première", disabled=current_page==0, on_click=go_to_first_page, use_container_width=True)
    with col2:
        st.button("◀️ Précédente", disabled=current_page==0, on_click=go_to_previous_page, use_container_width=True)
    with col3:
        st.button("Suivante ▶️", disabled=current_page>=total_pages-1, on_click=go_to_next_page, use_container_width=True)
    with col4:
        st.button("Dernière ⏩", disabled=current_page>=total_pages-1, on_click=go_to_last_page, use_container_width=True)

# =======================
# Main
# =======================
def main():
    st.title("💼 RecrutoBot")
    st.markdown("*Version locale sans API externe*")

    # Init state
    for key, default in {
        "page_number": 0, "current_results": [], "last_search": "", "messages": []
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Chargement des ressources
    with st.spinner("Chargement des données..."):
        try:
            download_files()
            model = load_model()
            offers_emb = load_embeddings("embedding.npy")
            offers = load_offers("jobs_catalogue2.json")
        except Exception as e:
            st.error(f"❌ Erreur au chargement : {e}")
            st.code(traceback.format_exc())
            return

    # Message d’accueil
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"
        })

    # Afficher historique
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Résultats
    if st.session_state.current_results:
        with st.chat_message("assistant"):
            st.markdown(f"Voici les offres correspondant à '{st.session_state.last_search}':")
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
                    query_emb = model.encode(prompt, convert_to_tensor=True)
                    cos_scores = util.cos_sim(query_emb, offers_emb)[0]
                    good_indices = [i for i, score in enumerate(cos_scores) if score > 0.4]
                    if not good_indices:
                        msg = "Aucune offre trouvée. Essayez de reformuler votre recherche."
                        st.markdown(msg)
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                        st.session_state.current_results = []
                    else:
                        st.session_state.current_results = [{
                            "intitule": offers[i].get("intitule", "Titre non disponible"),
                            "description": offers[i].get("description", "Description non disponible"),
                            "score": float(cos_scores[i])
                        } for i in good_indices]
                        st.session_state.current_results.sort(key=lambda x: x["score"], reverse=True)
                        st.markdown(f"Voici les offres correspondant à '{prompt}':")
                        display_offers_page()
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"J'ai trouvé {len(st.session_state.current_results)} offres correspondant à '{prompt}'"
                        })
                except Exception as e:
                    msg = f"Erreur recherche : {e}"
                    st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.current_results = []
        st.rerun()

if __name__ == "__main__":
    main()
