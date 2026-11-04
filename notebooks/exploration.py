#%%
## Import des bibliothèques nécessaires
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
## Lecture du jeu de données généré
df = pd.read_csv("../data/raw/churn.csv")
## affichage des premières lignes du jeu de données
print(df.head())
 #%% 
 ## Affichage de la répartition du churn (ligne, colonne)
print("\nDimensions :")
print(df.shape)

#%%
## Verification du type de chaque colonne et de la présence de valeurs manquantes
print("\nTypes :")
print(df.dtypes)

#%% 
##VTraitement des valeurs manquantes
print("\nValeurs manquantes :")
## Nous constatons qu'il n'y a pas de valeurs manquantes dans le jeu de données
print(df.isnull().sum())

#%%
## Affichage des statistiques descriptives du jeu de données
print("\nStatistiques :")
print(df.describe())
## Nous constatons que les variables sont sur des échelles différentes, 
# ce qui peut poser problème pour certains algorithmes de machine learning.
#  Il sera donc nécessaire de normaliser ou standardiser les variables avant de les utiliser pour l'entraînement d'un modèle.

#%%
## Affichage de la répartition du churn
print("\nRépartition du churn :")
print(df["churn"].value_counts())
#%%
### Visualisation de la répartition du churn par un graphique à barres
sns.countplot(data=df, x="churn")
plt.title("Répartition des clients selon le churn")
plt.savefig("../data/churn_distribution.png")
plt.show()
#%%
## Visualisation des corrélations entre les variables du jeu de données
plt.figure(figsize=(10, 6))
sns.heatmap(df.corr(), annot=True)
plt.title("Corrélations")
plt.savefig("../data/correlation.png")
plt.show()
# %% [markdown]
# Nous ne constatons pas de corrélations très fortes entre les variables, 
# %%
