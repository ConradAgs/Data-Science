# 22410562 SEDJRO CONRAD AGOSSOU 


##################################################### Section 1 : Imports de module ###########################################################
#                                                                                                                                             #
###############################################################################################################################################

import P01_utils as projet
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist





################################################## Section 2 : Définition de fonctions #######################################################
#                                                                                                                                            #
##############################################################################################################################################

#création d'un échantillon de taille n
def echantillon(n):
    return projet.lire_donnees(n)

# fonction dist qui prend en entrée deux vecteurs X_i et X_j et retourne leur distance euclidienne
def dist(X_i,X_j):
    if len(X_i) == len(X_j):
        return np.sqrt(sum((X_i - X_j)**2))
    else:
        print("Oups, les deux vecteurs n'ont pas la même longueur")

#Implémentez une fonction qui permette d’obtenir les indices des 𝑘 plus proches voisin d’un individu de test parmi le jeu d’entraînement.
def k_proches_voisin(individu, k, X_train):
    dist_avec_voisins = [dist(individu, X_train[i]) for i in range(X_train.shape[0])]
    return np.argsort(dist_avec_voisins)[:k]

#Implémentez une fonction qui, à partir d’une liste des classes des 𝑘‑plus proches voisins, calcule la classe la plus représentée dans la liste
def classe_dominante(liste_classe_voisins):
    nbr_F = liste_classe_voisins.count("F")
    nbr_H = liste_classe_voisins.count("H")
    if nbr_F > nbr_H:
        return "F"
    else:
        return "H"

#Implémentez une fonction k_plus_proches_voisins_liste qui prend en entrée un jeu de données d’entraînement, un jeu de données de test et un nombre 𝑘 et retourne la liste des
#                                    prédictions d’un modèle de 𝑘‑plus proches voisins pour ces données.
def k_plus_proches_voisins_liste(X_train, Y_train, X_test, k = 1):
    Y_predit = []
    for i in range(X_test.shape[0]):
        ind = k_proches_voisin(X_test[i], k, X_train)
        classe = [Y_train[i] for i in ind if i < len(Y_train)]
        Y_predit.append(classe_dominante(classe))
    return Y_predit



#Ré‑implémentation des 𝑘‑plus proches voisins en utilisant numpy

def k_plus_proches_voisins_numpy(X_train, Y_train, X_test, k=1):
    distances = cdist(X_test, X_train)
    voisins_indices = np.argsort(distances, axis=1)[:, :k]
    predictions = []
    for i in range(X_test.shape[0]):
        k_voisins_classes = Y_train[voisins_indices[i]]
        if np.sum(k_voisins_classes == "F") > k_voisins_classes.shape[0] /2 :
            predictions.append("F")
        else:
            predictions.append("H")
    return predictions



############################# Section 3 : Tests de fonctions définies et manipulations en mode "script" #######################################
#                                                                                                                                             #
###############################################################################################################################################

X_train, Y_train = echantillon(100)
X_test, Y_test = echantillon(15)

#projet.visualiser_donnees(X_train, Y_train, X_test)
print()

# test de la fonction qui retourne la distance euclidienne
A = np.array([1,2])
B = np.array([4, 6])
print("Distance euclidienne entre A= [1,2] et B= [4, 6] est: ", dist(A, B) ) 
print()

# test de la fonction qui retourne les indices des k plus proches voisins
indiv = [165, 65]
print("Indices des 5 plus proche voisins de indiv = [165, 65] : ", k_proches_voisin(indiv,5,X_train)) #Tout ce que je peux dire pour le moment c'est que la fonction marche
print()


#test de la fonction qui retourne la classe dominante
print('Classe dominante dans ["F", "F", "H","F", "F", "H","F", "F", "H"] est :', classe_dominante(["F", "F", "H","F", "F", "H","F", "F", "H"]) )
print()

#test de mon modèle de prédiction full code python
print("prédiction avec la fonction full python: ",k_plus_proches_voisins_liste(X_train, Y_train, X_test, 10))
print()


print("prédiction avec numpy: ",k_plus_proches_voisins_numpy(X_train, Y_train, X_test, 10))
print()

print("Y_test: ", Y_test) #En prenant les 20 plus proches voisins, mes prédictions sont exactes (enfin, presque)
print()