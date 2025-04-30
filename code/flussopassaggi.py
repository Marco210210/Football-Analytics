from pymongo import MongoClient
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch

def generate_pass_flow(game_id, team_id, team_name, output_file):
    print(f"Received arguments: game_id={game_id}, team_id={team_id}, team_name={team_name}, output_file={output_file}")
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']

    query = {'type_name': 'pass', 'game_id': game_id, 'result_name': 'success', 'team_id': team_id}
    print(f"Query: {query}")

    count = db['azioni'].count_documents(query)
    print(f"Number of passes retrieved: {count}")
    if count == 0:
        print("No pass data available.")
        return

    results = db['azioni'].find(query, {'start_x': 1, 'start_y': 1, 'end_x': 1, 'end_y': 1, '_id': 0})
    results_list = list(results)
    print(f"Results: {results_list}")

    df_pass = pd.DataFrame(results_list)
    print(f"DataFrame: {df_pass}")

    df_pass.rename(columns={'start_x': 'x', 'start_y': 'y', 'end_x': 'end_x', 'end_y': 'end_y'}, inplace=True)

    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, line_color='#c7d5cc', pitch_color='#22312b')
    bins = (6, 4)

    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('#22312b')
    bs_heatmap = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=bins)
    hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Blues')
    fm = pitch.flow(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y,
                    color='black', arrow_type='same', arrow_length=5, bins=bins, ax=ax)
    ax.set_title(f'{team_name} Pass Flow Map', fontsize=30, pad=-20)

    print(f"Saving figure to {output_file}")
    fig.savefig(output_file)
    plt.close(fig)
    print("File saved successfully")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python flussopassaggi.py <game_id> <team_id> <team_name> <output_file>")
        sys.exit(1)

    try:
        game_id = int(sys.argv[1])
        team_id = int(sys.argv[2])
        team_name = sys.argv[3]
        output_file = sys.argv[4]

        generate_pass_flow(game_id, team_id, team_name, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
