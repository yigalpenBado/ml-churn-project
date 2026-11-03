# Dockerfile pour a prediction de churn avec FastAPI et Uvicorn
#recuperation de l'mage de base python 3.12 slim
FROM python:3.12-slim
# On se positione dans le repertoire /app
WORKDIR /app
# on copie le fichier des requirements pour installer les dependances
COPY requirements.txt .
# Installation des dependances
RUN pip install --no-cache-dir -r requirements.txt
# copie des fichier de la racine du projet dans le conteneur
COPY . .
# le port 8000 sera exposé à l'exterieur du conteneur
EXPOSE 8000
# Lanceent de l'application FastAPI avec Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
