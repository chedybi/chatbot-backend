# logic/guests.py

def get_guests_info(programmes_foire_2023, programmes_enfants_2023):
    invités = set()

    for collection in [programmes_foire_2023, programmes_enfants_2023]:
        for doc in collection.find({}, {"invites": 1}):
            invites = doc.get("invites")
            if isinstance(invites, list):
                invités.update(invites)
            elif isinstance(invites, str):
                invités.update([inv.strip() for inv in invites.split(",")])

    if not invités:
        return "Aucun invité n’a été trouvé dans le programme."

    return f"Les invités présents sont : {', '.join(sorted(invités))}"
