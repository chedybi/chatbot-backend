# mode_detector.py
"""
Détection du mode de question : 'brief' ou 'detailed'
Basé sur heuristiques simples + possibilité d'évolution en mini modèle.
"""

import re
import unicodedata

# --- Mots-clés et structures courantes ---
DETAILED_HINTS = [
    #FR
    "détail", "Détaille", "liste complète", "programme complet", "complet", "concrètes", "Elaborez", "en profondeur",
    "montre-moi", "affiche-moi", "tous les", "toutes les", "énumère", "décris", "Listez", "ne manquez aucun détail",
    "complet", "précises", "Donne-moi", "afficher tout", "tous les jours", "Explique-moi", "plan parfait", "toute la ",
    #EN
    "detail", "explain", "complete list", "complete program", "complete", "concrete", "elaborate", "in depth",
    "show me", "display me", "all", "all", "enumerate", "describe", "list", "don't miss any details",
    "complete", "precise", "give me", "display everything", "every day", "explain to me", "perfect plan", "all of it",
    #DE
"Detail", "erklären", "vollständige Liste", "vollständiges Programm", "vollständig", "konkret", "ausführlich", "tiefgründig",
"zeig es mir", "präsentiere es mir", "alles", "aufzählen", "beschreiben", "Liste", "keine Details auslassen",
"vollständig", "präzise", "gib es mir", "zeig alles", "täglich", "erkläre es mir", "perfekter Plan", "alles",
    #AR
"تفصيل"، "شرح"، "قائمة كاملة"، "برنامج كامل"، "كامل"، "ملموس"، "شرح"، "متعمق"،
"أرني"، "اعرض لي"، "الكل"، "الكل"، "عدد"، "وصف"، "سرد"، "لا تغفل أي تفاصيل"،
"كامل"، "دقيق"، "أعطني"، "اعرض كل شيء"، "يومياً"، "اشرح لي"، "خطة مثالية"، "كل شيء"،
    #JA
"詳細", "説明する", "完全なリスト", "完全なプログラム", "完全な, 具体的な", "精巧な", "詳細に"
"見せて", "表示して", "すべて", "すべて", "列挙する", "説明する"、"リストする", "細部まで見逃さないで" ,
"完全な", "正確な","私に知らせて", "すべてを表示する","毎日", "私に説明して" ,"完璧な計画"、"すべて",
    #ZH
"细节", "解释", "完整清单", "完整方案","完整","具体" ,"详细阐述", "深入地" ,

"展示给我", "给我看", "全部", "全部", "列举", "描述", "列出", "不要遗漏任何细节"、

"完整", "精确", "给我", "展示所有内容", "每天", "向我解释", "完美计划", "全部内容"    
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
