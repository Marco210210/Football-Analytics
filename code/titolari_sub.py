from pymongo import MongoClient
import json
import sys
import re
from datetime import datetime

def get_players_and_subs(game_id, team_id, side, db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    partite = db['partite']
    giocatori = db['giocatori']

    match = partite.find_one({"wyId": game_id})

    if not match:
        return None

    player_ids = []
    player_in_ids = []
    sub_details = []

    team = match[side]

    if 'formation' in team and 'lineup' in team['formation']:
        lineup_str = team['formation']['lineup'].replace("'", '"')
        lineup_dict = json.loads(lineup_str)
        player_ids = [item['playerId'] for item in lineup_dict if isinstance(item, dict) and 'playerId' in item]

    if 'formation' in team and 'substitutions' in team['formation']:
        substitutions_str = team['formation']['substitutions'].replace("'", '"')
        substitutions_dict = json.loads(substitutions_str)
        player_in_ids = [item['playerIn'] for item in substitutions_dict if isinstance(item, dict) and 'playerIn' in item]
        sub_details = []
        for item in substitutions_dict:
            if isinstance(item, dict):
                player_in = giocatori.find_one({"wyId": item['playerIn']})
                player_out = giocatori.find_one({"wyId": item['playerOut']})
                if player_in and player_out:
                    sub_details.append({
                        "playerIn": item['playerIn'],
                        "playerOut": item['playerOut'],
                        "minute": item['minute'],
                        "playerInName": decode_unicode(player_in["shortName"]),
                        "playerOutName": decode_unicode(player_out["shortName"])
                    })

    player_names_roles = [
        (decode_unicode(giocatori.find_one({"wyId": player_id})["shortName"]),
         extract_role_code(giocatori.find_one({"wyId": player_id})["role"]))
        for player_id in player_ids if giocatori.find_one({"wyId": player_id})
    ]
    sub_names_roles = [
        (decode_unicode(giocatori.find_one({"wyId": player_in_id})["shortName"]),
         extract_role_code(giocatori.find_one({"wyId": player_in_id})["role"]))
        for player_in_id in player_in_ids if giocatori.find_one({"wyId": player_in_id})
    ]

    # Ordina i giocatori per ruolo
    player_names_roles = sorted(player_names_roles, key=lambda x: get_role_priority(x[1]))
    sub_names_roles = sorted(sub_names_roles, key=lambda x: get_role_priority(x[1]))

    return player_names_roles, player_ids, sub_names_roles, player_in_ids, sub_details
def extract_role_code(role_str):
    match = re.search(r"'code2': '(\w+)'", str(role_str))
    role_code = match.group(1) if match else "Unknown"
    return role_code_to_italian(role_code)

def role_code_to_italian(role_code):
    role_map = {
        "GK": "Portiere",
        "DF": "Difensore",
        "MD": "Centrocampista",
        "FW": "Attaccante"
    }
    return role_map.get(role_code, role_code)

def get_role_priority(role):
    priority_map = {
        "Portiere": 1,
        "Difensore": 2,
        "Centrocampista": 3,
        "Attaccante": 4
    }
    return priority_map.get(role, 99)

def decode_unicode(s):
    return s.encode('utf-8').decode('unicode-escape')

def print_players(game_id, team1_id, team2_id, db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    partite = db['partite']
    squadre = db['squadre']
    allenatori = db['allenatori']

    match = partite.find_one({"wyId": game_id})

    if not match:
        print(json.dumps({"error": "Match not found"}))
        return

    gameweek = match.get('gameweek', 'N/A')
    label = match.get('label', 'N/A')
    date_str = match.get('date', 'N/A')
    team1_coachId = match.get('team1', {}).get('coachId', 'N/A')
    team2_coachId = match.get('team2', {}).get('coachId', 'N/A')
    team1_score = match.get('team1', {}).get('score', 'N/A')
    team2_score = match.get('team2', {}).get('score', 'N/A')
    team1_scoreHT = match.get('team1', {}).get('scoreHT', 'N/A')
    team2_scoreHT = match.get('team2', {}).get('scoreHT', 'N/A')

    team1_side = match.get('team1', {}).get('side', 'N/A')
    team2_side = match.get('team2', {}).get('side', 'N/A')

    if team1_side == 'home':
        home_team = 'team1'
        away_team = 'team2'
    else:
        home_team = 'team2'
        away_team = 'team1'

    home_team_name = squadre.find_one({"wyId": match[home_team]['teamId']}, {"_id": 0, "name": 1})["name"]
    away_team_name = squadre.find_one({"wyId": match[away_team]['teamId']}, {"_id": 0, "name": 1})["name"]
    home_team_coach_name = decode_unicode(allenatori.find_one({"wyId": match[home_team]['coachId']}, {"_id": 0, "shortName": 1})["shortName"])
    away_team_coach_name = decode_unicode(allenatori.find_one({"wyId": match[away_team]['coachId']}, {"_id": 0, "shortName": 1})["shortName"])

    date_str = re.sub(r' GMT[+-]\d+', '', date_str)
    date = datetime.strptime(date_str, "%B %d, %Y at %I:%M:%S %p")
    formatted_date = date.strftime("%d/%m/%Y - %H:%M")

    home_team_players, home_team_player_ids, home_team_subs, home_team_sub_ids, home_team_sub_details = get_players_and_subs(game_id, match[home_team]['teamId'], home_team, db_name)
    away_team_players, away_team_player_ids, away_team_subs, away_team_sub_ids, away_team_sub_details = get_players_and_subs(game_id, match[away_team]['teamId'], away_team, db_name)

    result = {
        "gameId": game_id,
        "label": label,
        "gameweek": gameweek,
        "formatted_date": formatted_date,
        "home_team_name": home_team_name,
        "away_team_name": away_team_name,
        "home_team_coach_name": home_team_coach_name,
        "away_team_coach_name": away_team_coach_name,
        "team1_scoreHT": team1_scoreHT,
        "team2_scoreHT": team2_scoreHT,
        "team1_score": team1_score,
        "team2_score": team2_score,
        "homeTeamPlayers": home_team_players if home_team_players else [],
        "homeTeamPlayerIds": home_team_player_ids if home_team_player_ids else [],
        "homeTeamSubs": home_team_subs if home_team_subs else [],
        "homeTeamSubIds": home_team_sub_ids if home_team_sub_ids else [],
        "homeTeamSubDetails": home_team_sub_details if home_team_sub_details else [],
        "awayTeamPlayers": away_team_players if away_team_players else [],
        "awayTeamPlayerIds": away_team_player_ids if away_team_player_ids else [],
        "awayTeamSubs": away_team_subs if away_team_subs else [],
        "awayTeamSubIds": away_team_sub_ids if away_team_sub_ids else [],
        "awayTeamSubDetails": away_team_sub_details if away_team_sub_details else []
    }

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python titolari_sub.py <game_id> <team1_id> <team2_id>")
        sys.exit(1)

    game_id = int(sys.argv[1])
    team1_id = int(sys.argv[2])
    team2_id = int(sys.argv[3])

    print_players(game_id, team1_id, team2_id)
