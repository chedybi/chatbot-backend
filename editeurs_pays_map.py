from pymongo import MongoClient
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import difflib

# Connexion MongoDB
client = MongoClient("mongodb+srv://Chedy:QUhRSsmtyWnudlAn@cluster0.6ki4q4p.mongodb.net/?retryWrites=true&w=majority")
db = client["chatbotEvent"]
collection = db["editeurs_foire"]

# Liste mise à jour des pays valides
pays_valides = [
    "Tunisie", "Egypt", "Liban", "Iraq", "Iran", "Emirates Arabes Unis", "Syrie", "Kuwait", "Jordanie",
    "Soudan", "Irlande", "Royaume De Arabie Saoudite", "Algérie", "Palestine", "Mauritanie", "Maroc",
    "Yémen", "Russie", "Hongrie", "Amman", "Libye", "Sénégal", "Suède", "Qatar", "Turquie"
]

# Création de la carte
map = folium.Map(location=[34, 10], zoom_start=3)
geolocator = Nominatim(user_agent="editeurs_map")

def geocode(pays):
    try:
        loc = geolocator.geocode(pays)
        if loc:
            return (loc.latitude, loc.longitude)
    except GeocoderTimedOut:
        time.sleep(1)
        return geocode(pays)
    return None

# 🔍 Corriger les noms de pays incorrects
corrections = {}
pays_trouves = collection.distinct("pays")
for pays in pays_trouves:
    if pays not in pays_valides:
        match = difflib.get_close_matches(pays, pays_valides, n=1, cutoff=0.6)
        if match:
            corrections[pays] = match[0]
            collection.update_many({"pays": pays}, {"$set": {"pays": match[0]}})
        else:
            corrections[pays] = "Inconnu"

# 📍 Ajouter les pays sur la carte
for pays in pays_valides:
    coords = geocode(pays)
    if coords:
        folium.Marker(location=coords, popup=pays, icon=folium.Icon(color='blue')).add_to(map)

# 💾 Sauvegarde de la carte
map.save("editeurs_map.html")

# ✅ Résumé
print("✅ Carte générée et sauvegardée sous 'editeurs_map.html'")
if corrections:
    print("🔍 Corrections effectuées :")
    for k, v in corrections.items():
        print(f"  - {k} → {v}")
else:
    print("✅ Aucun nom de pays incorrect détecté.")
