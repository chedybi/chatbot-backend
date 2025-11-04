# chatbot_story.py

import os
import random
from pymongo import MongoClient  # type: ignore
from dotenv import load_dotenv  # type: ignore
from datetime import datetime
from questions import get_bot_response  # fallback si besoin
from logic.programmes import get_editors_count_detailed
from recommendation import get_recommendations

# -------------------------
# Chargement variables d'environnement
# -------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# -------------------------
# Connexion MongoDB
# -------------------------
if MONGO_URI:
    client = MongoClient(MONGO_URI)
    db = client["chatbotEvent"]
    programmes = db.get_collection("programmes_foire_2023")
    programmes_enfant = db.get_collection("programmes_enfant_2023")
    editeurs = db.get_collection("editeurs_foire")
else:
    client = None
    db = None
    programmes = None
    programmes_enfant = None
    editeurs = None


# -------------------------
# Utilitaires
# -------------------------
def normalize_story(summary: str, details=None):
    """Uniformise la sortie en dict {summary, details}."""
    default_text = "Aucune information disponible pour cette question."

    if isinstance(summary, str):
        summary = summary.strip() if summary else default_text
    else:
        summary = str(summary) if summary else default_text

    if isinstance(details, str):
        details = details.strip()
    elif isinstance(details, list):
        pass
    elif details is None:
        details = summary
    else:
        details = str(details)

    return {"summary": summary, "details": details}


def anecdote_aleatoire(theme="general"):
    """Retourne une petite recommandation finale."""
    recommendations = {
        "general": [
            "Vous pouvez explorer d'autres journées du programme pour découvrir encore plus d'activités.",
            "N’hésitez pas à poser une question spécifique sur un auteur ou un atelier qui vous intéresse."
        ],
        "programmes": [
            "💡 Vous souhaitez en savoir plus ? Demandez la description détaillée d’une session pour découvrir son contenu.",
            "👉 Pour aller plus loin, vous pouvez poser une question sur les invités ou les thèmes abordés."
        ],
        "enfants": [
            "💡 Pour les plus jeunes, demandez la description complète des animations afin de mieux préparer votre visite.",
            "👉 Vous pouvez aussi explorer les activités enfants prévues les autres jours."
        ],
        "editeurs": [
            "💡 Vous pouvez demander la liste complète des maisons d’édition par pays.",
            "👉 Si vous cherchez un éditeur en particulier, indiquez son nom et je vous dirai où le trouver."
        ]
    }
    return random.choice(recommendations.get(theme, recommendations["general"]))


def _format_date(date_str: str) -> str:
    """Formate une date brute en version lisible (ex: 28 avril 2023)."""
    if not date_str or str(date_str).lower() in ["none", "null", ""]:
        return "le 28 Avril"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %B %Y")
    except Exception:
        return str(date_str)


def intro_narrative_programme(date=None, n_events=0, question=None):
    date_fmt = _format_date(date)
    if question and any(word in question.lower() for word in ["commence", "début"]):
        return (
            f"🚀 Bonjour cher visiteur, la foire débute officiellement le {date_fmt}, "
            f"avec {n_events} événement(s) au programme. Voici les détails du premier jour :"
        )
    return f"📅 Le programme du {date_fmt} propose {n_events} moment(s) fort(s)."


def intro_narrative_editors(n_editors: int = 0, question: str = None):
    """Retourne une intro narrative interactive spécifique aux éditeurs."""
    if question and any(word in question.lower() for word in ["éditeur", "editeur", "maison d'édition", "maison d’édition"]):
        return (
            f"📚 Cette année, plus de {n_editors} éditeurs de plusieurs pays participent à la foire. "
            "Voici quelques exemples :"
        )
    return f"📚 La foire accueille environ {n_editors} éditeurs de divers horizons."


def intro_narrative_editors_countries(n_editors_countries: int, question: str = "") -> str:
    """
    Génère une introduction narrative plus vivante pour la section ÉDITEURS.
    """
    intro = f"📚 Cette année, la Foire du Livre accueille environ {n_editors_countries} maisons d’édition venues du monde entier."
    
    anecdotes = [
        "🇹🇳 La Tunisie reste le cœur battant de la Foire, avec de nombreuses maisons locales célébrant la littérature arabe et francophone.",
        "🇪🇬 L’Égypte apporte une touche classique et historique, avec plusieurs éditeurs reconnus du monde arabe.",
        "🇸🇾 La Syrie, malgré les difficultés, continue d’enrichir l’événement par la profondeur de sa poésie et de ses essais.",
        "🇱🇧 Le Liban, célèbre pour sa vitalité culturelle, présente cette année encore des auteurs modernes très suivis.",
        "🇲🇦 Le Maroc, fidèle au rendez-vous, mêle tradition et modernité dans ses publications littéraires.",
    ]

    intro += "\n\n" + random.choice(anecdotes)
    return intro



