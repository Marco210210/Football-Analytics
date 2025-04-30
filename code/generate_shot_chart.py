import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
import sys
import os

def get_action_data(type_name, game_id, team_id, db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    features = db['azioni']
    query = {'type_name': type_name, 'game_id': int(game_id), 'team_id': team_id}
    fields = {'start_x': 1, 'start_y': 1, '_id': 0}
    risultati = features.find(query, fields)
    df_shot = pd.DataFrame(list(risultati))
    print(f"Query: {query}")
    print(f"Number of shots retrieved: {len(df_shot)}")
    print(f"Retrieved DataFrame:\n{df_shot}")
    df_shot.rename(columns={'start_x': 'x', 'start_y': 'y'}, inplace=True)
    return df_shot

def generate_shot_chart(game_id, team1_id, team2_id, team1_name, team2_name, output_file):
    tiriTeam1 = get_action_data('shot', game_id, team1_id)
    tiriTeam2 = get_action_data('shot', game_id, team2_id)

    if tiriTeam1.empty and tiriTeam2.empty:
        print("No shot data available for both teams.")
        return
    elif tiriTeam1.empty:
        print(f"No shot data available for {team1_name}.")
    elif tiriTeam2.empty:
        print(f"No shot data available for {team2_name}.")

    if 'x' not in tiriTeam1.columns or 'y' not in tiriTeam1.columns:
        print(f"DataFrame tiriTeam1 columns: {tiriTeam1.columns}")
        print(f"Missing 'x' or 'y' in tiriTeam1 DataFrame for team {team1_name}")
        return

    if 'x' not in tiriTeam2.columns or 'y' not in tiriTeam2.columns:
        print(f"DataFrame tiriTeam2 columns: {tiriTeam2.columns}")
        print(f"Missing 'x' or 'y' in tiriTeam2 DataFrame for team {team2_name}")
        return

    from mplsoccer import Pitch, FontManager, VerticalPitch
    import seaborn as sns

    pitch = Pitch(pad_top=0.05, pad_right=0.05, pad_bottom=0.05, pad_left=0.05, line_zorder=2)
    vertical_pitch = VerticalPitch(half=True, pad_top=0.05, pad_right=0.05, pad_bottom=0.05, pad_left=0.05, line_zorder=2)
    fm = FontManager()

    tiriTeam1['x'] = pitch.dim.right - tiriTeam1.x

    fig, axs = pitch.jointgrid(figheight=10, left=None, bottom=0.075, marginal=0.1, space=0, grid_width=0.9, title_height=0, axis=False, endnote_height=0, grid_height=0.8)
    sc_team1 = pitch.scatter(tiriTeam1.x, tiriTeam1.y, ec='black', color='#697cd4', ax=axs['pitch'])
    sc_team2 = pitch.scatter(tiriTeam2.x, tiriTeam2.y, ec='black', color='#ba495c', ax=axs['pitch'])
    sns.histplot(y=tiriTeam1.y, ax=axs['left'], element='step', color='#ba495c')
    sns.histplot(x=tiriTeam1.x, ax=axs['top'], element='step', color='#697cd4')
    sns.histplot(x=tiriTeam2.x, ax=axs['top'], element='step', color='#ba495c')
    sns.histplot(y=tiriTeam2.y, ax=axs['right'], element='step', color='#697cd4')
    axs['pitch'].text(x=15, y=70, s=team1_name, fontproperties=fm.prop, color='#ba495c', ha='center', va='center', fontsize=30)
    axs['pitch'].text(x=105, y=70, s=team2_name, fontproperties=fm.prop, color='#697cd4', ha='center', va='center', fontsize=30)

    print(f"Saving figure to {output_file}")
    fig.savefig(output_file)
    plt.close(fig)

    # Check if file exists after saving
    if os.path.isfile(output_file):
        print(f"File saved successfully at {output_file}")
    else:
        print(f"Failed to save the file at {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python generate_shot_chart.py <game_id> <team1_id> <team2_id> <team1_name> <team2_name> <output_file>")
        sys.exit(1)

    game_id = sys.argv[1]
    team1_id = int(sys.argv[2])
    team2_id = int(sys.argv[3])
    team1_name = sys.argv[4]
    team2_name = sys.argv[5]
    output_file = sys.argv[6]

    print(f"Received arguments: game_id={game_id}, team1_id={team1_id}, team2_id={team2_id}, team1_name={team1_name}, team2_name={team2_name}, output_file={output_file}")
    generate_shot_chart(game_id, team1_id, team2_id, team1_name, team2_name, output_file)
