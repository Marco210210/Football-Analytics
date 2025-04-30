import sys
import json
from pymongo import MongoClient
import re

# Connettersi al database MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Soccer']
squadre_collection = db['squadre']
giocatori_collection = db['giocatori']
minutaggio_collection = db['minutaggiogiocatori']
azioni_collection = db['azioni']

# Recuperare il nome della squadra dalla riga di comando
team_name = sys.argv[1]

# Dizionario di mappatura dei ruoli
role_mapping = {
    'GK': 'Portiere',
    'DF': 'Difensore',
    'MD': 'Centrocampista',
    'FW': 'Attaccante'
}

# Funzione per estrarre il codice del ruolo utilizzando regex
def extract_role_code(role_str):
    match = re.search(r"'code2': '(\w+)'", role_str)
    return match.group(1) if match else "Unknown"

# Definire l'ordine dei ruoli
role_priority = {'GK': 1, 'DF': 2, 'MD': 3, 'FW': 4}

# Trovare la squadra nel database
squadra = squadre_collection.find_one({'name': team_name})

if squadra:
    team_id = squadra['wyId']
    # Trovare i giocatori della squadra
    giocatori = giocatori_collection.find({'currentTeamId': team_id}, {'_id': 0, 'wyId': 1, 'shortName': 1, 'role': 1})
    giocatori_list = []

    for giocatore in giocatori:
        shortName = giocatore['shortName'].encode('utf-8').decode('unicode-escape')
        role_code = extract_role_code(str(giocatore['role']))
        role = role_mapping.get(role_code, role_code)
        player_id = giocatore['wyId']
        
        # Calcolare il totale dei minuti giocati
        total_minutes = minutaggio_collection.aggregate([
            {'$match': {'player_id': player_id}},
            {'$group': {'_id': '$player_id', 'totalMinutes': {'$sum': '$Min'}}}
        ])
        total_minutes = next(total_minutes, {'totalMinutes': 0})['totalMinutes']
        
        # Calcolare il totale dei gol segnati
        total_goals = azioni_collection.aggregate([
            {'$match': {'player_id': player_id, 'type_name': {'$in': ['shot', 'shot_freekick', 'shot_penalty']}, 'result_name': 'success'}},
            {'$group': {'_id': '$player_id', 'totalGoals': {'$sum': 1}}}
        ])
        total_goals = next(total_goals, {'totalGoals': 0})['totalGoals']
        
        # Aggiungere solo i giocatori con minuti giocati maggiori di 0
        if total_minutes > 0:
            giocatori_list.append((role_priority.get(role_code, 5), shortName, role, total_minutes, total_goals, player_id))

    # Ordinare i giocatori per ruolo e nome
    giocatori_list.sort()

    # Convertire la lista ordinata in JSON
    result = [
        {
            "name": name,
            "role": role,
            "minutes": minutes,
            "goals": goals,
            "wyId": player_id
        } for _, name, role, minutes, goals, player_id in giocatori_list
    ]
    print(json.dumps(result))
else:
    print(json.dumps([]))

# Chiudere la connessione al database
client.close()
