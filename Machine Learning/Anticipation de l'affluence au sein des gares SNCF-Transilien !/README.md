# Prédiction des Validations Quotidiennes des Gares SNCF-Transilien

## Contexte
SNCF-Transilien, opérateur de trains de banlieue en Île-de-France, gère plus de 6 200 trains par jour pour transporter 3,2 millions de voyageurs. Ces voyageurs valident leurs cartes à puce sur nos portiques environ 2,3 millions de fois quotidiennement. Avec une croissance annuelle de 6 % entre 2015 et 2019, anticiper cette augmentation est crucial pour améliorer les services et optimiser l'exploitation.

Accédez au challenge : https://challengedata.ens.fr/participants/challenges/149/

## Objectif
Prédire à moyen-long terme le nombre de validations par jour et par gare afin d'anticiper les flux de voyageurs et de mieux comprendre les tendances à venir.

## Données
Les données proviennent de bases de validations d'Île-de-France Mobilités, comprenant :
- **date** : Jour de collecte des validations (format YYYY-MM-DD)
- **station** : Identifiant anonymisé des gares (ex. 7RP, J3V)
- **job** : Indicateur de jour ouvrable de base (1 = Oui, 0 = Non)
- **ferie** : Indicateur de jour férié (1 = Oui, 0 = Non)
- **vacances** : Indicateur de jour de vacances scolaires (1 = Oui, 0 = Non)
- **y** : Nombre de validations par jour et par gare

### Datasets
- **train.csv** : Données de 448 gares, couvrant la période du 1er janvier 2015 au 31 décembre 2022 (1 237 971 lignes, 6 colonnes).
- **test.csv** : Données des mêmes gares pour la période du 1er janvier 2023 au 30 juin 2023 (78 652 lignes, 6 colonnes).

## Méthodologie
### Exploration des Données
- Fusion des données d'entrée pour obtenir un dataset consolidé.
- Extraction de caractéristiques temporelles (jour, mois, année) et visualisation des tendances par gare.

### Modèles Utilisés
1. **Random Forest**
2. **LightGBM**
3. **XGBoost**

### Prétraitement
- Encodage One-Hot pour la variable `station`.
- Division des données en ensembles d'entraînement (60 %), de validation (20 %) et de test (20 %).

### Entraînement et Évaluation
- Les modèles ont été entraînés sur les données d'entraînement et évalués à l'aide des métriques suivantes :
  - **R²**
  - **Erreur quadratique moyenne (RMSE)**
  - **Erreur absolue moyenne (MAE)**

### Résultats
- Les performances des modèles ont été comparées sur les ensembles de validation et de test.
- Le modèle XGBoost a offert les meilleurs résultats sur l'ensemble de test :
  - **R²** : 0.86
  - **RMSE** : 120.45
  - **MAE** : 80.12

## Prédictions
Les données de test ont été prétraitées et encodées de manière similaire aux données d'entraînement. Les prédictions ont été réalisées avec le modèle XGBoost, puis sauvegardées dans un fichier CSV :
- **y_sncf_predit.csv** : Contient les prédictions pour chaque gare et chaque jour de la période de test.




