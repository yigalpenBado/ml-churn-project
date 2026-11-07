# Guide d'installation : ml-churn-project

API de prédiction du churn (FastAPI + scikit-learn), conteneurisée avec Docker, avec logs centralisés (ELK) et monitoring (Prometheus + Grafana).

Ce guide permet d'installer le projet sur une machine neuve, de lancer l'API seule ou toute la stack, puis de vérifier que tout fonctionne.

## 1. Prérequis

| Outil | Version testée | Utilisé pour |
|---|---|---|
| Git | toute version récente | récupérer le projet |
| Python | 3.12 | lancer l'API, les tests et l'entraînement en local |
| Docker + Docker Compose v2 | Docker 29.9, Compose v5.7 | lancer la stack complète |
| Google Chrome | toute version récente | test Selenium uniquement |

Ressources : prévoir **4 Go de RAM libre** pour la stack complète (Elasticsearch, Logstash et Kibana sont gourmands).

Ports utilisés par la stack :

| Service | Port | URL |
|---|---|---|
| API FastAPI | 8000 | http://localhost:8000/docs |
| Logstash | 5000 | (réception des logs, pas d'interface) |
| Elasticsearch | 9200 | http://localhost:9200 |
| Kibana | 5601 | http://localhost:5601 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |

Ces ports doivent être libres avant le lancement.

## 2. Récupérer le projet

```bash
git clone https://github.com/yigalpenBado/ml-churn-project.git
cd ml-churn-project
```

Toutes les commandes suivantes se lancent depuis la racine du projet, sauf indication contraire.

## 3. Installer l'environnement Python

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Pour le test Selenium, installer aussi `selenium`. Il n'est pas dans `requirements.txt` :

```bash
pip install selenium
```

## 4. Données et modèle (optionnel)

Le dépôt contient déjà le jeu de données (`data/raw/churn.csv`) et le modèle entraîné (`models/model.pkl`). Cette étape sert uniquement à tout régénérer.

Générer le jeu de données (2 000 clients synthétiques), depuis la racine :

```bash
python src/generate_data.py
```

Entraîner les modèles. Le script utilise des chemins relatifs (`../data`, `../models`) : il faut le lancer depuis le dossier `src/`.

```bash
cd src
python train.py
cd ..
```

Attention : `train.py` écrase `models/model.pkl`.

Le notebook d'exploration `notebooks/exploration.py` est un script découpé en cellules `#%%`. Pour l'exécuter, ouvrir le fichier dans VS Code (extension Python) et cliquer sur « Run Cell ». Les graphiques sont enregistrés dans `data/`.

## 5. Lancer l'API seule (sans Docker)

```bash
uvicorn api.main:app --reload
```

Vérification, dans un second terminal :

```bash
curl http://localhost:8000/health
# {"status":"UP"}

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":35,"anciennete":36,"revenu":450000,"nb_reclamations":0,"montant_mensuel":25000,"retards_paiement":0}'
# {"prediction":"NO_CHURN","probability":0.24,...}
```

L'interface Swagger est disponible sur http://localhost:8000/docs.

Sans Docker, les logs restent dans la console : l'envoi vers Logstash n'est activé que si la variable `LOGSTASH_HOST` est définie.

## 6. Lancer les tests

Tests de l'API (4 tests, aucune dépendance externe) :

```bash
python -m pytest tests/test_api.py -v
```

Test Selenium : il ouvre `http://localhost:8000/docs` dans Chrome. L'API doit donc tourner (étape 5 ou 7).

```bash
python -m pytest tests/test_selenium.py -v
```

Problème connu : le test Selenium échoue actuellement. Il cherche « FastAPI » dans le titre de la page, alors que le titre réel est « Churn Prediction API - Swagger UI ».

## 7. Lancer la stack complète avec Docker

Sous Linux uniquement, à faire une fois par démarrage de la machine (exigence d'Elasticsearch) :

```bash
sudo sysctl -w vm.max_map_count=262144
```

Construire et démarrer les 6 services :

```bash
docker compose up -d --build
docker compose ps
```

Attendre qu'`elasticsearch` soit à l'état `healthy`, soit environ une minute. Logstash et Kibana démarrent ensuite automatiquement.

| Interface | URL | Identifiants |
|---|---|---|
| API (Swagger) | http://localhost:8000/docs | aucun |
| Kibana | http://localhost:5601 | aucun (sécurité désactivée) |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | aucun |

## 8. Générer du trafic de test

```bash
./generate_logs.sh          # 10 CHURN, 10 NO_CHURN, 3 erreurs
./generate_logs.sh 20 5     # 20 de chaque prédiction, 5 erreurs
```

Le script vérifie d'abord que l'API répond, puis affiche le code HTTP de chaque requête : 200 pour les prédictions, 500 pour les erreurs volontaires.

## 9. Vérifier l'observabilité

Prometheus : ouvrir http://localhost:9090/targets. La cible `ml-churn-api` doit être à l'état `UP`.

Grafana : menu Dashboards, dossier ML Churn, dashboard « ML Churn API - Monitoring ». Les valeurs apparaissent 10 à 15 secondes après l'envoi de trafic.

Kibana :

1. Menu Stack Management, puis Data Views, puis Create data view.
2. Nom : `ml-churn-logs-*`. Champ de temps : `@timestamp`.
3. Dans Discover, essayer les recherches `event : "prediction"`, `level : "ERROR"` ou `response_time > 50`.

## 10. Arrêter la stack

```bash
docker compose down
```

Les données d'Elasticsearch et de Grafana sont conservées dans des volumes Docker. Pour tout supprimer, y compris ces données :

```bash
docker compose down -v
```

## 11. Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `port is already allocated` au démarrage | un autre programme ou conteneur utilise le port | `docker ps` pour trouver le conteneur, l'arrêter, puis relancer |
| Elasticsearch redémarre en boucle | `vm.max_map_count` trop bas ou RAM insuffisante | lancer la commande `sysctl` de l'étape 7, libérer de la mémoire |
| Kibana n'affiche aucun log | data view absente ou période trop courte | créer la data view `ml-churn-logs-*`, élargir la période en haut à droite |
| Grafana affiche « No data » | trafic trop récent ou période inadaptée | attendre 15 secondes après `generate_logs.sh`, vérifier la période |
| Aucune erreur visible dans Kibana | les données invalides sont rejetées (422) avant le modèle | utiliser `./generate_logs.sh`, qui envoie des requêtes en erreur 500 |
| `ModuleNotFoundError: selenium` | `selenium` absent de `requirements.txt` | `pip install selenium` |
| Le test Selenium échoue sur le titre | problème connu (voir étape 6) | corriger l'assertion dans `tests/test_selenium.py` |
