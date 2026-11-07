"""Test de bout en bout : la page Swagger de l'API déployée s'affiche dans Chrome.

L'URL cible se règle avec la variable d'environnement APP_URL
(par défaut http://localhost:8000, c'est-à-dire l'environnement de dev local / docker compose).
Exemple : APP_URL=http://mon-serveur-dev:8000 python -m pytest tests/test_selenium.py
"""
import os
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

APP_URL = os.getenv("APP_URL", "http://localhost:8000").rstrip("/")


def api_disponible():
    try:
        with urllib.request.urlopen(f"{APP_URL}/health", timeout=3) as r:
            return r.status == 200
    except OSError:
        return False


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")      # pas d'écran sur un serveur ou en CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()


@pytest.mark.skipif(not api_disponible(), reason=f"API injoignable sur {APP_URL}")
def test_swagger_accessible(driver):
    driver.get(f"{APP_URL}/docs")

    # Swagger UI est rendu en JavaScript : on attend le titre de l'API dans la page
    titre = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".info .title"))
    )

    assert "Churn Prediction API" in driver.title
    assert "Churn Prediction API" in titre.text
    # l'endpoint de prédiction est bien exposé
    assert driver.find_elements(By.ID, "operations-default-predict_predict_post")
