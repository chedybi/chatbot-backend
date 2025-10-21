"""
nlp_engine.py
-------------
Module pour la détection d'intentions utilisateur.
Combine regex rapides + fallback NLP (spaCy / Transformers / LLM).
"""

import re
import unicodedata
from text_corrector import corriger_texte
from faq_retrieval import traiter_question as faq_traiter


# ──────────────
# 🔧 Pré-traitement texte
# ──────────────
def nettoyer_texte(text: str) -> str:
    """
    Nettoie le texte : minuscule, suppression des accents et ponctuations.
    """
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = re.sub(r"[?.!,:;]", "", text)
    return text.strip()


# ──────────────
# 🎯 Détection d’intention (regex rapides)
# ──────────────
def detect_intent_regex(question: str) -> str:
    """
    Première passe de détection via regex.
    """
    q = nettoyer_texte(question)

    if re.search(r"(quand|quelle date).*(commence|debut).*(programme|foire)", q):
        return "manual_foire_start"
    if re.search(r"(quand|quelle date).*(termine|fin).*(programme|foire)", q):
        return "manual_foire_end"
    if re.search(r"(combien de jours|duree du programme|jusqu a quand|periode)", q):
        return "manual_duree_globale"
    if re.search(r"(horaire|quelle heure|heures douverture|heure.*commence|heure.*termine)", q):
        return "manual_horaires_evenements"
    if re.search(r"(ou.*lieu|stands|salle|endroit|lieux.*evenement)", q):
        return "manual_lieux_evenements"
    if re.search(r"(combien).*(editeurs|maisons d'edition|participants)", q):
        return "manual_nb_editeurs"

    # Date spécifique (ex: "le 2 mai 2023")
    match = re.search(r"\b(\d{1,2})\s*(avril|mai)(?:\s*2023)?\b", q)
    if match:
        jour, mois = match.groups()
        mois = mois.capitalize()
        return f"get_programme_by_date::{jour.zfill(2)} {mois} 2023"

    # Intentions générales
    if "toutes les dates" in q or "dates disponibles" in q:
        return "get_all_programme_combined_dates"
    if "programme enfant" in q or "programme pour les enfants" in q:
        return "get_programme_enfant_general"
    if "editeurs" in q or "maison d’edition" in q or "editeur" in q:
        return "get_publishers_info"
    if "invite" in q or "auteur" in q or "personnalite" in q:
        return "get_guests_info"
    if "stand" in q or "hall" in q or "lieu" in q or "salle" in q:
        return "get_location_info"

    return "not_found"


# ──────────────
# 🤖 NLP avancé (spaCy / Transformers / LLM)
# ──────────────
def detect_intent_nlp(question: str) -> str:
    """
    Détection d’intention avancée via NLP.
    - Peut être implémentée avec spaCy, HuggingFace, ou un appel API LLM.
    - Actuellement placeholder : retourne "not_found".
    """
    # ⚠️ À implémenter selon les besoins
    return "not_found"


# ──────────────
# 🧩 Orchestration complète
# ──────────────
def detect_intent_and_route(question: str) -> str:
    """
    Combine regex + NLP pour trouver l’intention.
    """
    intent = detect_intent_regex(question)
    if intent != "not_found":
        return intent

    # Sinon, tenter NLP avancé
    return detect_intent_nlp(question)


def traiter_question_utilisateur(question_utilisateur: str, questions_module, response_type="brief"):
    """
    Route la question utilisateur :
      1. Corrige le texte
      2. Détecte l’intention (regex + NLP)
      3. Envoie vers le bon handler (programmes, FAQ, fallback)
    """
    question_corrigee = corriger_texte(question_utilisateur)
    intent = detect_intent_and_route(question_corrigee)

    # Intent → storytelling programme
    if intent != "not_found":
        from logic.programmes import handle_fixed_intent
        return handle_fixed_intent(intent, response_type=response_type)

    # Sinon → FAQ
    faq_result = faq_traiter(question_utilisateur, response_type=response_type)
    if faq_result:
        return faq_result

    # Fallback
    return "❓ Je n’ai pas trouvé de réponse. Pouvez-vous préciser votre demande ?"
