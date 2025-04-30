import sys
import json
from pymongo import MongoClient

def get_match_details(game_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']
    collection_partite = db['partite']
    collection_squadre = db['squadre']
    collection_calendario = db['calendario']

    match = collection_partite.find_one({"wyId": int(game_id)})
    calendario = collection_calendario.find_one({"game_id": int(game_id)})
    if not match:
        return {}

    team1_id = match['team1']['teamId']
    team2_id = match['team2']['teamId']

    # Verifica se i campi homeTeamId e awayTeamId esistono
    home_team_id = calendario['home_team_id']
    away_team_id = calendario['away_team_id']

    team1 = collection_squadre.find_one({"wyId": team1_id})
    team2 = collection_squadre.find_one({"wyId": team2_id})
    home_team = collection_squadre.find_one({"wyId": home_team_id})
    away_team = collection_squadre.find_one({"wyId": away_team_id})

    if not team1 or not team2 or not home_team or not away_team:
        return {}

    match_details = {
        "team1Id": team1_id,
        "team2Id": team2_id,
        "team1Name": team1['name'],
        "team2Name": team2['name'],
        "homeTeamId": home_team_id,
        "awayTeamId": away_team_id,
        "homeTeamName": home_team['name'],
        "awayTeamName": away_team['name']
    }

    return match_details

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_match_details.py <game_id>")
        sys.exit(1)

    game_id = sys.argv[1]
    if not game_id.isdigit():
        print(f"Invalid game_id: {game_id}")
        sys.exit(1)

    details = get_match_details(game_id)
    print(json.dumps(details))
