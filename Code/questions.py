import os
import unicodedata
import re
from dotenv import load_dotenv
from pymongo import MongoClient
from model_intents import predict_intent  # Détection d'intention
from text_corrector import corriger_texte  # Correction texte

from logic.programmes import (
    programmes_foire_2023,
    programmes_enfant_2023,
    get_programme_duration_global,
    get_programme_by_date_global,
    get_programme_enfant_general_global,
    get_all_programme_combined_dates_global,
    get_foire_end_date_global,
    get_foire_start_date_global,
    get_programme_date_range,
    get_event_locations_global,
    get_event_locations_detailed,
    get_event_hours_global,
    get_event_hours_detailed,
    get_editors_count_detailed,
    get_programme_by_date_detailed,
    get_programme_enfant_general_detailed,
    get_programme_28_avril,
    get_programme_07_mai,
    get_event_duration_detailed,
    get_editors_countries_of_origin,
    get_event_price_global,
    get_event_price_detailed,
    get_programme_date_range_detailed,
)

# ───────────────────────────────
# ✅ Uniformisation des réponses
# ───────────────────────────────
def normalize_response(summary: str, details: str = None):
    """Force un format {summary, details}."""
    return {
        "summary": (summary or "").strip(),
        "details": (details or summary or "").strip(),
    }

def ensure_normalized(resp):
    """Accepte dict déjà normalisé ou string brute → renvoie toujours {summary, details}."""
    if isinstance(resp, dict) and "summary" in resp and "details" in resp:
        return resp
    return normalize_response(resp if resp else "")

# ───────────────────────────────
# 🤖 Gestion des questions
# ───────────────────────────────
def handle_question(intent: str, entities: dict = None, mode: str = "summary"):
    try:
        entities = entities or {}
        detailed = mode.lower().startswith("d")

        def clean_text(text: str) -> str:
            """Évite les pipes ou formats condensés → transforme en liste lisible."""
            if not text:
                return ""
            if "|" in text:
                parts = [p.strip() for p in text.split("|") if p.strip()]
                return "\n- " + "\n- ".join(parts)
            return text.strip()

        def clean_response(resp):
            """Nettoie dict ou string brute."""
            if isinstance(resp, dict):
                return {
                    "summary": clean_text(resp.get("summary", "")),
                    "details": clean_text(resp.get("details", resp.get("summary", "")))
                }
            return {
                "summary": clean_text(resp),
                "details": clean_text(resp)
            }

        # --- Dates de la foire
        if intent in ["when", "when_detailed"]:
            start = get_foire_start_date_global()
            end = get_foire_end_date_global()
            if detailed:
                return clean_response({
                    "summary": f"La foire commence le {start} et se termine le {end}.",
                    "details": f"La Foire Internationale de Tunis débutera le {start} et prendra fin le {end}. "
                               "Ces dates couvrent l'ensemble des programmes pour enfants et adultes."
                })
            return clean_response({
                "summary": f"La foire commence le {start} et se termine le {end}.",
                "details": f"Période officielle : du {start} au {end}."
            })

        # --- Durée
        elif intent == "duration":
            return clean_response(get_programme_duration_global())
        elif intent == "duration_detailed":
            return clean_response(get_event_duration_detailed())

        # --- Programme par date
        elif intent in ["programme_by_date", "programme_by_date_detailed"]:
            date_str = entities.get("date")
            if intent == "programme_by_date_detailed":
                return clean_response(get_programme_by_date_detailed(date_str))
            return clean_response(get_programme_by_date_global(date_str))

        # --- Programme enfant
        elif intent == "programme_enfant":
            return clean_response(get_programme_enfant_general_global())
        elif intent == "programme_enfant_detailed":
            return clean_response(get_programme_enfant_general_detailed())

        # --- 28 Avril
        elif intent == "programme_28_avril":
            return clean_response(get_programme_28_avril())
                
        elif intent == "programme_07_mai":
            return clean_response(get_programme_07_mai())


        # --- Lieux
        elif intent == "locations":
            return clean_response(get_event_locations_global())
        elif intent == "locations_detailed":
            return clean_response(get_event_locations_detailed())

        # --- Horaires
        elif intent == "hours":
            return clean_response(get_event_hours_global())
        elif intent == "hours_detailed":
            return clean_response(get_event_hours_detailed())

        # --- Éditeurs
        elif intent in ["editors_count", "editors_count_detailed"]:
              from chatbot_story import format_editors, format_editors_countries  # Formattage réponses éditeur
              data = get_editors_count_detailed()
              return {
        "summary": data["summary"],
        "details": format_editors(data)  # ✅ propre et chat-friendly
                     }
        elif intent == "editors_countries":
             data = get_editors_countries_of_origin()
             return format_editors_countries(data)


        # --- Tarifs
        elif intent == "price":
            return clean_response(get_event_price_global())
        elif intent == "price_detailed":
            return clean_response(get_event_price_detailed())

        # --- Dates disponibles
        elif intent == "dates_range":
            return clean_response(get_programme_date_range())
        elif intent == "dates_range_detailed":
            return clean_response(get_programme_date_range_detailed())

        # --- Tous les programmes
        elif intent == "all_programmes":
            return clean_response(get_all_programme_combined_dates_global())

        # --- Fallback
        else:
            corrected = corriger_texte(entities.get("user_input", ""), mode="detailed" if detailed else "summary")
            return clean_response({
                "summary": "Je n’ai pas compris votre question.",
                "details": f"Suggestion après correction : {corrected}"
            })

    except Exception as e:
        return {
            "summary": "Une erreur est survenue.",
            "details": f"Erreur technique : {str(e)}"
        }

# ───────────────────────────────
# 🤖 Orchestrateur principal
# ───────────────────────────────
def get_bot_response(user_input: str, response_type: str = "detailed") -> dict:
    from chatbot_story import generer_storytelling  # import LOCAL pour éviter import circulaire

    # --- Détection intent
    intent, confidence = predict_intent(user_input)
    print(f"💡 [DEBUG] Intent détecté : {intent}, Confiance : {confidence:.2f}")

    if confidence < 0.10:
        intent = "unknown"

    mode = "detailed" if response_type in ["detailed", "detail", "full"] else "brief"
    user_lower = user_input.lower()

    # 🔥 Redirection manuelle → sécuriser "combien d’éditeurs"
    if "combien" in user_lower and "editeur" in user_lower:
        intent = "editors_count"
        confidence = 0.99

    try:
        storytelling_intents = [
            "all_programmes", "programme_by_date", "programme_enfant", "programme_28_avril",
            "programme_by_date_detailed", "programme_enfant_detailed", "editors_count_detailed"
        ]

        if intent in storytelling_intents or any(word in user_lower for word in ["commence", "début"]):
            date_entity = None
            months = [
                "janvier","février","mars","avril","mai","juin",
                "juillet","août","septembre","octobre","novembre","décembre"
            ]
            if any(month in user_lower for month in months):
                date_entity = user_input

            print("💡 Mot-clé storytelling détecté → génération storytelling")
            response = generer_storytelling(
                date=date_entity,
                question=user_input,
                response_type=mode
            )
        elif intent != "unknown":
            response = handle_question(intent, entities={"user_input": user_input}, mode=mode)
        else:
            corrected_text = corriger_texte(user_input, mode=mode)
            response = {
                "details": f"Je n’ai pas compris votre question.\nSuggestion après correction : {corrected_text}"
            }

    except Exception as e:
        response = {
            "details": f"Une erreur est survenue.\nErreur technique : {str(e)}"
        }

    return {"intent": intent, "confidence": confidence, "answer": response}
