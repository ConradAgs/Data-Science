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
    page_title="RecrutoBot Local - Windows",
    page_icon="💼",
    layout="centered"
)

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

    # Interface chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour la recherche d'emploi. Comment puis-je vous aider ?"}
        ]

    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input utilisateur
    if prompt := st.chat_input("Ex: 'Développeur Python junior à Paris'"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Recherche en cours..."):
                try:
                    if not data_loaded:
                        error_msg = "Erreur recherche : [WinError 10061] Aucune connexion n'a pu être établie car l'ordinateur cible l'a expressément refusée"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # Encoder la requête
                        query_emb = model.encode(prompt, convert_to_tensor=True)

                        # Similarité cosinus
                        cos_scores = util.cos_sim(query_emb, offers_emb)[0]

                        # Top-k résultats
                        top_k = min(10, len(offers))
                        top_results = torch.topk(cos_scores, k=top_k)

                        if top_results.values[0] < 0.3:  # Seuil de similarité bas
                            no_results_msg = "Je n'ai trouvé aucune offre correspondante. Pouvez-vous reformuler votre recherche ?\n\nEx : 'Développeur Python junior à Paris'"
                            st.markdown(no_results_msg)
                            st.session_state.messages.append({"role": "assistant", "content": no_results_msg})
                        else:
                            response = f"Voici les offres correspondant à votre recherche '{prompt}':\n\n"

                            for idx, score in zip(top_results.indices, top_results.values):
                                if score < 0.3:  # Ignorer les résultats avec un score trop bas
                                    continue

                                offer = offers[int(idx)]
                                title = offer.get("TITLE") or offer.get("title") or "Titre non disponible"
                                text = offer.get("SUMMARY") or offer.get("text") or "Description non disponible"

                                response += f"**{title}** (score: {score:.3f})\n"
                                response += f"{text}\n\n"
                                response += "---\n\n"

                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"Erreur lors de la recherche: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()