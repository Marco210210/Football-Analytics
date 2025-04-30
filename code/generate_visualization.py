import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
import sys

def read_data_from_mongodb(collection_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']
    collection = db[collection_name]
    data = pd.DataFrame(list(collection.find()))
    return data

def prepare_data(player_wyId):
    # Caricamento dei dati da MongoDB
    rank_data = read_data_from_mongodb('rankgiocatori')
    players_data = read_data_from_mongodb('giocatori')
    matches_data = read_data_from_mongodb('partite')
    
    print("Dati dei giocatori caricati:\n", players_data.head())
    print("Dati delle partite caricati:\n", matches_data.head())
    print("Dati dei rank caricati:\n", rank_data.head())
    
    # Verifica se il wyId del giocatore esiste nella tabella giocatori
    if player_wyId not in players_data['wyId'].values:
        print(f"Nessun giocatore trovato con wyId: {player_wyId}")
        return pd.DataFrame()
    
    # Pulizia e preparazione dei dati dei giocatori
    players_data_clean = players_data[['wyId', 'shortName']].rename(columns={'wyId': 'playerId'})
    print("Dati dei giocatori puliti:\n", players_data_clean.head())
    
    # Verifica se i playerId in rank_data sono corretti
    unique_player_ids = rank_data['playerId'].unique()
    print(f"Unique player IDs in rank_data: {unique_player_ids[:10]}")
    
    # Verifica se il player_wyId è presente nei playerId della tabella rankgiocatori
    if player_wyId not in unique_player_ids:
        print(f"Il player_wyId {player_wyId} non è presente nella colonna playerId della tabella rankgiocatori")
        return pd.DataFrame()
    
    # Unione dei dati dei giocatori con i dati dei rank
    combined_data = pd.merge(rank_data, players_data_clean, on='playerId', how='left')
    print("Dati combinati:\n", combined_data.head())
    
    # Verifica se ci sono dati combinati per il giocatore specificato
    if player_wyId not in combined_data['playerId'].values:
        print(f"Nessun dato combinato trovato per il giocatore con wyId: {player_wyId}")
        return pd.DataFrame()
    
    # Pulizia dei valori dei rank per essere sicuri che siano tra 0 e 1
    combined_data['playerankScore'] = combined_data['playerankScore'].clip(lower=0, upper=1)
    
    # Aggregazione dei dati per playerId e matchId, ordinando per matchId per avere una sequenza temporale
    rank_progression = combined_data.groupby(['playerId', 'shortName', 'matchId'])['playerankScore'].mean().reset_index()
    rank_progression.sort_values(by=['playerId', 'matchId'], inplace=True)
    print("Progressione rank:\n", rank_progression.head())
    
    # Unione con i dati delle partite per ottenere le etichette delle partite
    rank_progression = pd.merge(rank_progression, matches_data[['wyId', 'label']], left_on='matchId', right_on='wyId', how='left')
    rank_progression.rename(columns={'label': 'MatchLabel'}, inplace=True)
    print("Rank progressione con etichette delle partite:\n", rank_progression.head())
    
    # Filtra e aggrega i dati per il giocatore specificato
    player_data = rank_progression[rank_progression['playerId'] == player_wyId]
    print("Dati del giocatore specificato:\n", player_data.head())
    player_data = player_data.groupby(['MatchLabel', 'shortName']).mean().reset_index()
    print("Dati del giocatore specificato dopo la media:\n", player_data.head())
    
    if player_data.empty:
        print(f"Nessun dato disponibile per il giocatore con wyId: {player_wyId}")
        return pd.DataFrame()
    
    # Normalizza il punteggio del rank per trasformarlo in voti da 1 a 10
    min_score = player_data['playerankScore'].min()
    max_score = player_data['playerankScore'].max()
    player_data['rank'] = 1 + 9 * (player_data['playerankScore'] - min_score) / (max_score - min_score)

    return player_data

def plot_player_votes(player_data, output_file):
    if player_data.empty:
        print(f"Nessun dato disponibile per il giocatore")
        plt.figure(figsize=(10, 1))
        plt.text(0.5, 0.5, f'Statistiche Ranking non presenti per questo giocatore', horizontalalignment='center', verticalalignment='center', fontsize=20)
        plt.axis('off')
        plt.savefig(output_file)
        plt.close()
        return
    
    # Plot dei Rank per ciascuna partita
    plt.figure(figsize=(14, 8))
    plt.plot(player_data['MatchLabel'], player_data['rank'], marker='o', color='crimson')
    plt.xticks(rotation=90)
    plt.xlabel('Match')
    plt.ylabel('Rank')
    plt.title(f'Rank giocatore')
    plt.ylim(1, 10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Verifica che siano stati passati i giusti argomenti
if len(sys.argv) < 3:
    print("Usage: python generate_visualization.py <output_file> <player_wyId>")
    sys.exit(1)

output_file = sys.argv[1]
player_wyId = int(sys.argv[2])

# Preparazione dei dati
player_data = prepare_data(player_wyId)

# Generazione del grafico dei voti
plot_player_votes(player_data, output_file)
