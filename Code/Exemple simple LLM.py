from transformers import pipeline, set_seed

# Initialisation du pipeline de génération de texte (modèle LLM GPT-2 allégé)
generator = pipeline('text-generation', model='distilgpt2')

# On fixe la graine pour avoir des résultats reproductibles
set_seed(42)

# Prompt (entrée utilisateur simulée)
prompt = "Bonjour, quels sont les événements aujourd'hui ?"

# Génération de texte par le LLM
reponses = generator(prompt, max_length=50, num_return_sequences=1)

# Affichage de la réponse générée
print("Réponse générée par le LLM :")
print(reponses[0]['generated_text'])
