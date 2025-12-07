from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv
import locale

# 🌍 Locale française
try:
    locale.setlocale(locale.LC_TIME, 'French_France.1252')  # Windows
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux/Mac
    except locale.Error:
        print("⚠️ Locale française non disponible. Utilisation d'une conversion manuelle.")

# 🔁 Conversion manuelle des mois FR → EN
def convertir_date_fr_to_en(date_str):
    mois_fr_en = {
        "janvier": "January", "février": "February", "mars": "March",
        "avril": "April", "mai": "May", "juin": "June",
        "juillet": "July", "août": "August", "septembre": "September",
        "octobre": "October", "novembre": "November", "décembre": "December"
    }
    for fr, en in mois_fr_en.items():
        date_str = date_str.lower().replace(fr, en)
    return date_str

def parser_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d %B %Y")
    except ValueError:
        try:
            date_en = convertir_date_fr_to_en(date_str)
            return datetime.strptime(date_en.strip(), "%d %B %Y")
        except Exception as e:
            raise ValueError(f"Erreur lors de l’analyse des dates : {e}")

# 🔌 Connexion MongoDB
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["chatbotEvent"]
programmes_foire_2023 = db["programmes_foire_2023"]
programmes_enfant_2023 = db["programmes_enfant_2023"]

# =========================================
# --- Réponses BRÈVES
# =========================================
def get_programme_duration_global():
    dates_foire = programmes_foire_2023.distinct("date")
    dates_enfant = programmes_enfant_2023.distinct("date")
    all_dates = list(set(dates_foire + dates_enfant))
    if not all_dates:
        return "Aucune date trouvée dans les programmes."
    try:
        dates_dt = [parser_date(d) for d in all_dates]
        dates_dt.sort()
        debut = dates_dt[0].strftime("%d %B")
        fin = dates_dt[-1].strftime("%d %B")
        return f"📅 Le programme global se déroulera du {debut} au {fin}."
    except Exception as e:
        return str(e)

def get_programme_by_date_global(date_str):
    events_foire = list(programmes_foire_2023.find({"date": date_str}))
    events_enfant = list(programmes_enfant_2023.find({"date": date_str}))
    total_events = events_foire + events_enfant
    if not total_events:
        return f"Aucun événement trouvé pour le {date_str}."
    lines = []
    for e in total_events:
        titre = e.get("titre", "Sans titre")
        heure = e.get("heure", "Heure inconnue")
        salle = e.get("salle", "Lieu inconnu")
        public = "👶 Enfants" if e in events_enfant else "🧑‍🦰 Tous publics"
        lines.append(f"- {public} – {titre} — {heure} dans {salle}")
    return f"📅 Événements du {date_str} :\n" + "\n".join(lines)
def get_event_price_global(event_name=None):
    """
    Retourne le prix d'entrée pour un événement donné (version brève).
    Si aucun événement spécifique n'est fourni, on retourne le prix général.
    """
    # Ici on peut imaginer une structure de prix
    prix_generaux = {
        "adulte": "10 TND",
        "enfant": "5 TND",
        "etudiant": "7 TND",
    }

    if event_name:
        # Exemple simplifié : certains événements peuvent avoir des prix différents
        if "concert" in event_name.lower():
            return "Le prix du concert est de 20 TND."
        elif "atelier" in event_name.lower():
            return "Le prix de l'atelier est de 15 TND."
    
    # Par défaut → prix généraux
    return f"Les prix sont : Adulte {prix_generaux['adulte']}, Enfant {prix_generaux['enfant']}, Étudiant {prix_generaux['etudiant']}."


def get_programme_enfant_general_global():
    events = list(programmes_enfant_2023.find())
    if not events:
        return "Aucun événement pour enfants trouvé."
    titres = [e.get("titre", "Événement sans titre").strip() for e in events]
    return "🎠 Activités enfants prévues :\n- " + "\n- ".join(sorted(set(titres)))

