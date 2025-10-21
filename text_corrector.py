import re

def corriger_texte(text: str, mode: str = "brief") -> str:
    """
    Corrige et restructure le texte généré par le chatbot.
    - Supprime les espaces superflus
    - Corrige les majuscules après un point
    - En mode 'detailed', structure en liste avec des tirets
    """

    if not text or not isinstance(text, str):
        return ""

    # Nettoyage de base
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()

    # Corriger les majuscules après un point
    text = re.sub(
        r"([.!?])\s+([a-z])",
        lambda m: m.group(1) + " " + m.group(2).upper(),
        text,
    )

    if mode == "brief":
        return text

    # Mode détaillé = transformer en liste
    lines = text.split("\n")
    structured_lines = []
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if not clean_line.startswith("-"):
            structured_lines.append(f"- {clean_line}")
        else:
            structured_lines.append(clean_line)

    return "\n".join(structured_lines)
