from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import time
from pathlib import Path

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Churn Prediction API",
    version="1.0.0"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.pkl"
model = joblib.load(MODEL_PATH)

# Ordre des colonnes utilisé à l'entraînement
FEATURES = [
    "age",
    "anciennete",
    "revenu",
    "nb_reclamations",
    "montant_mensuel",
    "retards_paiement",
]

# Initialisation de la classe ClientData pour la validation des données d'entrée
class ClientData(BaseModel):
    age: int
    anciennete: int
    revenu: float
    nb_reclamations: int
    montant_mensuel: float
    retards_paiement: int


@app.get("/")
def root():
    return {
        "application": "Churn Prediction API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "UP"
    }


@app.get("/model/info")
def model_info():
    return {
        "model": "Random Forest",
        "version": "1.0.0"
    }


@app.post("/predict")
def predict(data: ClientData):

    start = time.time()

    # DataFrame avec les mêmes noms de colonnes que lors de l'entraînement
    values = pd.DataFrame([data.model_dump()])[FEATURES]

    prediction = model.predict(values)[0]
    probability = model.predict_proba(values)[0][1]

    duration = time.time() - start

    print(
        f"prediction={prediction}, "
        f"probability={probability:.4f}, "
        f"duration={duration:.4f}s"
    )

    return {
        "prediction": "CHURN" if prediction == 1 else "NO_CHURN",
        "probability": round(float(probability), 4),
        "model_version": "1.0.0",
        "duration_ms": round(duration * 1000, 2)
    }

# Instrumentation for Prometheus monitoring
Instrumentator().instrument(app).expose(app)