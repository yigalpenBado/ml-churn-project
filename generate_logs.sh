#!/usr/bin/env bash
# Génère des logs de test pour Kibana : prédictions CHURN, NO_CHURN et erreurs.
#
# Utilisation :
#   ./generate_logs.sh                 # 10 CHURN, 10 NO_CHURN, 3 erreurs
#   ./generate_logs.sh 20 5            # 20 de chaque prédiction, 5 erreurs
#   API_URL=http://autre-hote:8000 ./generate_logs.sh

set -u

API_URL="${API_URL:-http://localhost:8000}"
NB_PREDICTIONS="${1:-10}"
NB_ERREURS="${2:-3}"

CHURN='{"age":35,"anciennete":5,"revenu":450000,"nb_reclamations":2,"montant_mensuel":25000,"retards_paiement":2}'
NO_CHURN='{"age":35,"anciennete":36,"revenu":450000,"nb_reclamations":0,"montant_mensuel":25000,"retards_paiement":0}'
# "inf" passe la validation Pydantic mais fait planter le modèle -> log ERROR
ERREUR='{"age":35,"anciennete":36,"revenu":"inf","nb_reclamations":0,"montant_mensuel":25000,"retards_paiement":0}'

# Envoie un payload à /predict et affiche le code HTTP reçu
envoyer() {
    local libelle="$1" payload="$2" code
    code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/predict" \
        -H "Content-Type: application/json" -d "$payload")
    echo "  $libelle -> HTTP $code"
}

# Vérifie que l'API répond avant de commencer
if ! curl -s -f -o /dev/null "$API_URL/health"; then
    echo "Erreur : l'API ne répond pas sur $API_URL (lancer 'docker compose up -d')."
    exit 1
fi

echo "Envoi de $NB_PREDICTIONS CHURN + $NB_PREDICTIONS NO_CHURN vers $API_URL ..."
for i in $(seq 1 "$NB_PREDICTIONS"); do
    envoyer "CHURN    " "$CHURN"
    envoyer "NO_CHURN " "$NO_CHURN"
done

echo "Envoi de $NB_ERREURS requêtes en erreur ..."
for i in $(seq 1 "$NB_ERREURS"); do
    envoyer "ERREUR   " "$ERREUR"
done

echo "Terminé. Rechercher dans Kibana : event : \"prediction\"  ou  level : \"ERROR\""
