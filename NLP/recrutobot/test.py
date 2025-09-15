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

def download_if_needed(filename, file_id):
    """Télécharge un fichier depuis Google Drive s’il n’existe pas déjà"""
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        gdown.download(url, filename, quiet=False)

# =======================
# Mise en cache des ressources
# =======================
@st.cache_resource
def load_model():
    return SentenceTransformer("all-mpnet-base-v2", device="cpu")

@st.cache_data
def load_embeddings():
    download_if_needed("embedding.npy", files["embedding.npy"])
    emb = np.load("embedding.npy", allow_pickle=True)
    return torch.tensor(emb.astype(np.float16))  # optimisation mémoire

@st.cache_data
def load_offers():
    download_if_needed("jobs_catalogue2.json", files["jobs_catalogue2.json"])
    with open("jobs_catalogue2.json", "r", encoding="utf-8") as f:
        return json.load(f)

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
# Chargement initial
# =======================
st.title("💼 RecrutoBot")
st.markdown("*Version optimisée avec cache*")

try:
    with st.spinner("Chargement du modèle et des données..."):
        model = load_model()
        offers_emb = load_embeddings()
        offers = load_offers()
    st.success(f"📈 {len(offers)} offres chargées")
except Exception as e:
    st.error("❌ Erreur lors du chargement")
    st.code(traceback.format_exc())
    st.stop()

# =======================
# Historique chat
# =======================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
    ]

if "results" not in st.session_state:
    st.session_state.results = []
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

# Afficher l’historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =======================
# Recherche utilisateur
# =======================
if prompt := st.chat_input("Ex: 'Développeur Python junior à Paris'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.page_number = 0

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche en cours..."):
            try:
                # Encoder la requête
                query_emb = model.encode(prompt, convert_to_tensor=True)
                cos_scores = util.cos_sim(query_emb, offers_emb)[0]

                # Filtrer les résultats pertinents
                good_indices = [i for i, score in enumerate(cos_scores) if score > 0.4]

                if not good_indices:
                    msg = "Aucune offre trouvée. Essayez : 'Développeur Python junior à Paris'."
                    st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.results = []
                else:
                    # Construire la liste des résultats
                    results = []
                    for i in good_indices:
                        results.append({
                            "intitule": offers[i].get("intitule", "Titre non disponible"),
                            "description": offers[i].get("description", "Description non disponible"),
                            "score": float(cos_scores[i])
                        })
                    results.sort(key=lambda x: x["score"], reverse=True)

                    st.session_state.results = results
                    msg = f"J'ai trouvé {len(results)} offres correspondant à '{prompt}'"
                    st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})

            except Exception as e:
                err = f"Erreur lors de la recherche: {str(e)}"
                st.markdown(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
                st.session_state.results = []

# =======================
# Affichage des résultats
# =======================
def display_offers(results, page, per_page=5):
    if not results:
        return
    start, end = page * per_page, min((page + 1) * per_page, len(results))
    st.markdown(f"📋 Résultats {start+1}-{end} sur {len(results)}")
    for offer in results[start:end]:
        st.markdown(f"""
        <div style="background:#f8f9fa;padding:10px;margin:10px 0;border-left:5px solid #4b8bbe;border-radius:8px;">
            <b>{offer['intitule']}</b><br>
            {offer['description'][:250]}...<br>
            <i>Pertinence: {offer['score']:.3f}</i>
        </div>
        """, unsafe_allow_html=True)

def pagination_controls(results, page, per_page=5):
    if not results:
        return
    total_pages = (len(results) + per_page - 1) // per_page
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("⏪ Première", disabled=page == 0, key=f"first_{page}", on_click=lambda: st.session_state.update(page_number=0))
    with col2:
        st.button("◀️ Précédente", disabled=page == 0, key=f"prev_{page}", on_click=lambda: st.session_state.update(page_number=page-1))
    with col3:
        st.button("Suivante ▶️", disabled=page >= total_pages-1, key=f"next_{page}", on_click=lambda: st.session_state.update(page_number=page+1))
    with col4:
        st.button("Dernière ⏩", disabled=page >= total_pages-1, key=f"last_{page}", on_click=lambda: st.session_state.update(page_number=total_pages-1))

if st.session_state.results:
    display_offers(st.session_state.results, st.session_state.page_number)
    pagination_controls(st.session_state.results, st.session_state.page_number)
