import os
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
load_dotenv()

# --- Chargement du modèle d'embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Base de connaissance : programmes, ateliers, conférences, livres, FAQ
RECOMMENDATION_DB = [
    {
        "title": "Programme complet foire 2023",
        "type": "programme",
        "description": "La foire 2023 commence le 28 avril avec des conférences et ateliers pour tous les âges."
    },
    {
        "title": "Atelier enfants - Lecture interactive",
        "type": "atelier",
        "description": "Un atelier pour enfants où ils participent à des lectures interactives."
    },
    {
        "title": "Conférence auteur : Jean Dupont",
        "type": "conference",
        "description": "Rencontrez Jean Dupont pour parler de ses derniers romans sur l'environnement."
    },
    {
        "title": "Livre recommandé : Le Petit Prince",
        "type": "livre",
        "description": "Un classique pour tous les âges, traitant de l'amitié et de la découverte du monde."
    },
    {
        "title": "Livre recommandé : Harry Potter",
        "type": "livre",
        "description": "Une saga fantastique très appréciée des jeunes et adultes."
    },
    {
        "title": "Atelier adulte - Écriture créative",
        "type": "atelier",
        "description": "Atelier pour développer vos compétences en écriture et partager vos textes."
    },
    {
        "title": "Nombre d'éditeurs présents",
        "type": "faq",
        "description": "Plus de 300 éditeurs seront présents à la foire du livre 2023."
    },
    {
        "title": "Événements pour enfants",
        "type": "faq",
        "description": "Une dizaine d'événements et d'ateliers seront consacrés aux enfants durant la foire."
    },
    {
        "title": "Horaires des événements",
        "type": "faq",
        "description": "Les événements ont lieu chaque jour de 10h à 19h, avec certaines nocturnes jusqu'à 22h."
    },
    {
        "title": "Lieu de la foire",
        "type": "faq",
        "description": "La foire a lieu à la Maison de la Foire, Tunis."
    }
]

# --- Pré-calcul des embeddings (titre + description)
for item in RECOMMENDATION_DB:
    full_text = f"{item['title']} - {item['description']}"
    item["embedding"] = model.encode(full_text, convert_to_tensor=True)


def get_recommendations(user_question: str = "", intent_type: str = None, top_k: int = 3):
    """
    Renvoie les top_k recommandations les plus proches sémantiquement de la question.
    Si un intent_type est fourni, filtre la base correspondante (programme, faq, etc.)
    """
    if not user_question or len(user_question.strip()) < 3:
        return []  # ⚠️ Pas de question claire -> on ne recommande rien

    try:
        question_emb = model.encode(user_question, convert_to_tensor=True)
    except Exception as e:
        print(f"⚠️ Erreur embedding dans get_recommendations: {e}")
        return []

    scores = []
    for item in RECOMMENDATION_DB:
        # Si un intent est fourni, on ne garde que les éléments du même type
        if intent_type and item["type"] != intent_type:
            continue
        try:
            score = util.cos_sim(question_emb, item["embedding"]).item()
            scores.append((score, item))
        except Exception as e:
            print(f"⚠️ Erreur de similarité avec {item['title']}: {e}")
            continue

    if not scores:
        return []

    # Tri décroissant
    scores.sort(key=lambda x: x[0], reverse=True)

    # Prend uniquement les top_k avec un score minimum
    top_items = [(score, item) for score, item in scores[:top_k] if score > 0.25]

    if not top_items:
        return []

    # Formatage final lisible
    recommendations = [
        f"→ {item['title']} ({item['type']}) — pertinence {round(score, 2)}"
        for score, item in top_items
    ]

    return recommendations


# --- Exemple de test
if __name__ == "__main__":
    question = "Quels livres me recommandez-vous ?"
    recs = get_recommendations(question, intent_type="livre")
    print("\n🔍 Recommandations :")
    for r in recs:
        print(r)