def get_all_programme_combined_dates_global():
    dates_foire = programmes_foire_2023.distinct("date")
    dates_enfant = programmes_enfant_2023.distinct("date")
    all_dates = list(set(dates_foire + dates_enfant))
    if not all_dates:
        return "Aucune date trouvée dans les programmes."
    try:
        dates_dt = [parser_date(d) for d in all_dates]
        dates_dt.sort()
        dates_str = [d.strftime("%d %B %Y") for d in dates_dt]
        return "📅 Dates couvertes par les programmes :\n- " + "\n- ".join(dates_str)
    except Exception as e:
        return f"Erreur lors du tri des dates : {e}"

def get_foire_start_date_global():
    return "📅  le 28 Avril 2023."

def get_foire_end_date_global():
    return "📅  le 07 Mai 2023."

def get_programme_date_range():
    return "10 jours, commence le 28 Avril et termine le 07 Mai."

def get_event_locations_global():
    return ("Il y aura 4 stands différents pour accueillir les événements : "
            "Salles de Baghdad, Babel, Dejla & Forat et Convention du Ministère de la Culture.")

def get_event_hours_global():
    return "Chaque jour, les événements commencent à 9h du matin et se terminent à 18h."

def get_editors_count_global():
    return "Plus de 200 éditeurs tunisiens et étrangers seront présents."

# =========================================
# --- Réponses DÉTAILLÉES (LISTE STRUCTURÉE POUR FRONT-END)
# =========================================
def get_programme_by_date_detailed(date_str):
    brief = get_programme_by_date_global(date_str)
    events_foire = list(programmes_foire_2023.find({"date": date_str}))
    events_enfant = list(programmes_enfant_2023.find({"date": date_str}))
    total_events = events_foire + events_enfant
    if not total_events:
        return brief
    details = []
    for e in total_events:
        details.append({
            "date": date_str,
            "heure": e.get("heure", "Heure inconnue"),
            "titre": e.get("titre", "Sans titre"),
            "salle": e.get("salle", "Lieu inconnu"),
            "public": "👶 Enfants" if e in events_enfant else "🧑‍🦰 Tous publics"
        })
    return {"summary": brief, "details": details}

def get_programme_date_range_detailed():
    """Retourne résumé + liste complète des événements pour toutes les dates"""
    dates_foire = programmes_foire_2023.distinct("date")
    dates_enfant = programmes_enfant_2023.distinct("date")
    all_dates = sorted(list(set(dates_foire + dates_enfant)), key=lambda d: parser_date(d))
    
    if not all_dates:
        return {"summary": "Aucune date trouvée", "details": []}
    
    summary = f"{len(all_dates)} jours, commence le {all_dates[0]} et termine le {all_dates[-1]}"
    
    details = []
    for date in all_dates:
        events_foire = list(programmes_foire_2023.find({"date": date}))
        events_enfant = list(programmes_enfant_2023.find({"date": date}))
        total_events = events_foire + events_enfant
        
        day_events = []
        for e in total_events:
            day_events.append({
                "heure": e.get("heure"),
                "titre": e.get("titre"),
                "salle": e.get("salle"),
                "public": "👶 Enfants" if e in events_enfant else "🧑‍🦰 Tous publics"
            })
        details.append({"date": date, "events": day_events})
    
    return {"summary": summary, "details": details}


def get_all_programmes_detailed():
    """
    Retourne une version détaillée du programme complet avec toutes les informations.
    """
    dates_foire = programmes_foire_2023.distinct("date")
    dates_enfant = programmes_enfant_2023.distinct("date")
    all_dates = sorted(list(set(dates_foire + dates_enfant)), key=lambda d: parser_date(d))

    if not all_dates:
        return {"summary": "Aucun programme trouvé", "details": []}

    summary = f"📅 Programme complet sur {len(all_dates)} jours."

    details = []
    for date in all_dates:
        events_foire = list(programmes_foire_2023.find({"date": date}))
        events_enfant = list(programmes_enfant_2023.find({"date": date}))
        total_events = events_foire + events_enfant

        if not total_events:
            continue

        day_events = []
        for e in total_events:
            day_events.append({
                "date": date,
                "heure": e.get("heure", "Heure inconnue"),
                "titre": e.get("titre", "Sans titre"),
                "salle": e.get("salle", "Lieu inconnu"),
                "public": "👶 Enfants" if e in events_enfant else "🧑‍🦰 Tous publics"
            })
        details.append({"date": date, "events": day_events})

    return {"summary": summary, "details": details}




