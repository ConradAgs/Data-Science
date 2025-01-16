#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import lightgbm as lgb
import xgboost as xgb
from statsmodels.tsa.api import VAR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

#%% Importation de mes donnees
train1 = pd.read_csv('train_f_x.csv')
train2 = pd.read_csv('y_train_sncf.csv')
X_a_predire = pd.read_csv('test_f_x_THurtzP.csv')


#%% Fusion de mes données d'entrainement
train1['index']=train1.date + '_' + train1.station
data = pd.merge(train1, train2, on='index')
data['date'] = pd.to_datetime(data['date'])
data.head()

#%%
# Conversion de la colonne 'date' en datetime et extraction des informations temporelles si pertinent
data['date'] = pd.to_datetime(data['date'])
data['day'] = data['date'].dt.day
data['month'] = data['date'].dt.month
data['year'] = data['date'].dt.year
print(data.head())

filtered_data = data[data['station'] == 'O2O']
print(filtered_data.head())

#%%  Visualisation du prix par jour
sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.lineplot(x='date', y='y', data=filtered_data)
plt.title("Distribution de y par jour")
plt.xlabel("Jour")
plt.ylabel("y")
plt.show()

#%% Pré-traitement des données
# Encodage de la variable station
encoder = OneHotEncoder(sparse_output=False, drop='first')
stations_encoded = encoder.fit_transform(data[['station']])
stations_encoded_df = pd.DataFrame(stations_encoded, columns=encoder.get_feature_names_out(['station']))

# Ajout des colonnes encodées aux données
data = pd.concat([data, stations_encoded_df], axis=1)
data = data.drop(['station', 'index'], axis=1)
# Séparation en X et de la cible y
X = data.drop(['y', 'date'], axis=1)
y = data['y']

#%%
print(X.head())
print(y.head())


#%% Séparation des données en ensembles d'entraînement, test et validation
# Étape 1 : Diviser en 60% train, 40% validation + test
X_train, X_val_test, y_train, y_val_test = train_test_split(X, y, test_size=0.4, random_state=42)
# Étape 2 : Diviser le 40% restant en 20% validation, 20% test
X_val, X_test, y_val, y_test = train_test_split(X_val_test, y_val_test, test_size=0.5, random_state=42)


#%% Création et entraînement du modèle de forêt aléatoire
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

#%% Prédiction
#  Prédictions sur le set de validation
y_val_pred_rf = model.predict(X_val)
# Prédictions sur le set de test
y_test_pred_rf = model.predict(X_test)


#%%
print(y_val_pred_rf)
print(y_test_pred_rf)


#%%
# Évaluation sur le set de validation
RMSE = np.sqrt(mean_squared_error(y_val, y_val_pred_rf))
R2 = r2_score(y_val, y_val_pred_rf)
MAE = mean_absolute_error(y_val, y_val_pred_rf)
print(f"(Random Forest) le R2 sur l'ensemble de validation est : {R2:.4f}")
print(f"(Random Forest) L'erreur quadratique moyenne sur l'ensemble de validation: {RMSE:.4f}")
print(f"(Random Forest) L'erreur absolue moyenne sur l'ensemble de validation: {MAE:.4f}")

# Évaluation sur le set de test
RMSE = np.sqrt(mean_squared_error(y_test, y_test_pred_rf))
R2 = r2_score(y_test, y_test_pred_rf)
MAE = mean_absolute_error(y_test, y_test_pred_rf)
print(f"(Random Forest) le R2 sur l'ensemble de test est : {R2:.4f}")
print(f"(Random Forest) L'erreur quadratique moyenne sur l'ensemble de test: {RMSE:.4f}")
print(f"(Random Forest) L'erreur absolue moyenne sur l'ensemble de test: {MAE:.4f}")




#%% Voyons ce que ça donne avec LightGBM

model2 = lgb.LGBMRegressor()
model2.fit(X_train, y_train)

#  Prédictions sur le set de validation
y_val_pred_rf2 = model2.predict(X_val)
# Prédictions sur le set de test
y_test_pred_rf2 = model2.predict(X_test)


