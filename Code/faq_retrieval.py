"""
faq_retrieval.py
Module pour récupérer des réponses depuis la FAQ.
⚙️ 100 % local – ne dépend plus d’OpenAI ni de LangChain.
"""

import re
import unicodedata
from text_corrector import corriger_texte  # Corrige le texte selon le mode (brief/detailed)

# ──────────────
# 🌍 Base FAQ multilingue avec synonymes
# ──────────────
FAQ_DATABASE = {
    "horaires": ["horaires", "heures", "ouverture", "fermeture", "hours", "schedule", "opening", "closing"],
    "billets": ["billets", "ticket", "entrée", "pass", "tickets", "entry", "pass"],
    "lieu": ["lieu", "stand", "salle", "hall", "emplacement", "place", "location", "where"],
    "paiement": ["paiement", "payer", "carte", "paypal", "cash", "espèces", "payment", "credit card"],
}

FAQ_RESPONSES = {
    "horaires": {
        "fr": "⏰ La foire est ouverte tous les jours de 9h à 19h.",
        "en": "⏰ The fair is open daily from 9 AM to 7 PM.",
    },
    "billets": {
        "fr": "🎟️ Les billets peuvent être achetés en ligne ou à l’entrée de la foire.",
        "en": "🎟️ Tickets can be purchased online or at the entrance.",
    },
    "lieu": {
        "fr": "📍 L’événement se déroule au Parc des Expositions du Kram, à Tunis.",
        "en": "📍 The event takes place at the Kram Exhibition Center in Tunis.",
    },
    "paiement": {
        "fr": "💳 Les paiements sont acceptés par carte, PayPal ou en espèces.",
        "en": "💳 Payments are accepted by credit card, PayPal, or cash.",
    },
}

# ──────────────
# 🔧 Nettoyage du texte pour comparaison
# ──────────────
def nettoyer_texte(text: str) -> str:
    """Nettoie et normalise le texte pour la comparaison."""
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = re.sub(r"[?.!,:;]", "", text)
    return text.strip()

# ──────────────
# 🧩 Recherche FAQ
# ──────────────
def obtenir_response(user_question: str, lang: str = "fr") -> str | None:
    """Retourne la meilleure réponse FAQ correspondant à la question."""
    user_question = nettoyer_texte(user_question)
    lang = lang.lower().strip()

    for key, synonyms in FAQ_DATABASE.items():
        for syn in synonyms:
            if re.search(r"\b" + re.escape(syn) + r"\b", user_question):
                response_dict = FAQ_RESPONSES.get(key, {})
                return response_dict.get(lang, response_dict.get("fr", "Réponse indisponible."))
    return None

# ──────────────
# 🤖 Fallback local si aucune correspondance
# ──────────────
def generer_reponse_locale(question: str, lang: str = "fr", response_type: str = "brief") -> str:
    """Génère une réponse locale si la FAQ ne contient pas la question."""
    if lang == "en":
        if response_type == "brief":
            return "I'm not sure about that. Please ask about schedules, tickets, or locations."
        else:
            return (
                "I'm not entirely sure how to answer that. "
                "Try rephrasing your question about fair programs, exhibitors, or event details."
            )
    else:
        if response_type == "brief":
            return "Je ne suis pas sûr de bien comprendre. Parlez-moi des horaires, billets ou lieux."
        else:
            return (
                "Je ne suis pas certain de la réponse exacte. "
                "Essayez de reformuler votre question à propos des programmes, éditeurs ou stands."
            )

# ──────────────
# 🎯 Fonction principale à appeler depuis app.py
# ──────────────
def traiter_question(user_question: str, response_type: str = "brief", lang: str = "fr") -> str:
    """
    Traite la question FAQ :
      - 1️⃣ Cherche dans la base locale
      - 2️⃣ Si rien trouvé, utilise une réponse générique locale
      - 3️⃣ Corrige et reformate le texte
    """
    if not user_question or not isinstance(user_question, str):
        return "⚠️ Question vide ou invalide."

    cleaned_question = re.sub(r"\s+", " ", user_question.strip().lower())

    # Recherche directe
    response = obtenir_response(cleaned_question, lang=lang)

    # Fallback local
    if not response:
        response = generer_reponse_locale(user_question, lang=lang, response_type=response_type)

    # Correction finale
    response = corriger_texte(response, mode=response_type) or response

    return response