def get_programme_enfant_general_detailed():
    brief = get_programme_enfant_general_global()
    events = list(programmes_enfant_2023.find())
    if not events:
        return brief
    details = []
    for e in events:
        details.append({
            "date": e.get("date"),
            "heure": e.get("heure"),
            "titre": e.get("titre"),
            "salle": e.get("salle")
        })
    return {"summary": brief, "details": details}

def get_event_locations_detailed():
    return {
        "summary": get_event_locations_global(),
        "details": [
            {"lieu": "Salle Dejla et Forat"},
            {"lieu": "Salle Babel"},
            {"lieu": "Salle Baghdad"},
            {"lieu": "Convention du Ministère de la Culture"}
        ]
    }

def get_event_hours_detailed():
    brief = get_event_hours_global()
    return {
        "summary": brief,
        "details": [
            {"info": "Certaines activités spéciales peuvent se prolonger après 18h, notamment les cérémonies d’ouverture et de clôture."}
        ]
    }

def get_event_price_detailed(event_name=None):
    """
    Retourne une réponse détaillée concernant le prix d'entrée.
    """
    if event_name:
        if "concert" in event_name.lower():
            return ("Le tarif pour assister au concert est fixé à 20 TND par personne. "
                    "Il est recommandé d’acheter vos billets à l’avance car les places sont limitées.")
        elif "atelier" in event_name.lower():
            return ("La participation à l’atelier coûte 15 TND. "
                    "Ce tarif inclut le matériel de base fourni sur place.")
    
    # Réponse générale détaillée
    return ("Les tarifs d’entrée sont organisés en plusieurs catégories :\n"
            "- Adulte : 10 TND\n"
            "- Enfant : 5 TND\n"
            "- Étudiant : 7 TND\n"
            "Les billets peuvent être achetés directement à la Maison de la Foire ou via notre site officiel. "
            "Certains événements spéciaux peuvent avoir des tarifs différents (exemple : concerts ou ateliers).")

def get_editors_count_detailed():
    """
    Retourne un résumé global du nombre d'éditeurs,
    avec une liste d'exemples concrets.
    """
    brief = "📚 Plus de 200 éditeurs de plusieurs pays seront présents."

    exemples = [
        {"pays": "Jordanie", "éditeur": "Association de Conservation du Quran", "stand": 205},
        {"pays": "Tunisie", "éditeur": "Maison Khrif pour l'Édition", "stand": 400},
        {"pays": "Tunisie", "éditeur": "Sweeps", "stand": 401},
        {"pays": "Tunisie", "éditeur": "Douane Nationale des Mines", "stand": 402},
        {"pays": "Maroc", "éditeur": "StepPublishing", "stand": 403},
        {"pays": "Liban", "éditeur": "Maison des Nobles", "stand": 405},
        {"pays": "Liban", "éditeur": "Centre des Études de l'Union Arabe", "stand": 406},
        {"pays": "Syrie", "éditeur": "Maison Yesmina pour la Traduction, Édition et Distribution", "stand": 500},
        {"pays": "Égypte", "éditeur": "Société de la Créativité pour la Traduction et Distribution", "stand": 501},
        {"pays": "Yémen", "éditeur": "Bibliothèque de Khaled Ibn Walid", "stand": 503},
        {"pays": "Égypte", "éditeur": "Bibliothèque des Sciences Modernes", "stand": 504},
        {"pays": "Égypte", "éditeur": "Centre Ibsar pour l'Édition et Distribution", "stand": 506},
    ]

    details_list = [
        {"info": "Ils représenteront un large éventail d’ouvrages : littérature, sciences, jeunesse, et publications techniques."},
        {"exemples": exemples[:5]}  # on limite à 5 exemples pour la réponse détaillée
    ]

    return {
        "summary": brief,
        "details": details_list
    }


def get_event_duration_detailed():
    return {
        "summary": "⏱️ Durée moyenne des événements",
        "details": [
            {"info": "30 minutes pour les présentations rapides"},
            {"info": "1 heure pour les sessions classiques"},
            {"info": "2 heures pour les grandes cérémonies et hommages"}
        ]
    }

