"""Handler de logging qui envoie les logs en JSON à Logstash (input tcp + codec json_lines)."""
import json
import logging
import logging.handlers
from datetime import datetime, timezone

# Attributs standards d'un LogRecord : tout le reste vient de `extra=...`
_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "taskName"}


class LogstashHandler(logging.handlers.SocketHandler):
    """Envoie chaque log sous forme d'une ligne JSON sur une connexion TCP.

    Si Logstash n'est pas joignable, le log est simplement ignoré
    (SocketHandler retente la connexion plus tard) : l'API continue de fonctionner.
    """

    def makePickle(self, record):
        document = {
            "@timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "ml-churn-api",
        }
        # Champs métier passés via extra={...} (prediction, model_version, response_time...)
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS:
                document[key] = value
        if record.exc_info:
            document["exception"] = logging.Formatter().formatException(record.exc_info)
        return (json.dumps(document, default=str) + "\n").encode("utf-8")
