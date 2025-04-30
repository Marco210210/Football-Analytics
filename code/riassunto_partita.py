import re
import sys
from pymongo import MongoClient
from datetime import datetime

# Controllare se il game_id è stato passato come argomento da riga di comando
if len(sys.argv) != 2:
    print("Usage: python script_name.py <game_id>")
    sys.exit(1)

# Leggere il game_id dalla riga di comando
game_id = int(sys.argv[1])

# Connettersi al database MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Soccer']
partite_collection = db['partite']
giocatori_collection = db['giocatori']
squadre_collection = db['squadre']
allenatori_collection = db['allenatori']

# Filtrare le partite per wyId
partita = partite_collection.find_one({'wyId': game_id})

# Estrarre le informazioni del sommario
gameweek = partita.get('gameweek', 'N/A')
label = partita.get('label', 'N/A')
date_str = partita.get('date', 'N/A')
team1_coachId = partita.get('team1', {}).get('coachId', 'N/A')
team2_coachId = partita.get('team2', {}).get('coachId', 'N/A')
team1_score = partita.get('team1', {}).get('score', 'N/A')
team2_score = partita.get('team2', {}).get('score', 'N/A')
team1_scoreHT = partita.get('team1', {}).get('scoreHT', 'N/A')
team2_scoreHT = partita.get('team2', {}).get('scoreHT', 'N/A')

# Rimuovere il fuso orario dalla stringa della data
date_str = re.sub(r' GMT[+-]\d+', '', date_str)

# Convertire la data in formato desiderato
date = datetime.strptime(date_str, "%B %d, %Y at %I:%M:%S %p")
formatted_date = date.strftime("%d/%m/%Y - %H:%M")

# Funzione per estrarre playerId utilizzando regex
def extract_player_ids(lineup_str):
    return re.findall(r"'playerId': (\d+)", lineup_str)

# Funzione per estrarre il codice del ruolo utilizzando regex
def extract_role_code(role_str):
    match = re.search(r"'code2': '(\w+)'", role_str)
    return match.group(1) if match else "Unknown"

# Estrai i playerId e i teamId da team1 e team2
team1_id = partita.get('team1', {}).get('teamId', None)
team2_id = partita.get('team2', {}).get('teamId', None)

lineup_team1_str = str(partita.get('team1', {}).get('formation', {}).get('lineup', []))
lineup_team2_str = str(partita.get('team2', {}).get('formation', {}).get('lineup', []))

player_ids_team1 = extract_player_ids(lineup_team1_str)
player_ids_team2 = extract_player_ids(lineup_team2_str)

# Convertire i player ID in liste di interi
player_ids_team1 = list(map(int, player_ids_team1))
player_ids_team2 = list(map(int, player_ids_team2))

# Ricerca dei nomi delle squadre nella collection "squadre" con i teamId ottenuti
team1_name = squadre_collection.find_one({'wyId': team1_id}, {'_id': 0, 'name': 1})['name']
team2_name = squadre_collection.find_one({'wyId': team2_id}, {'_id': 0, 'name': 1})['name']

# Ricerca dei nomi degli allenatori nella collection "allenatori" con i coachId ottenuti
team1_coach = allenatori_collection.find_one({'wyId': team1_coachId}, {'_id': 0, 'shortName': 1})
team2_coach = allenatori_collection.find_one({'wyId': team2_coachId}, {'_id': 0, 'shortName': 1})

team1_coach_name = team1_coach['shortName'].encode('utf-8').decode('unicode-escape') if team1_coach else 'Allenatore non registrato'
team2_coach_name = team2_coach['shortName'].encode('utf-8').decode('unicode-escape') if team2_coach else 'Allenatore non registrato'

# Funzione per estrarre substitutions utilizzando regex
def extract_substitutions(substitutions_str):
    substitutions = []
    matches = re.findall(r"{'playerIn': (\d+), 'playerOut': (\d+), 'minute': (\d+)}", substitutions_str)
    for match in matches:
        substitutions.append({
            'playerIn': int(match[0]),
            'playerOut': int(match[1]),
            'minute': int(match[2])
        })
    return substitutions

# Estrarre le sostituzioni per entrambe le squadre
substitutions_team1_str = str(partita.get('team1', {}).get('formation', {}).get('substitutions', []))
substitutions_team2_str = str(partita.get('team2', {}).get('formation', {}).get('substitutions', []))

substitutions_team1 = extract_substitutions(substitutions_team1_str)
substitutions_team2 = extract_substitutions(substitutions_team2_str)

# Ricerca dei giocatori nella collection "giocatori" con i playerId ottenuti
all_player_ids = set(player_ids_team1 + player_ids_team2 + 
                     [sub['playerIn'] for sub in substitutions_team1] + 
                     [sub['playerOut'] for sub in substitutions_team1] + 
                     [sub['playerIn'] for sub in substitutions_team2] + 
                     [sub['playerOut'] for sub in substitutions_team2])

