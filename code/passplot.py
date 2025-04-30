from pymongo import MongoClient
import pandas as pd
from matplotlib import rcParams
from mplsoccer import Pitch, FontManager, Sbopen
import warnings
import matplotlib.pyplot as plt
import sys
import json

def get_action_data(type_name, game_id, result_name, player_id, db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    features = db['azioni']
    query = {'type_name': type_name, 'game_id': game_id, 'result_name': result_name, 'player_id': player_id}
    fields = {'start_x': 1, 'start_y': 1, 'end_x': 1, 'end_y': 1, '_id': 0}
    risultati = features.find(query, fields)
    df_pass = pd.DataFrame(list(risultati))
    if not df_pass.empty:
        df_pass.rename(columns={'start_x': 'x', 'start_y': 'y', 'end_x': 'end_x', 'end_y': 'end_y'}, inplace=True)
        df_pass['player_id'] = player_id
    return df_pass

def generate_pass_flow_chart(game_id, team_id, team_name, output_file):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']
    partite = db['partite']
    match = partite.find_one({"wyId": game_id})

    if not match:
        print("Match not found")
        return

    player_ids = []
    player_in_ids = []

    if 'team1' in match and match['team1']['teamId'] == team_id:
        team = match['team1']
    elif 'team2' in match and match['team2']['teamId'] == team_id:
        team = match['team2']
    else:
        print("Team not found in match")
        return

    if 'formation' in team and 'lineup' in team['formation']:
        lineup_str = team['formation']['lineup'].replace("'", '"')
        lineup_dict = json.loads(lineup_str)
        player_ids = [item['playerId'] for item in lineup_dict if isinstance(item, dict) and 'playerId' in item]

    if 'formation' in team and 'substitutions' in team['formation']:
        substitutions_str = team['formation']['substitutions'].replace("'", '"')
        substitutions_dict = json.loads(substitutions_str)
        player_in_ids = [item['playerIn'] for item in substitutions_dict if isinstance(item, dict) and 'playerIn' in item]

    titolariSucc = pd.DataFrame()
    titolariFail = pd.DataFrame()
    subSucc = pd.DataFrame()
    subFail = pd.DataFrame()
    totSucc = pd.DataFrame()
    totFail = pd.DataFrame()

    for player_id in player_ids:
        player_data = get_action_data('pass', game_id, 'success', player_id)
        titolariSucc = pd.concat([titolariSucc, player_data])

    for player_in_id in player_in_ids:
        player_data = get_action_data('pass', game_id, 'success', player_in_id)
        subSucc = pd.concat([subSucc, player_data])

    for player_id in player_ids:
        player_data = get_action_data('pass', game_id, 'fail', player_id)
        titolariFail = pd.concat([titolariFail, player_data])

    for player_in_id in player_in_ids:
        player_data = get_action_data('pass', game_id, 'fail', player_in_id)
        subFail = pd.concat([subFail, player_data])

    totSucc = pd.concat([titolariSucc, subSucc])
    totFail = pd.concat([titolariFail, subFail])

    pitch = Pitch(pad_top=10, line_zorder=2)
    green_arrow = dict(arrowstyle='simple, head_width=0.7', connectionstyle="arc3,rad=-0.8", fc="green", ec="green")
    red_arrow = dict(arrowstyle='simple, head_width=0.7', connectionstyle="arc3,rad=-0.8", fc="red", ec="red")
    fm_scada = FontManager('https://raw.githubusercontent.com/googlefonts/scada/main/fonts/ttf/Scada-Regular.ttf')

    warnings.simplefilter("ignore", UserWarning)
    nrows = 5
    ncols = 3

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 15))
    idx = 0

    for player_id in player_ids:
        row_idx = idx // ncols
        col_idx = idx % ncols
        ax = axs[row_idx, col_idx]
        pitch = Pitch(pad_top=10, line_zorder=2)
        complete_pass = titolariSucc.loc[titolariSucc['player_id'] == player_id]
        incomplete_pass = titolariFail.loc[titolariFail['player_id'] == player_id]
        if not complete_pass.empty:
            pitch.arrows(complete_pass.x, complete_pass.y, complete_pass.end_x, complete_pass.end_y,
                         color='#56ae6c', width=2, headwidth=4, headlength=6, ax=ax)
        if not incomplete_pass.empty:
            pitch.arrows(incomplete_pass.x, incomplete_pass.y, incomplete_pass.end_x, incomplete_pass.end_y,
                         color='#7065bb', width=2, headwidth=4, headlength=6, ax=ax)
        ax.set_title(f'Player ID: {player_id}')
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 100])
        idx += 1

    for player_in_id in player_in_ids:
        row_idx = idx // ncols
        col_idx = idx % ncols
        ax = axs[row_idx, col_idx]
        pitch = Pitch(pad_top=10, line_zorder=2)
        complete_pass = subSucc.loc[subSucc['player_id'] == player_in_id] if 'player_id' in subSucc else pd.DataFrame()
        incomplete_pass = subFail.loc[subFail['player_id'] == player_in_id] if 'player_id' in subFail else pd.DataFrame()
        if not complete_pass.empty:
            pitch.arrows(complete_pass.x, complete_pass.y, complete_pass.end_x, complete_pass.end_y,
                         color='#56ae6c', width=2, headwidth=4, headlength=6, ax=ax)
        if not incomplete_pass.empty:
            pitch.arrows(incomplete_pass.x, incomplete_pass.y, incomplete_pass.end_x, incomplete_pass.end_y,
                         color='#7065bb', width=2, headwidth=4, headlength=6, ax=ax)
        ax.set_title(f'Player ID: {player_in_id}')
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 100])
        idx += 1

    plt.tight_layout()

    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor('#22312b')
    if not totSucc.empty:
        pitch.arrows(totSucc.x, totSucc.y, totSucc.end_x, totSucc.end_y, width=2,
                     headwidth=10, headlength=10, color='#ad993c', ax=ax, label='completed passes')
    if not totFail.empty:
        pitch.arrows(totFail.x, totFail.y, totFail.end_x, totFail.end_y, width=2,
                     headwidth=6, headlength=5, headaxislength=12, color='#ba4f45', ax=ax, label='other passes')
    ax.legend(facecolor='#22312b', handlelength=5, edgecolor='None', fontsize=20, loc='upper left')
    ax.set_title(f'{team_name} passes', fontsize=30)
    plt.savefig(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python passplot.py <game_id> <team_id> <team_name> <output_file>")
        sys.exit(1)

    game_id = int(sys.argv[1])
    team_id = int(sys.argv[2])
    team_name = sys.argv[3]
    output_file = sys.argv[4]

    generate_pass_flow_chart(game_id, team_id, team_name, output_file)
