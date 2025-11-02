# --- Étape 1 : Image de base ---
FROM python:3.10-slim

# --- Étape 2 : Préparer le système ---
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : Définir le dossier de travail ---
WORKDIR /app

# --- Étape 4 : Copier uniquement les fichiers nécessaires ---
COPY Code/requirements.txt ./requirements.txt

# --- Étape 5 : Installer les dépendances ---
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 6 : Copier le reste du code ---
COPY Code/ .

# --- Étape 7 : Exposer le port 8080 ---
EXPOSE 8080

# --- Étape 8 : Lancer l’application Flask avec Gunicorn ---
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
