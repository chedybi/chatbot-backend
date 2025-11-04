"""
audio_handler.py — version finale et stable
Gère : audio → texte (Whisper) et texte → audio (gTTS)
Compatible Flask, multilingue et avec amplification du volume.
"""

import base64
import os
import io
import tempfile
import re
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import whisper

# ---------------------------------------------------------------------
# Langues disponibles
LANG_MAP = {
    "fr": {"speech": "fr-FR", "tts": "fr"},
    "ar": {"speech": "ar-SA", "tts": "ar"},
    "en": {"speech": "en-US", "tts": "en"},
    "de": {"speech": "de-DE", "tts": "de"},
    "es": {"speech": "es-ES", "tts": "es"},
    "ja": {"speech": "ja-JP", "tts": "ja"},
}

# ---------------------------------------------------------------------
# Chargement du modèle Whisper une seule fois
try:
    model = whisper.load_model("small")
    print("✅ Modèle Whisper chargé avec succès.")
except Exception as e:
    print(f"⚠️ Impossible de charger Whisper : {e}")
    model = None


# ---------------------------------------------------------------------
def speech_to_text_from_base64(b64_audio: str, language="fr") -> str:
    """
    Convertit un audio encodé en base64 en texte via Whisper.
    Retourne une chaîne vide en cas d'erreur.
    """
    if not model:
        raise RuntimeError("Le modèle Whisper n’a pas été chargé.")

    try:
        audio_bytes = base64.b64decode(b64_audio)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = model.transcribe(tmp.name, language=language)
        os.remove(tmp.name)

        text = result.get("text", "").strip()
        if not text:
            print("⚠️ Aucun texte reconnu par Whisper.")
        else:
            print(f"🗣️ Transcription réussie : {text}")

        return text

    except Exception as e:
        print(f"⚠️ Erreur Whisper : {e}")
        return ""


# ---------------------------------------------------------------------
def _convert_time_to_text(match: re.Match) -> str:
    """
    Convertit une heure au format HH:MM en texte lisible pour la voix.
    Exemples :
        "15:00" → "quinze"
        "14:30" → "quatorze trente"
    """
    heures, minutes = match.group(1), match.group(2)

    heures_int = int(heures)
    minutes_int = int(minutes)

    heures_text = str(heures_int)  # Lecture numérique naturelle par gTTS

    if minutes_int == 0:
        return heures_text
    else:
        minutes_text = str(minutes_int).zfill(2)
        return f"{heures_text} {minutes_text}"


# ---------------------------------------------------------------------
def text_to_speech(text: str, language="fr") -> str | None:
    """
    Convertit un texte en audio (base64 MP3) avec nettoyage et amplification.
    - Corrige la lecture des heures (HH:MM)
    - Amplifie le volume (+5 dB)
    """
    if not text.strip():
        print("⚠️ Aucun texte à vocaliser.")
        return None

    try:
        # --- 🕒 Conversion des horaires avant nettoyage ---
        clean_text = re.sub(r"\b(\d{1,2}):(\d{2})\b", _convert_time_to_text, text)

        # --- 🧹 Nettoyage général sans supprimer les chiffres et les espaces utiles ---
        clean_text = (
            clean_text.replace('"', "")
                      .replace("'", "")
                      .replace("«", "")
                      .replace("»", "")
                      .replace(";", "")
                      .replace("...", ".")
        )

        # On ne supprime plus les ":" ici, ils sont déjà convertis avant
        clean_text = re.sub(r"[^\w\s,.!?]", "", clean_text)

        lang_code = LANG_MAP.get(language, LANG_MAP["fr"])["tts"]
        tts = gTTS(text=clean_text, lang=lang_code)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)

            # 🔊 Amplifie le volume (+5 dB)
            sound = AudioSegment.from_file(tmp.name, format="mp3")
            louder_sound = sound + 5
            louder_sound.export(tmp.name, format="mp3")

            with open(tmp.name, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")

        os.remove(tmp.name)
        print(f"🔊 TTS généré avec succès ({len(encoded)} caractères encodés)")
        return encoded

    except Exception as e:
        print(f"⚠️ Erreur TTS : {e}")
        return None
