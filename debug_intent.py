# debug_intent.py
# Test rapide du modèle d'intents sur une liste de phrases

import joblib
import numpy as np
from tensorflow import keras
from tabulate import tabulate  # Pour un affichage clair en tableau

# ──────────────
# 1. Charger le modèle et objets
# ──────────────
try:
    model = keras.models.load_model("intents_model/model.keras")
    vectorizer = joblib.load("intents_model/vectorizer.joblib")
    label_encoder = joblib.load("intents_model/label_encoder.joblib")
except Exception as e:
    print("❌ Erreur lors du chargement des fichiers :", e)
    exit(1)

# ──────────────
# 2. Fonction pour prédire un intent
# ──────────────
def predict_intent(user_input: str):
    X = vectorizer.transform([user_input]).toarray().astype("float32")
    predictions = model.predict(X, verbose=0)
    predicted_index = int(np.argmax(predictions, axis=1)[0])
    predicted_intent = label_encoder.inverse_transform([predicted_index])[0]
    confidence = float(predictions[0][predicted_index])
    return predicted_intent, confidence

# ──────────────
# 3. Liste de phrases de test
# ──────────────
test_phrases = [
    "Bonjour",
    "Quand commence la foire ?",
    "Où se trouve le stand des enfants ?",
    "Donne-moi le programme détaillé du 28 Avril",
    "Quels sont les horaires d'ouverture ?",
    "Merci pour votre aide"
]

# ──────────────
# 4. Test et affichage
# ──────────────
results = []
for phrase in test_phrases:
    try:
        intent, confidence = predict_intent(phrase)
        results.append([phrase, intent, f"{confidence:.2f}"])
    except Exception as e:
        results.append([phrase, "❌ Erreur", str(e)])

print("\n💬 Résultats des prédictions d'intents :\n")
print(tabulate(results, headers=["Phrase", "Intent prédit", "Confiance"], tablefmt="fancy_grid"))
print("\n✅ Test terminé.\n")