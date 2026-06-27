# --- Étape 1 : Le Builder (Compilation et téléchargement des dépendances) ---
FROM python:3.11-alpine AS builder

WORKDIR /app

# Installer les dépendances système nécessaires à la compilation de certains paquets Python (comme psycopg2)
RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY requirements.txt .

# Installer les dépendances dans un dossier local pour pouvoir les copier facilement ensuite
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Étape 2 : L'image finale de Production (Légère et sécurisée) ---
FROM python:3.13-alpine

WORKDIR /app

# Installer uniquement la bibliothèque d'exécution postgresql (nécessaire pour la DB)
RUN apk add --no-cache libpq

# Recréer un utilisateur non-root pour la sécurité
RUN adduser -D flaskuser

# Copier les dépendances Python depuis l'étape "builder"
COPY --from=builder /root/.local /home/flaskuser/.local
COPY app.py .

# Modifier les permissions pour que notre utilisateur possède les fichiers de l'application
RUN chown -R flaskuser:flaskuser /app

# Basculer sur l'utilisateur non-root
USER flaskuser

# Mettre à jour la variable d'environnement PATH pour que Python trouve les paquets installés
ENV PATH=/home/flaskuser/.local/bin:$PATH

EXPOSE 8000

CMD ["python", "app.py"]