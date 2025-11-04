import random
import difflib

# Stocke les questions déjà posées
last_questions = set()

# Réponses génériques
fallback_messages = [
    "Désolé, je n'ai pas compris votre question. Pouvez-vous la reformuler ?",
    "Je ne trouve aucune correspondance à votre demande. Essayez des mots comme ‘programme’, ‘horaire’, ‘enfants’ ou ‘invités’.",
    "Votre question semble hors du sujet de la foire. Je peux vous aider avec les horaires, les événements ou les stands.",
    "Désolé, aucune correspondance à votre question. Essayez d’être plus précis.",
]

# Dictionnaire de réponses contextuelles
faq_fallbacks = {
    "horaire": "Les horaires varient selon les jours. Consultez la section Programme pour plus de détails.",
    "lieu": "Les événements ont lieu dans plusieurs halls et salles de la Maison de la Foire.",
    "enfant": "Un espace dédié aux enfants propose diverses animations et spectacles.",
    "éditeur": "Une carte des éditeurs est disponible dans la section dédiée.",
    "livre": "Des auteurs tunisiens et étrangers y présentent leurs œuvres.",
    "invité": "De nombreux invités seront présents pour dédicacer leurs livres."
}

def fallback_response(user_input, previous_questions=None):
    question = user_input.lower()
    print("[🤷] Fallback activé pour :", user_input)

    # Recherche par mot-clé direct
    for mot_cle, reponse in faq_fallbacks.items():
        if mot_cle in question:
            return {"answer": reponse}

    # Recherche par similarité (tolérance si l’utilisateur écrit "enfants" au lieu de "enfant", etc.)
    for mot_cle in faq_fallbacks:
        ratio = difflib.SequenceMatcher(None, question, mot_cle).ratio()
        if ratio > 0.75:
            return {"answer": faq_fallbacks[mot_cle]}

    # Réponse aléatoire générique
    return {"answer": random.choice(fallback_messages)}
