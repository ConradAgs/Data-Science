#%% Bibliothèques

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import ast
import json






#%% Import des données

def read_json(file_path):
    fp = open(file_path, "r", encoding='utf-8')
    data = json.load(fp)  # Charge les données JSON
    fp.close()
    return data

job_listings = read_json("job_listings.json")






#%% Fonctions intermédiaires

unique_job_ids = sorted(map(int, job_listings.keys())) # Extraire tous les job_ids uniques

def creation_R(train_data):
    train_data['job_ids'] = train_data['job_ids'].apply(ast.literal_eval) # Convertit les chaines de caractères de la colonne en leur véritable objet (ici, une liste)
    train_data['actions'] = train_data['actions'].apply(ast.literal_eval)
    unique_session_id = list(set(list(train_data['session_id']))) # Extraire tous les session_ID unique

    R = pd.DataFrame(0, index=unique_session_id, columns=unique_job_ids, dtype=np.int32)


    # Remplir la matrice Rui
    for i, row in train_data.iterrows():
        session_id = row['session_id']
        job_ids = row['job_ids']
        
        for job_id in job_ids:
            R.at[session_id, job_id] = 1
    return R


def similarite_cosinus(Rui, Rvi):
    num = np.dot(Rui, Rvi) 
    denom = np.linalg.norm(Rui) * np.linalg.norm(Rvi)
    return num / denom if denom != 0 else 0


def k_proches_voisin(individu, R, k):
    Uc = [similarite_cosinus(np.array(individu), np.array(R.iloc[i])) for i in range(R.shape[0])]
    return np.argsort(Uc)[-k:]


def score_emploi(Uc, R):
    scores = {}
    for emploi in unique_job_ids:
        scores[emploi] = sum(R.iloc[voisin][emploi] for voisin in Uc) / len(Uc)
    return scores

def recommander_emplois(Uc, R, n=10):
    scores = score_emploi(Uc, R)
    return sorted(scores, key = scores.get, reverse=True)[:n]


def predire_intention_postuler(theta, emplois_recommandes, scores):
    P_c_moyenne = np.mean([scores[emploi] for emploi in emplois_recommandes])
    return int(P_c_moyenne >= theta)






#%% Fonction de recommandation

def recommandation_d_emploi(test_data):
    y_test = pd.DataFrame(columns = ["session_id","job_id","action"])
    R = creation_R(test_data)
    for i, utilisateur in R.iterrows():
        Q = R.drop(i)
        Uc = k_proches_voisin(utilisateur, Q, k)
        scores = score_emploi(Uc, Q)
        id_10_emploi = recommander_emplois(Uc, Q)
        prochaine_action = predire_intention_postuler(theta, id_10_emploi, scores)
        y_test = pd.concat([y_test, pd.DataFrame({"session_id": [i], 
                                                  "job_id": [id_10_emploi], 
                                                  "action": [prochaine_action]})], ignore_index = True)
        if i % 100 == 0:
            print(f"Progression : {i}/{len(R)} individus traités")

    return y_test






#%% Test

train_data = pd.read_csv("x_train_Meacfjr.csv")
theta = 0.4
k = 100
y_train = recommandation_d_emploi(train_data)
y_train.to_csv('y_trains.csv', index=False, sep=';', encoding='utf-8')


