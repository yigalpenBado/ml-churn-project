from fastapi.testclient import TestClient

from api.main import app
# Utilisation de TestClient pour tester l'API FastAPI
client = TestClient(app)

# test du context de l'application FastAPI
def test_root():

    response = client.get("/")

    assert response.status_code == 200

# test de l'endpoint /health
# retourne un code 200 et un status "UP" si l'API est en bonne santé
def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "UP"

#test de l'endpoint /model/info
# retourne un code 200 et un status "UP" si l'API est en bonne santé
def test_model_info():

    response = client.get("/model/info")

    assert response.status_code == 200

# test de l'endpoint /predict pour le post d'une prédiction
def test_prediction():
# Initialisation du payload avec des données de test pour un client
    payload = {
        "age": 35,
        "anciennete": 5,
        "revenu": 450000,
        "nb_reclamations": 2,
        "montant_mensuel": 25000,
        "retards_paiement": 2
    }
# appel de l'endpoint /predict avec le payload
    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert "model_version" in data