# Évaluation sur le set de validation
RMSE_lGBM = np.sqrt(mean_squared_error(y_val, y_val_pred_rf2))
R2_lGBM = r2_score(y_val, y_val_pred_rf2)
MAE_lGBM = mean_absolute_error(y_val, y_val_pred_rf2)
print(f"(LIGHT GBM) le R2 sur l'ensemble de validation est : {R2_lGBM:.4f}")
print(f"(LIGHT GBM) L'erreur quadratique moyenne sur l'ensemble de validation: {RMSE_lGBM:.4f}")
print(f"(LIGHT GBM) L'erreur absolue moyenne sur l'ensemble de validation: {MAE_lGBM:.4f}")

# Évaluation sur le set de test
RMSE_lGBM = np.sqrt(mean_squared_error(y_test, y_test_pred_rf2))
R2_lGBM = r2_score(y_test, y_test_pred_rf2)
MAE_lGBM = mean_absolute_error(y_test, y_test_pred_rf2)
print(f"(LIGHT GBM) le R2 sur l'ensemble de test est : {R2_lGBM:.4f}")
print(f"(LIGHT GBM) L'erreur quadratique moyenne sur l'ensemble de test: {RMSE_lGBM:.4f}")
print(f"(LIGHT GBM) L'erreur absolue moyenne sur l'ensemble de test: {MAE_lGBM:.4f}")




#%% Voyons ce que ça donne avec XGBoost

# Création et entraînement du modèle XGBoost
#model3 = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.05)
model3 = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, learning_rate=0.08, max_depth=8,           min_child_weight=1, n_jobs=-1)
model3.fit(X_train, y_train)

#  Prédictions sur le set de validation
y_val_pred_rf3 = model3.predict(X_val)
# Prédictions sur le set de test
y_test_pred_rf3 = model3.predict(X_test)


# Évaluation sur le set de validation
RMSE_xgboost = np.sqrt(mean_squared_error(y_val, y_val_pred_rf3))
R2_xgboost = r2_score(y_val, y_val_pred_rf3)
MAE_xgboost = mean_absolute_error(y_val, y_val_pred_rf3)
print(f"(XGBoost) le R2 sur l'ensemble de validation est : {R2_xgboost:.4f}")
print(f"(XGBoost) L'erreur quadratique moyenne sur l'ensemble de validation: {RMSE_xgboost:.4f}")
print(f"(XGBoost) L'erreur absolue moyenne sur l'ensemble de validation: {MAE_xgboost:.4f}")

# Évaluation sur le set de test
RMSE_xgboost = np.sqrt(mean_squared_error(y_test, y_test_pred_rf3))
R2_xgboost = r2_score(y_test, y_test_pred_rf3)
MAE_xgboost = mean_absolute_error(y_test, y_test_pred_rf3)
print(f"(XGBoost) le R2 sur l'ensemble de test est : {R2_xgboost:.4f}")
print(f"(XGBoost) L'erreur quadratique moyenne sur l'ensemble de test: {RMSE_xgboost:.4f}")
print(f"(XGBoost) L'erreur absolue moyenne sur l'ensemble de test: {MAE_xgboost:.4f}")




# %% Prédiction des valeurs cibles

# Création d'une copie de mes données
test_copy = X_a_predire.copy()

y_sncf_predit = (test_copy['date'] + '_' + test_copy['station']).to_frame()

# Extraction des informations temporelles
test_copy['date'] = pd.to_datetime(test_copy['date'])
test_copy['day'] = test_copy['date'].dt.day
test_copy['month'] = test_copy['date'].dt.month
test_copy['year'] = test_copy['date'].dt.year

# Encodage de la variable station
encoder = OneHotEncoder(sparse_output=False, drop='first')
stations_encoded = encoder.fit_transform(test_copy[['station']])
stations_encoded_df = pd.DataFrame(stations_encoded, columns=encoder.get_feature_names_out(['station']))

# Ajout des colonnes encodées aux données
train_data_encoded = pd.concat([test_copy, stations_encoded_df], axis=1)
train_data_encoded = train_data_encoded.drop(['station', 'index', 'date'], axis=1)

print(train_data_encoded.head())

# Prediction
y_chap = model.predict(train_data_encoded)
y_chap = y_chap.astype(int)

# Ajouter y_chap comme nouvelle colonne dans y_sncf_predit et exporter le dataframe
y_sncf_predit['y_chap'] = y_chap

y_sncf_predit.columns = ['index', 'y']

y_sncf_predit.to_csv("y_sncf_predit.csv", index=False)


