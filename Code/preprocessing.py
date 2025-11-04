import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ✅ Importer le correcteur orthographique et grammatical
from text_corrector import corriger_texte

# Télécharger les ressources nécessaires de nltk (à exécuter une seule fois)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialisation
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('french'))

def pretraiter_texte(texte):
    """
    Fonction complète de prétraitement : correction + nettoyage.
    :param texte: str, texte brut
    :return: texte corrigé et nettoyé (liste de tokens)
    """
    # 0️⃣ Correction orthographique, accents, genre, etc.
    texte = corriger_texte(texte)
    
    # 1️⃣ Supprimer caractères spéciaux et chiffres
    texte = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', texte)
    
    # 2️⃣ Minuscules
    texte = texte.lower()
    
    # 3️⃣ Tokenisation
    tokens = word_tokenize(texte)
    
    # 4️⃣ Stopwords
    tokens = [mot for mot in tokens if mot not in stop_words]
    
    # 5️⃣ Lemmatisation
    tokens = [lemmatizer.lemmatize(mot) for mot in tokens]
    
    return tokens

# Test local
if __name__ == "__main__":
    phrase_test = "Elle a ecrit un text sans accents ni conjugaison correcte, il faut corriger."
    print("Avant traitement:", phrase_test)
    print("Après traitement:", pretraiter_texte(phrase_test))
