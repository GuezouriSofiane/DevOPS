import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

# Configuration des logs au format JSON
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "path": request.path if request else None,
            "method": request.method if request else None,
            "ip": request.remote_addr if request else None
        }
        return json.dumps(log_record)

# Appliquer le formateur JSON aux logs de Flask
log_handler = logging.StreamHandler()
log_handler.setFormatter(JsonFormatter())
app.logger.handlers = [log_handler]
app.logger.setLevel(logging.INFO)

# Supprimer les logs par défaut de Werkzeug pour éviter les doublons
logging.getLogger('werkzeug').disabled = True

@app.route('/health', methods=['GET'])
def health():
    app.logger.info("Health check endpoint called")
    return jsonify({"status": "ok"})

@app.route('/version', methods=['GET'])
def version():
    app.logger.info("Version endpoint called")
    return jsonify({"version": "1.0.0"})

@app.route('/db-check', methods=['GET'])
def db_check():
    try:
        
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "postgres")
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        app.logger.info("Database check successful")
        return jsonify({"database": "connected"})
    except Exception as e:
        app.logger.error(f"Database check failed: {str(e)}")
        return jsonify({"database": "disconnected", "error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    # Endpoint /metrics minimaliste pour Prometheus
    return "http_requests_total{endpoint=\"/health\"} 1\n", 200, {'Content-Type': 'text/plain; version=0.0.4'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)