giocatori = giocatori_collection.find(
    {'wyId': {'$in': list(all_player_ids)}},
    {'_id': 0, 'wyId': 1, 'shortName': 1, 'role': 1}
)

# Creare un dizionario di wyId a shortName e role
player_info = {giocatore['wyId']: (giocatore['shortName'].encode('utf-8').decode('unicode-escape'), extract_role_code(str(giocatore['role']))) for giocatore in giocatori}

# Configurare l'encoding per gestire correttamente i caratteri speciali
sys.stdout.reconfigure(encoding='utf-8')

# Definire l'ordine dei ruoli
role_priority = {'GK': 1, 'DF': 2, 'MD': 3, 'FW': 4}

# Funzione per stampare la formazione ordinata per ruolo e nome
def print_formation(team_name, player_ids, player_info):
    print(f"{team_name} titolari:")
    players = []
    unregistered = []
    for player_id in player_ids:
        if player_id in player_info:
            player_name = player_info[player_id][0]
            role = player_info[player_id][1]
            players.append((role_priority.get(role, 5), player_name, role))
        else:
            unregistered.append(f"ID: {player_id} (Giocatore non registrato nel database)")
    players.sort()
    for role_num, name, role in players:
        print(f"{name} ({role})")
    for unreg in unregistered:
        print(unreg)

# Funzione per stampare la panchina ordinata
def print_bench(team_name, bench_player_ids, bench_player_info):
    print(f"\n{team_name} panchinari:")
    bench_players = []
    unregistered = []
    for player_id in bench_player_ids:
        if player_id in bench_player_info:
            player_name = bench_player_info[player_id][0]
            role = bench_player_info[player_id][1]
            bench_players.append((role_priority.get(role, 5), player_name, role))
        else:
            unregistered.append(f"ID: {player_id} (Giocatore non registrato nel database)")
    bench_players.sort()
    for role_num, name, role in bench_players:
        print(f"{name} ({role})")
    for unreg in unregistered:
        print(unreg)

# Funzione per stampare i giocatori sostituiti
def print_substitutions(team_name, substitutions, player_info):
    print(f"\n{team_name} sostituzioni:")
    for sub in substitutions:
        player_in_name = player_info[sub['playerIn']][0] if sub['playerIn'] in player_info else f"ID: {sub['playerIn']} (Giocatore non registrato nel database)"
        player_out_name = player_info[sub['playerOut']][0] if sub['playerOut'] in player_info else f"ID: {sub['playerOut']} (Giocatore non registrato nel database)"
        print(f"In: {player_in_name}, Out: {player_out_name}, Minuto: {sub['minute']}")

# Stampare il sommario
print("Resoconto partita")
print(f"{label}")
print(f"{gameweek}° giornata")
print(f"{formatted_date}")
print(f"Allenatore {team1_name}: {team1_coach_name}")
print(f"Allenatore {team2_name}: {team2_coach_name}")
print(f"Risultato primo tempo: {team1_scoreHT}-{team2_scoreHT}")
print(f"Risultato finale: {team1_score}-{team2_score}\n")

# Stampare i risultati per team1 e team2
print_formation(team1_name, player_ids_team1, player_info)
print("")
print_formation(team2_name, player_ids_team2, player_info)

# Estrai i giocatori dalla panchina di team1
bench_team1_str = str(partita.get('team1', {}).get('formation', {}).get('bench', []))
bench_player_ids_team1 = extract_player_ids(bench_team1_str)
bench_player_ids_team1 = list(map(int, bench_player_ids_team1))

# Estrai i giocatori dalla panchina di team2
bench_team2_str = str(partita.get('team2', {}).get('formation', {}).get('bench', []))
bench_player_ids_team2 = extract_player_ids(bench_team2_str)
bench_player_ids_team2 = list(map(int, bench_player_ids_team2))

# Ricerca dei giocatori titolari nella collection "giocatori" con i playerId ottenuti dalla panchina
all_bench_player_ids = set(bench_player_ids_team1 + bench_player_ids_team2)
bench_giocatori = giocatori_collection.find(
    {'wyId': {'$in': list(all_bench_player_ids)}},
    {'_id': 0, 'wyId': 1, 'shortName': 1, 'role': 1}
)

# Creare un dizionario di wyId a shortName e role per i giocatori della panchina
bench_player_info = {giocatore['wyId']: (giocatore['shortName'].encode('utf-8').decode('unicode-escape'), extract_role_code(str(giocatore['role']))) for giocatore in bench_giocatori}

# Stampare i risultati della panchina per team1 e team2
print_bench(team1_name, bench_player_ids_team1, bench_player_info)
print_bench(team2_name, bench_player_ids_team2, bench_player_info)

# Stampare i risultati delle sostituzioni per team1 e team2
print_substitutions(team1_name, substitutions_team1, player_info)
print_substitutions(team2_name, substitutions_team2, player_info)

# Stampare la nota esplicativa
print("\nNota: I giocatori con solo l'ID non sono presenti perché non hanno mai giocato.")
