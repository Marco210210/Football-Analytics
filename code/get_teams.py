import pandas as pd
from pymongo import MongoClient
import json
import base64
from PIL import Image
import io
from collections import defaultdict

# Connettersi a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Soccer']
partite_collection = db.partite
squadre_collection = db.squadre

# Dizionario per mantenere le statistiche delle squadre
classifica = defaultdict(lambda: {
    "V": 0,
    "N": 0,
    "P": 0,
    "GF": 0,
    "GS": 0,
    "PTI": 0,
    "DR": 0,
    "scontri_diretti": defaultdict(lambda: {"PTI": 0, "DR": 0, "GF": 0, "GS": 0})
})

# Funzione per aggiornare la classifica e gli scontri diretti
def aggiorna_classifica(team1_id, team2_id, team1_goals, team2_goals, winner):
    if winner == team1_id:
        classifica[team1_id]["V"] += 1
        classifica[team1_id]["PTI"] += 3
        classifica[team2_id]["P"] += 1
    elif winner == team2_id:
        classifica[team2_id]["V"] += 1
        classifica[team2_id]["PTI"] += 3
        classifica[team1_id]["P"] += 1
    else:
        classifica[team1_id]["N"] += 1
        classifica[team1_id]["PTI"] += 1
        classifica[team2_id]["N"] += 1
        classifica[team2_id]["PTI"] += 1
    
    classifica[team1_id]["GF"] += team1_goals
    classifica[team1_id]["GS"] += team2_goals
    classifica[team2_id]["GF"] += team2_goals
    classifica[team2_id]["GS"] += team1_goals

    classifica[team1_id]["DR"] = classifica[team1_id]["GF"] - classifica[team1_id]["GS"]
    classifica[team2_id]["DR"] = classifica[team2_id]["GF"] - classifica[team2_id]["GS"]

    # Aggiorna gli scontri diretti
    classifica[team1_id]["scontri_diretti"][team2_id]["GF"] += team1_goals
    classifica[team1_id]["scontri_diretti"][team2_id]["GS"] += team2_goals
    classifica[team2_id]["scontri_diretti"][team1_id]["GF"] += team2_goals
    classifica[team2_id]["scontri_diretti"][team1_id]["GS"] += team1_goals

    classifica[team1_id]["scontri_diretti"][team2_id]["DR"] = (
        classifica[team1_id]["scontri_diretti"][team2_id]["GF"] - classifica[team1_id]["scontri_diretti"][team2_id]["GS"]
    )
    classifica[team2_id]["scontri_diretti"][team1_id]["DR"] = (
        classifica[team2_id]["scontri_diretti"][team1_id]["GF"] - classifica[team2_id]["scontri_diretti"][team1_id]["GS"]
    )

    if winner == team1_id:
        classifica[team1_id]["scontri_diretti"][team2_id]["PTI"] += 3
    elif winner == team2_id:
        classifica[team2_id]["scontri_diretti"][team1_id]["PTI"] += 3
    else:
        classifica[team1_id]["scontri_diretti"][team2_id]["PTI"] += 1
        classifica[team2_id]["scontri_diretti"][team1_id]["PTI"] += 1

# Recupero delle partite
partite = partite_collection.find()

for partita in partite:
    team1_id = partita['team1']['teamId']
    team2_id = partita['team2']['teamId']
    team1_goals = partita['team1']['score']
    team2_goals = partita['team2']['score']
    winner = partita['winner']
    
    aggiorna_classifica(team1_id, team2_id, team1_goals, team2_goals, winner)

# Recupero dei nomi delle squadre
squadre = squadre_collection.find()
squadre_dict = {squadra['wyId']: squadra for squadra in squadre}

# Funzione di ordinamento basata sui criteri della Serie A
def ordina_classifica(item):
    team_id, stats = item
    return (
        stats['PTI'],
        sum(d['PTI'] for d in stats['scontri_diretti'].values()),
        sum(d['DR'] for d in stats['scontri_diretti'].values()),
        stats['DR'],
        stats['GF']
    )

# Creazione della classifica ordinata
classifica_ordinata = sorted(classifica.items(), key=ordina_classifica, reverse=True)

# Funzione per convertire immagini binarie in formato PNG o JPG
def convert_image_to_base64(image_binary):
    image = Image.open(io.BytesIO(image_binary))
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")  # Puoi scegliere PNG o JPG
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Costruzione del risultato con i dati della classifica e i loghi
risultato = []
for posizione, (team_id, stats) in enumerate(classifica_ordinata, start=1):
    squadra = squadre_dict.get(team_id, {})
    logo_base64 = convert_image_to_base64(squadra['logo'])
    risultato.append({
        'position': posizione,
        'name': squadra.get('name', 'Sconosciuto'),
        'logo': logo_base64,
        'points': stats['PTI'],
        'wins': stats['V'],
        'draws': stats['N'],
        'losses': stats['P'],
        'goals_for': stats['GF'],
        'goals_against': stats['GS'],
        'goal_difference': stats['DR']
    })

# Converti il risultato in JSON
risultato_json = json.dumps(risultato)

# Stampa il risultato JSON
print(risultato_json)

# Chiusura della connessione
client.close()
