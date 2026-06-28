# --- ÉTAPE 1 : Le Builder (Compilation des dépendances) ---
FROM python:3.11-alpine AS builder

WORKDIR /build

# Installer uniquement ce qui est nécessaire pour compiler psycopg2
RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY requirements.txt .
# Installer les dépendances dans un dossier temporaire isolé
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- ÉTAPE 2 : L'Image Finale (Ultra-légère et sécurisée) ---
FROM python:3.11-alpine

WORKDIR /app

# Installer uniquement la bibliothèque d'exécution PostgreSQL (pas les outils de dev)
RUN apk add --no-cache libpq

# Récupérer les dépendances proprement compilées du Builder
COPY --from=builder /install /usr/local
COPY app.py .

# Créer l'utilisateur non-root et lui assigner le répertoire de l'application
RUN adduser -D flaskuser && chown -R flaskuser:flaskuser /app

USER flaskuser

EXPOSE 8000

CMD ["python", "app.py"]