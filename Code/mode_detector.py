# mode_detector.py
"""
Détection du mode de question : 'brief' ou 'detailed'
Basé sur heuristiques simples + possibilité d'évolution en mini modèle.
"""

import re
import unicodedata

# --- Mots-clés et structures courantes ---
DETAILED_HINTS = [
    "détail", "Détaille", "liste complète", "programme complet", "complet", "concrètes", "Elaborez", "en profondeur",
    "montre-moi", "affiche-moi", "tous les", "toutes les", "énumère", "décris", "Listez", "ne manquez aucun détail",
    "complet", "précises", "Donne-moi", "afficher tout", "tous les jours", "Explique-moi", "plan parfait", "toute la "
]
BRIEF_HINTS = [
    "Brièvement", "résumé", "en bref", "juste une idée", "simplement", "A-peu-près", "Quelques", "pertintents", "un peu", 
    "jetter un coup d'oeil", "un aperçu", "Juste", "seulement",  "version courte", "sois concis", "Soyez bref", "seulement",
    "vite", "rapidement", "vite fait"
]

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')
    return text.strip()

def detect_mode(text: str) -> str:
    if not text:
        return "breve"

    t = normalize_text(text)

    for kw in DETAILED_HINTS:
        if kw in t:
            return "detaille"
    for kw in BRIEF_HINTS:
        if kw in t:
            return "breve"

    word_count = len(t.split())
    if word_count <= 6:
        return "breve"
    if word_count >= 12:
        return "detaille"

    # interrogatifs → souvent brève (factuelle)
    if re.search(r"\b(quand|où|combien|quel|quelle|est-ce que)\b", t):
        return "breve"

    return "detaille"