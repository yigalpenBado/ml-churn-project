# Script de génération de données synthétiques pour le churn
'''
Nous générons un jeu de données synthétiques pour le churn lié à un operateur télécom, 
en utilisant des distributions aléatoires 
pour simuler les caractéristiques des clients et leur probabilité de churn. 
Le jeu de données contient les colonnes suivantes :
- age : âge du client
- anciennete : ancienneté du client en mois
- revenu : revenu annuel du client
- nb_reclamations : nombre de réclamations faites par le client
- montant_mensuel : montant mensuel payé par le client
- retards_paiement : nombre de retards de paiement du client
- churn : variable cible indiquant si le client a churné (1) ou non (0)
'''
import pandas as pd
import numpy as np
## Rien de parrticulier sur le choix du seed, juste pour avoir des résultats reproductibles
np.random.seed(42)
## Nombre d'échantillons à générer
n = 2000

age = np.random.randint(18, 70, n)
anciennete = np.random.randint(1, 120, n)
revenu = np.random.randint(150000, 1000000, n)
nb_reclamations = np.random.poisson(2, n)
montant_mensuel = np.random.randint(5000, 75000, n)
retards_paiement = np.random.poisson(1, n)

score = (
    0.04 * nb_reclamations
    + 0.08 * retards_paiement
    - 0.015 * anciennete
    + 0.00001 * montant_mensuel
)

probabilite = 1 / (1 + np.exp(-score))

churn = (np.random.random(n) < probabilite).astype(int)

df = pd.DataFrame({
    "age": age,
    "anciennete": anciennete,
    "revenu": revenu,
    "nb_reclamations": nb_reclamations,
    "montant_mensuel": montant_mensuel,
    "retards_paiement": retards_paiement,
    "churn": churn
})

df.to_csv("data/raw/churn.csv", index=False)

print(df.head())
print()
print(df["churn"].value_counts())
