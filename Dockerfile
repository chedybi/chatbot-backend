# --- Étape 1 : Image de base ---
FROM python:3.10-slim

# --- Étape 2 : Installer les dépendances système ---
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : Définir le dossier de travail ---
WORKDIR /app

# --- Étape 4 : Copier les fichiers de dépendances ---
COPY requirements.txt .

# --- Étape 5 : Installer les dépendances Python ---
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 6 : Copier le reste du code du projet ---
COPY Code/ ./Code

# --- Étape 7 : Exposer le port ---
EXPOSE 8080

# --- Étape 8 : Lancer l’application ---
# Note : le chemin du module Flask doit correspondre à ton app.py dans Code/
CMD ["gunicorn", "-b", "0.0.0.0:8080", "Code.app:app"]
