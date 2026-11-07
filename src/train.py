#%%
## Import des bibliothèques nécessaires
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

#%%
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
#%%
## Chargement du jeu de données
df = pd.read_csv("../data/raw/churn.csv")

#%% [markdown]
# Séparation des variables explicatives et de la variable cible
# On supprime la colonne "churn" du jeu de données pour obtenir les variables explicatives (X) 
# et on conserve la colonne "churn" comme variable cible (y)
#%%
X = df.drop("churn", axis=1)
y = df["churn"]

#%% [markdown]
# Séparation des données en ensembles d'entraînement et de test
# On utilise la fonction train_test_split de scikit-learn pour séparer les données en un 
# ensemble d'entraînement (80%) et un ensemble de test (20%). 
# On utilise l'argument stratify=y pour s'assurer que la répartition de la variable cible est 
# similaire dans les deux ensembles.   
#%%
## Séparation des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
#%% [markdown]
# Nous definissons un dictionnaire contenant les modèles à entraîner.
# Chaque modele est défini comme une instance de la classe correspondante de scikit-learn,
# avec les hyperparamètres souhaités.

#%%
## Normalisation des variables explicatives
models = {
    "logistic_regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000))
    ]),

    "decision_tree": DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    ),

    "random_forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )
}
#%%
results = {}
## Entraînement et évaluation des modèles
for name, model in models.items():

    print(f"\nEntraînement : {name}")
    # entrainement du modèle sur les données d'entraînement
    model.fit(X_train, y_train)
    # prédiction sur les données de test
    predictions = model.predict(X_test)

    results[name] = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions),
        "recall": recall_score(y_test, predictions),
        "f1": f1_score(y_test, predictions)
    }

    print(results[name])
#%%
# Sélection du Random Forest pour la suite du TP
model = models["random_forest"]

#%%
joblib.dump(model, "../models/model.pkl")
print("\nModèle sauvegardé dans models/model.pkl")
# %%