def get_editors_countries_of_origin():
    countries = [
        "Tunisie", "Égypte", "Liban", "Iraq", "Iran", "Émirats Arabes Unis", "Syrie",
        "Koweït", "Jordanie", "Soudan", "Irlande", "Royaume d’Arabie Saoudite", "Algérie",
        "Palestine", "Mauritanie", "Maroc", "Yémen", "Russie", "Hongrie", "Amman",
        "Libye", "Sénégal", "Suède"
    ]
    return {
        "summary": "🌍 Origine des éditeurs",
        "details": [{"pays": c} for c in countries]
    }

# --- Cas spécifique 28 avril
programme_28_avril = [
    {"titre": "Journée d'ouverture officielle de Maison de Foire", "heure": "11:00 - 13:00", "salle": "Théâtre de Shargiia", "Accés" : "Resevée pour les invités "},
    {"titre": "Cérémonie d'hommage et remise des prix", "heure": "17:00 - 18:30", "salle": "Maison de Sagesse - Carthage", "Accés" : "Resevée pour les invités "},
    {"titre": "Session pour commémorer les livres prestigieux", "heure": "14:00 - 16:00", "directeur" : "Hbib ben Salah ", "salle": "Salle de Congrès Culturelles", "Accés" : "Resevée pour les invités "},
    {"titre": "Session d’éloge à la mémoire de Bechir ben Salama", "heure": "15:00 - 16:30", "directeur" : "Mohammed el May", "salle": "Salle de Dejla et Forat", "Accés" : "Resevée pour les invités "},
]

def get_programme_28_avril():
    """
    Retourne un dict contenant :
    - la date de commencement
    - la liste complète des sessions pour le 28 avril
    """
    return {
        "date": "28 Avril 2023",
        "sessions": programme_28_avril
    }


programme_04_mai =[
    
 {"titre" : "Journée Culturelle Vénézuélienne ", "heure" :"11:00 à 13:00", "directeur" : "Ridha Kochtbane", "salle" : "Convention du Ministère de la Culture", "Accés" : "Ouvert au public "},
 {"titre" : "Interview avec Le Romancier Jalel Berjes (Jordanie) " , "heure" :"11:00 à 12:30", "directeur" : " Jamel Jlassi", "salle": " Salle de Babel", "Accés" : "Ouvert au public "},
 {"titre" : "Le Lien entre la Philosophie et la Démocratie", "heure" : "11:00 à 13:00", "directeur" : "Fathi Triki", "salle" : "Dejla et Forat", "Accés" : "Resevée pour les invités "},
 {"titre" : "Interview avec L'écrivaine Française Belinda Cannone", "heure" :"13:00 à 14:30", "directeur" : "Aymen Hssan", "salle" : "Salle de Babel", "Accés": "Ouvert au public "},   
 {"titre" : "La Poésie orienté vers L'enfance et Les attentes de L'enfant (en Partenariat avec Les Ministères des Famille , Femme , Enfance et Agé)", "heure" : "15:00 à 16:30", "directeur" : "Lotfi Ben Miled", "salle" : "Salle de Babel", "Accés": "Resevée pour les invités "},   
 {"titre" : "L'Ecriture et les Choques", "heure" : "15:00 à 16:30", "directeur" : "Mohammed Elhedi Jouili", "salle" : "Dejla et Forat", "Accés": "Resevée pour les invités "},  
 {"titre" : "Livres des Villes", "heure" : "14:00 à 16:00", "directeur" : "Hbib Ben Salha", "salle" : "Convention du Ministère de la Culture", "Accés": "Ouvert au public "},  
 {"titre" : "Les Communiqués d'Institution Supérieure pour la Musique (en partenariat avec L'institution)", "heure" : "", "directeur" : "L'Institution Supérieure pour la Musique", "salle" : "Convention du Ministère de la Culture", "Accés": "Ouvert au public "},  
 {"titre" : "Interview avec L'Ecrivain 'Awadh Shaher' (Invité Spéciale du Royaume Arabi Saoudite) sur son tout Noveau Œuvre 'Conte du Desert'", "heure" : "17:00 à 18:30", "directeur" : "Omar Hfayedh", "salle" : "Salle de Baghdad", "Accés": "Ouvert au public "},
 {"titre" : "Ecritures de La Bourterie", "heure" : "17:00 à 18:30", "directeur" : "Rajaa el Fariq", "salle" : "Dejla et Forat", "Accés": "Resevée pour les invités "}, 
]

