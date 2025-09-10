import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer, util
import streamlit as st

# =======================
# Fonctions
# =======================
def import_json(json_path):
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    return data

# =======================
# Configuration de la page
# =======================
st.set_page_config(
    page_title="RecrutoBot",
    page_icon="💼",
    layout="centered"
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
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number

    start_idx = current_page * results_per_page
    end_idx = min((current_page + 1) * results_per_page, len(st.session_state.current_results))

    st.markdown(f"**📋 Résultats {start_idx + 1}-{end_idx} sur {len(st.session_state.current_results)}**")

    for i in range(start_idx, end_idx):
        offer = st.session_state.current_results[i]

        # Utiliser du HTML/CSS pour un affichage plus esthétique
        st.markdown(f"""
        <div class="offer-card">
            <div class="offer-title">{offer['title']}</div>
            <div class="offer-description">{offer['description'][:250]}...</div>
            <div class="offer-score">Pertinence: {offer['score']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Information sur la pagination
    st.markdown(f"""
    <div class="pagination-info">
        Page {current_page + 1} sur {total_pages}
    </div>
    """, unsafe_allow_html=True)

def display_pagination_controls():
    """Affiche les contrôles de pagination"""
    results_per_page = 5
    total_pages = max(1, (len(st.session_state.current_results) + results_per_page - 1) // results_per_page)
    current_page = st.session_state.page_number

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.button("⏪ Première",
                 disabled=current_page == 0,
                 on_click=go_to_first_page,
                 key="first_page_btn")

    with col2:
        st.button("◀️ Précédente",
                 disabled=current_page == 0,
                 on_click=go_to_previous_page,
                 key="prev_page_btn")

    with col3:
        st.button("Suivante ▶️",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_next_page,
                 key="next_page_btn")

    with col4:
        st.button("Dernière ⏩",
                 disabled=current_page >= total_pages - 1,
                 on_click=go_to_last_page,
                 key="last_page_btn")

# =======================
# Chargement des fichiers
# =======================
def main():
    st.title("💼 RecrutoBot Local - Windows")
    st.markdown("*Version 100% locale sans API externe*")

    try:
        offers_emb = np.load("C:/Users/conra/Desktop/MAS2/NLP/NLP/Recommandation d'emploi/embedding_modele1.npy")
        offers_emb = torch.tensor(offers_emb)  # conversion en tensor

        model = SentenceTransformer("all-mpnet-base-v2", device="cpu")
        offers_dict = import_json("C:/Users/conra/Desktop/MAS2/NLP/NLP/Recommandation d'emploi/jobs_catalogue.json")

        # Convertir dict en liste pour l'indexation
        offers = list(offers_dict.values())

        data_loaded = True
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        data_loaded = False

    # Initialisation de la session state
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0
    if "current_results" not in st.session_state:
        st.session_state.current_results = []
    if "last_search" not in st.session_state:
        st.session_state.last_search = ""

    # Interface chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Afficher les résultats de la recherche actuelle si elle existe
    if st.session_state.current_results:
        with st.chat_message("assistant"):
            # Afficher le message de recherche
            if st.session_state.last_search:
                st.markdown(f"Voici les offres correspondant à votre recherche '{st.session_state.last_search}':")

            # Afficher les offres
            display_offers_page()

        # Afficher les contrôles de pagination (TOUJOURS en dehors du chat message)
        display_pagination_controls()

    # Input utilisateur
    if prompt := st.chat_input("Ex: 'Développeur Python junior à Paris'"):
        # Ajouter le message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.page_number = 0  # Réinitialiser la pagination
        st.session_state.last_search = prompt  # Stocker la dernière recherche

        # Afficher le message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)

        # Traiter la recherche
        with st.chat_message("assistant"):
            with st.spinner("🔍 Recherche en cours..."):
                try:
                    if not data_loaded:
                        error_msg = "Erreur recherche : Données non chargées"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        st.session_state.current_results = []
                    else:
                        # Encoder la requête
                        query_emb = model.encode(prompt, convert_to_tensor=True)

                        # Similarité cosinus
                        cos_scores = util.cos_sim(query_emb, offers_emb)[0]

                        # Filtrer les résultats avec un score > 0.3
                        good_indices = [i for i, score in enumerate(cos_scores) if score > 0.3]

                        if not good_indices:
                            no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler votre recherche ?\n\nEx : 'Développeur Python junior à Paris'"
                            st.markdown(no_results_msg)
                            st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                            st.session_state.current_results = []
                        else:
                            # Stocker les résultats dans la session state
                            st.session_state.current_results = []
                            for i in good_indices:
                                score = cos_scores[i]
                                offer = offers[i]
                                title = offer.get("TITLE") or offer.get("title") or "Titre non disponible"
                                text = offer.get("SUMMARY") or offer.get("text") or "Description non disponible"
                                st.session_state.current_results.append({
                                    "title": title,
                                    "description": text,
                                    "score": float(score)
                                })

                            # Trier par score décroissant
                            st.session_state.current_results.sort(key=lambda x: x["score"], reverse=True)

                            # Afficher le message de résultats
                            st.markdown(f"Voici les offres correspondant à votre recherche '{prompt}':")

                            # Afficher la première page
                            display_offers_page()

                            # Ajouter le message à l'historique
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

        # Forcer le rerun pour afficher immédiatement les boutons de pagination
        st.rerun()

if __name__ == "__main__":
    main()