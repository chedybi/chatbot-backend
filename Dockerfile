# --- Étape 1 : Image de base ---
FROM python:3.10-slim

# --- Étape 2 : Préparer le système ---
# Installation des dépendances système nécessaires à pip, numpy, torch, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : Définir le dossier de travail ---
WORKDIR /app

# --- Étape 4 : Copier les fichiers ---
COPY . .

# --- Étape 5 : Mettre à jour pip et installer les dépendances Python ---
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 6 : Exposer le port 8080 ---
EXPOSE 8080

# --- Étape 7 : Lancer l’application ---
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
