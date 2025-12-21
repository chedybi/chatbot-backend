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
        "de": "⏰ Die Messe ist täglich von 9 bis 19 Uhr geöffnet.",
        "ar": "⏰ المعرض مفتوح يوميًا من الساعة 9 صباحًا حتى 7 مساءً.",
        "ja": "⏰ フェアは毎日9時から19時まで開催されています。",
        "zh": "⏰ 展会每天开放时间为上午9点至晚上7点。"
    },
    "billets": {
        "fr": "🎟️ Les billets peuvent être achetés en ligne ou à l’entrée de la foire.",
        "en": "🎟️ Tickets can be purchased online or at the entrance.",
        "de": "🎟️ Tickets können online oder am Eingang gekauft werden.",
        "ar": "🎟️ يمكن شراء التذاكر عبر الإنترنت أو عند مدخل المعرض.",
        "ja": "🎟️ チケットはオンラインまたは会場入口で購入できます。",
        "zh": "🎟️ 门票可在线购买或在入口处购买。"
    },
    "lieu": {
        "fr": "📍 L’événement se déroule au Parc des Expositions du Kram, à Tunis.",
        "en": "📍 The event takes place at the Kram Exhibition Center in Tunis.",
        "de": "📍 Das Event findet im Kram Exhibition Center in Tunis statt.",
        "ar": "📍 يُقام الحدث في مركز معارض الكرام في تونس.",
        "ja": "📍 イベントはトゥニスのクラム展示センターで開催されます。",
        "zh": "📍 活动在突尼斯的卡拉姆展览中心举行。"
    },
    "paiement": {
        "fr": "💳 Les paiements sont acceptés par carte, PayPal ou en espèces.",
        "en": "💳 Payments are accepted by credit card, PayPal, or cash.",
        "de": "💳 Zahlungen werden per Kreditkarte, PayPal oder bar akzeptiert.",
        "ar": "💳 يتم قبول المدفوعات بواسطة بطاقة الائتمان أو PayPal أو نقدًا.",
        "ja": "💳 支払いはクレジットカード、PayPal、または現金で受け付けています。",
        "zh": "💳 可通过信用卡、PayPal或现金支付。"
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
    FALLBACKS = {
        "fr": {
            "brief": "Je ne suis pas sûr de bien comprendre. Parlez-moi des horaires, billets ou lieux.",
            "detailed": (
                "Je ne suis pas certain de la réponse exacte. "
                "Essayez de reformuler votre question à propos des programmes, éditeurs ou stands."
            )
        },
        "en": {
            "brief": "I'm not sure I understand. Try asking about schedules, tickets, or locations.",
            "detailed": (
                "I'm not entirely sure how to answer that. "
                "Try rephrasing your question about programs, exhibitors, or event details."
            )
        },
        "de": {
            "brief": "Ich bin mir nicht sicher. Fragen Sie nach Zeiten, Tickets oder Orten.",
            "detailed": "Bitte formulieren Sie Ihre Frage zu Programmen, Ausstellern oder Veranstaltungen neu."
        },
        "ar": {
            "brief": "لست متأكدًا من الفهم. اسأل عن المواعيد أو التذاكر أو الموقع.",
            "detailed": "يرجى إعادة صياغة سؤالك حول البرامج أو العارضين أو الفعاليات."
        },
        "ja": {
            "brief": "よく分かりません。時間、チケット、場所について聞いてみてください。",
            "detailed": "プログラムや出展者、イベントについて質問を言い換えてみてください。"
        },
        "zh": {
            "brief": "我不太明白。可以询问时间、门票或地点。",
            "detailed": "请尝试重新表述有关活动、参展商或安排的问题。"
        }
    }

    lang_data = FALLBACKS.get(lang, FALLBACKS["fr"])
    return lang_data.get(response_type, lang_data["brief"])

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
