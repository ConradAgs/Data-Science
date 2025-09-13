import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import os
import gdown
import time
import traceback

# =======================
# Configuration des fichiers Google Drive
# =======================
files = {
    "embedding.npy": "176y-qT1aYgry5m6hT2dRyEV4J-CcOlKj",
    "jobs_catalogue2.json": "1gzZCk3mtDXp8Y_siloYpCOJiJVCHY663"
}

# =======================
# Fonctions
# =======================
def import_json(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return data
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier JSON: {e}")
        return []

def download_files():
    """Télécharge les fichiers depuis Google Drive"""
    success = True
    for filename, file_id in files.items():
        try:
            if not os.path.exists(filename):
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
                gdown.download(url, filename, quiet=False)
                st.success(f"Fichier {filename} téléchargé avec succès")

            # Vérifier que le fichier a été téléchargé correctement
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                st.error(f"Le fichier {filename} est vide ou n'existe pas")
                success = False

        except Exception as e:
            st.error(f"❌ Erreur avec {filename}: {e}")
            success = False
    return success

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
# Initialisation de la session state
# =======================
def init_session_state():
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
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

# =======================
# Chargement des données optimisé
# =======================
def load_data():
    """Charge les données avec gestion d'erreurs améliorée"""
    try:
        # Télécharger les fichiers
        if not download_files():
            return False

        # Charger les embeddings avec gestion mémoire
        st.info("📊 Chargement des embeddings...")
        if os.path.exists("embedding.npy"):
            # Charger en mode mémoire mappée pour économiser la RAM
            embedding = np.load("embedding.npy", allow_pickle=True, mmap_mode='r')
            st.session_state.offers_emb = torch.tensor(embedding.astype(np.float32))
            del embedding  # Libérer la mémoire
        else:
            st.error("Fichier embedding.npy non trouvé")
            return False

        # Charger le modèle avec gestion mémoire
        st.info("🤖 Chargement du modèle...")
        try:
            # Utiliser un modèle plus léger si possible
            st.session_state.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        except:
            # Fallback au modèle original
            st.session_state.model = SentenceTransformer("all-mpnet-base-v2", device="cpu")

        # Charger les offres d'emploi
        st.info("📋 Chargement des offres d'emploi...")
        if os.path.exists("jobs_catalogue2.json"):
            st.session_state.offers = import_json("jobs_catalogue2.json")
            if not st.session_state.offers:
                st.error("Aucune offre chargée")
                return False
        else:
            st.error("Fichier jobs_catalogue2.json non trouvé")
            return False

        st.success(f"📈 {len(st.session_state.offers)} offres chargées")
        return True

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        st.code(traceback.format_exc())
        return False

# =======================
# Fonctions de recherche
# =======================
def perform_search(query):
    """Effectue une recherche sémantique dans les offres d'emploi"""
    try:
        # Encoder la requête
        query_emb = st.session_state.model.encode(query, convert_to_tensor=True)

        # Similarité cosinus
        cos_scores = util.cos_sim(query_emb, st.session_state.offers_emb)[0]

        # Filtrer les résultats avec un score > 0.3 (seuil plus bas)
        good_indices = [i for i, score in enumerate(cos_scores) if score > 0.3]

        if not good_indices:
            return []

        # Préparer les résultats
        results = []
        for i in good_indices:
            score = cos_scores[i]
            offer = st.session_state.offers[i]
            title = offer.get("intitule", "Titre non disponible")
            description = offer.get("description", "Description non disponible")
            results.append({
                "intitule": title,
                "description": description[:300] + "..." if len(description) > 300 else description,
                "score": float(score)
            })

        # Trier par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:20]  # Limiter à 20 résultats

    except Exception as e:
        st.error(f"Erreur lors de la recherche: {str(e)}")
        return []

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
            <div class="offer-title">{offer['intitule']}</div>
            <div class="offer-description">{offer['description']}</div>
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
        st.button("⏪ Première",
                 disabled=current_page == 0,
                 on_click=lambda: st.session_state.update(page_number=0),
                 use_container_width=True)

    with col2:
        st.button("◀️ Précédente",
                 disabled=current_page == 0,
                 on_click=lambda: st.session_state.update(page_number=max(0, current_page - 1)),
                 use_container_width=True)

    with col3:
        st.button("Suivante ▶️",
                 disabled=current_page >= total_pages - 1,
                 on_click=lambda: st.session_state.update(page_number=min(total_pages - 1, current_page + 1)),
                 use_container_width=True)

    with col4:
        st.button("Dernière ⏩",
                 disabled=current_page >= total_pages - 1,
                 on_click=lambda: st.session_state.update(page_number=total_pages - 1),
                 use_container_width=True)

# =======================
# Application principale
# =======================
def main():
    st.title("💼 RecrutoBot")
    st.markdown("*Version 100% locale sans API externe*")

    # Initialisation de la session state
    init_session_state()

    # Chargement des données (une seule fois)
    if not st.session_state.data_loaded:
        with st.spinner("Chargement des données..."):
            st.session_state.data_loaded = load_data()

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Afficher les résultats de la recherche actuelle si elle existe
    if st.session_state.current_results:
        with st.chat_message("assistant"):
            if st.session_state.last_search:
                st.markdown(f"Voici les offres correspondant à votre recherche '{st.session_state.last_search}':")

        display_offers_page()
        display_pagination_controls()

    # Input utilisateur
    if prompt := st.chat_input("Ex: 'Développeur Python junior à Paris'"):
        # Ajouter le message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.page_number = 0
        st.session_state.last_search = prompt

        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)

        # Traiter la recherche
        with st.chat_message("assistant"):
            if not st.session_state.data_loaded:
                error_msg = "Erreur recherche : Données non chargées"
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner("🔍 Recherche en cours..."):
                    results = perform_search(prompt)

                    if not results:
                        no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler votre recherche ?\n\nEx : 'Développeur Python junior à Paris'"
                        st.markdown(no_results_msg)
                        st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                        st.session_state.current_results = []
                    else:
                        st.session_state.current_results = results
                        st.markdown(f"Voici les offres correspondant à votre recherche '{prompt}':")
                        display_offers_page()

                        results_count = len(results)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"J'ai trouvé {results_count} offres correspondant à '{prompt}'"
                        })

        st.rerun()

if __name__ == "__main__":
    main()