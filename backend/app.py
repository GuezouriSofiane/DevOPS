from flask import Flask, jsonify

import os #Lire les variables d'environnement
import psycopg2 #Permet à python de parler à PostgreSQL

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })

@app.route("/version")
def version():
    return jsonify({
        "version": "1.0.0"
    })

@app.route("/db-check")
def db_check():
    try:

        conn = psycopg2.connect(

            host=os.getenv("POSTGRES_HOST"),

            database=os.getenv("POSTGRES_DB"),

            user=os.getenv("POSTGRES_USER"),

            password=os.getenv("POSTGRES_PASSWORD")
        )

        conn.close()
        return jsonify({
            "database": "connected"
        })
    
    except Exception as e:

        return jsonify({
            "database": "failed",
            
            "error": str(e)
        }),500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)