def get_programme_04_mai():
    """
    Retourne un dict contenant :
    - la date de commencement
    - la liste complète des sessions pour le 04 mai
    """
    return {
        "date": "04 Mai 2023",
        "sessions": programme_04_mai
    }


programme_07_mai =[
    
 {"titre" : "Journée Culturelle Italienne", "heure" :"11:00 - 13:00", "directeur" : "Ridha Kochtbane", "salle" : "Salle de Convention de la Ministere de Culture", "Accés" : "Resevée pour les invités "},
 {"titre" : "Papiers de la Poésie Oublié (en partenariat avec la Laboratoire Intersignes)" , "heure" :"11:00 - 13:00", "directeur" : "Hind Soudani", "salle": "Salle de Dejla et Forat", "Accés" : "Resevée pour les invités "},
 {"titre" : "Les Chefs-d'œuvre  du Mannouba", "heure" : "13:00 à 15:00", "directeur" : "Ali Youmi", "salle" : "Salle de Baghdad", "Accés" : "Resevée pour les invités "},
 {"titre" : "Les aspects sérieux de L'écriture (en partenariat avec la Maison nationale des livres , Equipe de programme 'Les oreilles lisent') ", "heure" :"14:00 à 16:00", "directeur" : "Souhail Esshamil", "salle" : "Salle de Convention de la Minstere de Culture", "Accés": "Resevée pour les invités "},   
 {"titre" : "Lectures Poétiques ", "heure" : "15:30 à 17:00", "directeur" : "Bouraaoui Barouun", "salle" : "Salle de Baghdad", "Accés": "Resevée pour les invités "},   
]


def get_programme_07_mai():
    print("[DEBUG] ✅ Fonction get_programme_07_mai() appelée.")
    """
    Retourne un dict contenant :
    - la date de conclusion
    - la liste complète des sessions pour le 07 mai
    """
    return {
        "date": "07 mai 2023",
        "sessions": programme_07_mai
    }



# =========================================
# --- WRAPPER CHAT-FRIENDLY
# =========================================
def get_programme_chat_friendly(intent, response_type="brief", max_lines=10, max_chars=500):
    """
    Wrapper pour renvoyer un texte court et chat-friendly.
    - intent : l'intention détectée (ex: "get_programme_by_date::28 Avril 2023")
    - response_type : "brief" ou "detailed"
    - max_lines : nombre max de lignes à afficher
    - max_chars : nombre max de caractères
    """
    from logic.programmes import handle_fixed_intent

    result = handle_fixed_intent(intent, response_type=response_type)

    # Si c’est un dict avec "summary" + "details"
    if isinstance(result, dict):
        lines = [result.get("summary", "")]
        details = result.get("details", [])
        for d in details:
            if isinstance(d, dict):
                # Concatène toutes les valeurs textuelles
                line_parts = [str(v) for v in d.values()]
                line_text = " — ".join(line_parts)
                lines.append(line_text)
            else:
                lines.append(str(d))
    else:
        # Texte simple
        lines = result.split("\n")

    # Limiter le nombre de lignes
    lines = lines[:max_lines]

    # Joindre et limiter le nombre de caractères
    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + " …"

    return text



# =========================================
# Export public
# =========================================
__all__ = [
   "programmes_foire_2023", "programmes_enfant_2023", "get_programme_28_avril", "get_programme_07_mai",
   "get_programme_duration_global", "get_programme_by_date_global", "get_programme_enfant_general_global",
   "get_all_programme_combined_dates_global", "get_foire_end_date_global", "get_foire_start_date_global",
   "get_programme_date_range", "get_event_locations_global", "get_event_hours_global", "get_event_price_global",    "get_editors_count_global","get_event_locations_detailed", "get_event_hours_detailed", "get_programme_enfant_general_detailed", 
   "get_editors_count_detailed",  "get_event_duration_detailed", "get_event_hours_detailed", "get_event_locations_detailed", "get_programme_by_date_detailed",
   "get_event_price_detailed", "get_programme_date_range_detailed" ,"get_all_programmes_detailed",  "get_editors_countries_of_origin",
]