def format_events(events: list, date: str = None, show_description: bool = True) -> str:
    """Formate les sessions en markdown structuré."""
    lines = []
    if date:
        lines.append(f"📅 **Programme du {_format_date(date)}**\n")

    for idx, ev in enumerate(events, start=1):
        titre = str(ev.get("titre") or ev.get("nom") or "Sans titre")
        heure = str(ev.get("duree") or ev.get("heure") or "Heure inconnue")
        directeur = str(ev.get("directeur") or "Sans directeur")
        salle = str(ev.get("salle") or "Salle inconnue")
        acces = str(ev.get("acces") or "Réservée aux invités")
        desc = str(ev.get("description") or "").strip()

        lines.append(f"### 🎤 Session {idx} : **{titre}**")
        lines.append(f"- 🕒 Horaire : {heure}")
        lines.append(f"- 👤 Directeur : {directeur}")
        lines.append(f"- 📍 Salle : {salle}")
        lines.append(f"- 🎟️ Accès : {acces}")
        if show_description and desc:
            lines.append(f"- 📝 Description : {desc}")
        lines.append("")

    return "\n".join(lines)


# -------------------------
# Storytelling principal
# -------------------------
def generer_storytelling(
    sessions=None,
    date="2023-04-28",
    response_type="detailed",
    question=None,
    include_children=False
):
    """
    Génère une réponse narrative (storytelling) à partir :
    - des données locales (dict retourné par get_programme_xx)
    - ou des données MongoDB (si connectées)
    - inclut des recommandations personnalisées selon la question
    """

    sessions_list = []

    # --- 1️⃣ Normalisation du format ---
    if isinstance(sessions, dict):
        if "details" in sessions and isinstance(sessions["details"], list):
            sessions_list = sessions["details"]
        elif "sessions" in sessions:
            sessions_list = sessions["sessions"]
        else:
            sessions_list = [sessions]
        date = sessions.get("date", date)

    elif isinstance(sessions, list):
        sessions_list = sessions

    elif db is not None and programmes is not None:
        query = {"date": date}
        sessions_list = list(programmes.find(query))
        if include_children and programmes_enfant:
            sessions_list += list(programmes_enfant.find(query))

    # --- 2️⃣ Validation ---
    sessions_list = [s for s in sessions_list if isinstance(s, dict)]
    n_events = len(sessions_list)

    if n_events == 0:
        # 🧩 Ajout fallback avec get_bot_response et get_recommendations
        fallback_text = get_bot_response(question) if question else ""
        rec_text = ""
        try:
            recs = get_recommendations(question or "")
            if recs:
                rec_text = "\n\n💡 Recommandation : " + ", ".join(recs)
        except Exception as e:
            rec_text = f"\n⚠️ (Erreur recommandation : {e})"

        return {
            "details": (
                f"❌ Aucun événement trouvé pour cette date.\n\n"
                f"{fallback_text}\n"
                f"{rec_text}\n\n"
                "Vous pouvez poser une autre question ou consulter le programme complet."
            )
        }

    # --- 3️⃣ Génération du storytelling ---
    intro = intro_narrative_programme(date, n_events, question)
    details = format_events(sessions_list, date=date, show_description=(response_type == "detailed"))

    # --- 4️⃣ Ajout dynamique de recommandations ---
    recommendation_text = ""
    try:
        recs = get_recommendations(question or "")
        if recs:
            recommendation_text = "\n\n💡 **Suggestions associées :**\n- " + "\n- ".join(recs)
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération des recommandations : {e}")

    # --- 5️⃣ Conclusion dynamique ---
    conclusion = anecdote_aleatoire("programmes")

    final_text = f"{intro}\n\n{details}\n\n{recommendation_text}\n\n{conclusion}"

    return normalize_story(intro, final_text)



# -------------------------
# Autres formats
# -------------------------
def format_editors(data: dict) -> str:
    """Formate la réponse sur les éditeurs."""
    lines = []

    summary = data.get("summary")
    if isinstance(summary, str):
        lines.append(summary.strip())
    else:
        lines.append(str(summary) if summary else "📚 Informations indisponibles.")

    details = data.get("details", [])
    if not isinstance(details, list):
        details = [details]

    for block in details:
        if not isinstance(block, dict):
            continue
        if "info" in block:
            info = block["info"]
            lines.append(f"\nℹ️ {info.strip() if isinstance(info, str) else str(info)}")

        if "exemples" in block and isinstance(block["exemples"], list):
            lines.append("\n**Exemples d’éditeurs présents :**")
            for ex in block["exemples"]:
                if not isinstance(ex, dict):
                    continue
                pays = str(ex.get("pays", "Inconnu"))
                editeur = str(ex.get("éditeur", "Sans nom"))
                stand = str(ex.get("stand", "?"))
                lines.append(f"- {pays} → {editeur} (Stand {stand})")

    return "\n".join(lines).strip()


def format_editors_countries(data):
    """Format chat-friendly pour la liste des pays d'origine des éditeurs."""
    summary = data.get("summary", "")
    details_list = [d.get("pays") for d in data.get("details", []) if "pays" in d]
    return {"summary": summary, "details": details_list}
