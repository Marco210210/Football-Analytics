import sys
import json
from pymongo import MongoClient
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch, add_image, FontManager, Sbopen, Pitch

def get_action_data(game_id, player_id, db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    features = db['azioni']
    query = {'player_id': player_id, 'game_id': game_id}
    fields = {'start_x': 1, 'start_y': 1, '_id': 0}
    risultati = features.find(query, fields)
    df_actions = pd.DataFrame(list(risultati))
    if not df_actions.empty:
        df_actions.rename(columns={'start_x': 'x', 'start_y': 'y'}, inplace=True)
        df_actions['player_id'] = player_id
    return df_actions

def generate_player_heatmap(game_id, player_id, player_name, output_file):
    player_data = get_action_data(game_id, player_id)
    
    pitch = VerticalPitch(line_color='#000009', line_zorder=2)
    fig, ax = pitch.draw(figsize=(4.4, 6.4))
    fig.set_facecolor('#22312b')

    flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors", ['#e3aca7', '#c03a1d'], N=100)

    if not player_data.empty:
        kde = pitch.kdeplot(player_data.x, player_data.y, ax=ax, fill=True, levels=100, thresh=0, cut=5, cmap=flamingo_cmap, label='Player Heatmap')

    plt.savefig(output_file)
    

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python prova.py <game_id> <player_id> <player_name> <output_file>")
        sys.exit(1)

    game_id = int(sys.argv[1])
    player_id = int(sys.argv[2])
    player_name = sys.argv[3]
    output_file = sys.argv[4]

    generate_player_heatmap(game_id, player_id, player_name, output_file)
