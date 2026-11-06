from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import logging
import os
import time
from pathlib import Path

from prometheus_fastapi_instrumentator import Instrumentator

from api.logstash_handler import LogstashHandler

MODEL_VERSION = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

# Envoi des logs vers Logstash uniquement si LOGSTASH_HOST est défini (cas Docker).
# En local et pendant les tests, les logs restent seulement dans la console.
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST")
if LOGSTASH_HOST:
    logger.addHandler(
        LogstashHandler(LOGSTASH_HOST, int(os.getenv("LOGSTASH_PORT", "5000")))
    )

app = FastAPI(
    title="Churn Prediction API",
    version=MODEL_VERSION
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.pkl"
model = joblib.load(MODEL_PATH)

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
        "version": MODEL_VERSION,
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
        "version": MODEL_VERSION
    }


@app.post("/predict")
def predict(data: ClientData):

    logger.info(
        "Prediction request: model_version=%s", MODEL_VERSION,
        extra={"event": "prediction_request", "model_version": MODEL_VERSION}
    )

    start = time.time()

    values = [[
        data.age,
        data.anciennete,
        data.revenu,
        data.nb_reclamations,
        data.montant_mensuel,
        data.retards_paiement
    ]]

    try:
        prediction = model.predict(values)[0]
        probability = model.predict_proba(values)[0][1]
    except Exception as e:
        logger.error(
            "Prediction error: %s", e,
            extra={
                "event": "prediction_error",
                "model_version": MODEL_VERSION,
                "error": str(e),
            }
        )
        raise HTTPException(status_code=500, detail="Prediction error")

    duration = time.time() - start
    label = "CHURN" if prediction == 1 else "NO_CHURN"
    response_time_ms = round(duration * 1000, 2)

    logger.info(
        "prediction=%s, probability=%.4f, duration=%.4fs",
        prediction, probability, duration,
        extra={
            "event": "prediction",
            "prediction": label,
            "probability": round(float(probability), 4),
            "model_version": MODEL_VERSION,
            "response_time": response_time_ms,
        }
    )

    return {
        "prediction": label,
        "probability": round(float(probability), 4),
        "model_version": MODEL_VERSION,
        "duration_ms": response_time_ms
    }

# Instrumentation for Prometheus monitoring
Instrumentator().instrument(app).expose(app)
