import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
import json
import sys

def trova_partite_squadra(nome_squadra):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']
    collection_squadre = db['squadre']
    squadre = list(collection_squadre.find({}))
    df_squadre = pd.DataFrame(squadre)
    id_to_name = dict(zip(df_squadre['wyId'], df_squadre['name']))
    
    if nome_squadra in id_to_name.values():
        id_squadra = df_squadre[df_squadre['name'] == nome_squadra]['wyId'].values[0]
    else:
        return []

    collection_partite = db['partite']
    partite = list(collection_partite.find({}))
    df_partite = pd.DataFrame(partite)

    if 'team1' in df_partite.columns and 'team2' in df_partite.columns and 'gameweek' in df_partite.columns and 'label' in df_partite.columns:
        df_partite['team1.teamId'] = df_partite['team1'].apply(lambda x: x['teamId'] if 'teamId' in x else None)
        df_partite['team2.teamId'] = df_partite['team2'].apply(lambda x: x['teamId'] if 'teamId' in x else None)
        
        partite_squadra = df_partite[(df_partite['team1.teamId'] == id_squadra) | (df_partite['team2.teamId'] == id_squadra)].copy()
        
        # Separare le squadre e il risultato dalla colonna 'label'
        partite_squadra[['squadre', 'risultato']] = partite_squadra['label'].str.split(', ', expand=True)
        
        # Ordina le partite in base al gameweek
        partite_squadra.sort_values(by='gameweek', inplace=True)
        
        # Converte ObjectId a string
        partite_squadra['_id'] = partite_squadra['_id'].apply(lambda x: str(x))
        
        return partite_squadra[['gameweek', 'squadre', 'risultato', 'wyId']].to_dict(orient='records')
    else:
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        nome_squadra = sys.argv[1]
    else:
        print("No team name provided")
        sys.exit(1)

    partite = trova_partite_squadra(nome_squadra)
    print(json.dumps(partite))
