import nltk
nltk.data.path.append("C:/Users/Admin/AppData/Roaming/nltk_data")

# Forcer le téléchargement
nltk.download('punkt', force=True)
nltk.download('stopwords', force=True)
nltk.download('wordnet', force=True)

print("Téléchargement terminé avec succès.")
