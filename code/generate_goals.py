from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch, FontManager, VerticalPitch
import sys
import os

def get_action_data(type_name, game_id, team_id, result_name='success', db_name='Soccer'):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    features = db['azioni']
    query = {'type_name': type_name, 'game_id': int(game_id), 'team_id': team_id, 'result_name': result_name}
    fields = {'start_x': 1, 'start_y': 1, 'end_x': 1, 'end_y': 1, '_id': 0}
    risultati = features.find(query, fields)
    df_action = pd.DataFrame(list(risultati))
    print(f"Query: {query}")
    print(f"Number of actions retrieved: {len(df_action)}")
    if not df_action.empty:
        df_action.rename(columns={'start_x': 'x', 'start_y': 'y', 'end_x': 'end_x', 'end_y': 'end_y'}, inplace=True)
    return df_action

def generate_no_goals_image(output_file, team1_name, team2_name):
    plt.figure(figsize=(10, 5))
    plt.text(0.5, 0.5, f'No goals su azione in {team1_name} vs. {team2_name}', horizontalalignment='center', verticalalignment='center', fontsize=20)
    plt.axis('off')
    plt.savefig(output_file)
    plt.close()

def generate_goal_chart(game_id, team1_id, team2_id, team1_name, team2_name, output_file):
    df_goals_team1 = get_action_data('shot', game_id, team1_id)
    df_goals_team2 = get_action_data('shot', game_id, team2_id)

    if df_goals_team1.empty and df_goals_team2.empty:
        print("Non sono stati segnati gol su azioni.")
        generate_no_goals_image(output_file, team1_name, team2_name)
        return
    elif df_goals_team1.empty:
        print(f"Non sono stati segnati gol su azioni da {team1_name}.")
    elif df_goals_team2.empty:
        print(f"Non sono stati segnati gol su azioni da {team2_name}.")

    plt.style.use('ggplot')

    pitch = VerticalPitch(half=True, goal_type='box', pad_bottom=0)
    fig, axs = pitch.grid(figheight=8, endnote_height=0, title_height=0.1, title_space=0.02, axis=False, grid_height=0.83)

    teams = {team1_name: 'blue', team2_name: 'red'}
    
    if not df_goals_team1.empty:
        pitch.scatter(df_goals_team1.x, df_goals_team1.y, color=teams[team1_name], s=200, ax=axs['pitch'], zorder=1.2, label=team1_name)

    if not df_goals_team2.empty:
        pitch.scatter(df_goals_team2.x, df_goals_team2.y, color=teams[team2_name], s=200, ax=axs['pitch'], zorder=1.2, label=team2_name)

    pitch.goal_angle(pd.concat([df_goals_team1, df_goals_team2]).x, 
                     pd.concat([df_goals_team1, df_goals_team2]).y, 
                     ax=axs['pitch'], alpha=0.2, zorder=1.1, color='#cb5a4c', goal='left')

    robotto_regular = FontManager()

    legend = axs['pitch'].legend(loc='center left', labelspacing=1.5)
    for text in legend.get_texts():
        text.set_fontproperties(robotto_regular.prop)
        text.set_fontsize(20)
        text.set_va('center')

    axs['title'].text(0.5, 0.5, f'Goals in {team1_name} vs. {team2_name}', va='center', ha='center', color='black', fontproperties=robotto_regular.prop, fontsize=25)

    axs['pitch'].set_xlim([-10, 90])
    axs['pitch'].set_ylim([-10, 50])

    try:
        fig.savefig(output_file)
        print(f"Goal chart saved to {output_file}")
    except Exception as e:
        print(f"Error saving goal chart: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python generate_goals.py <game_id> <team1_id> <team2_id> <team1_name> <team2_name> <output_file>")
        sys.exit(1)

    game_id = sys.argv[1]
    team1_id = int(sys.argv[2])
    team2_id = int(sys.argv[3])
    team1_name = sys.argv[4]
    team2_name = sys.argv[5]
    output_file = sys.argv[6]

    print(f"Received arguments: game_id={game_id}, team1_id={team1_id}, team2_id={team2_id}, team1_name={team1_name}, team2_name={team2_name}, output_file={output_file}")
    generate_goal_chart(game_id, team1_id, team2_id, team1_name, team2_name, output_file)
