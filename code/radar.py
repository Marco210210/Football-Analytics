import sys
from pymongo import MongoClient
import matplotlib.pyplot as plt
from mplsoccer import Radar, FontManager

def fetch_player_data(player_wyId):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Soccer']
    actions = db['azioni']

    stats = {
        'passaggi': actions.count_documents({'type_name': 'pass', 'result_name': 'success', 'player_id': player_wyId}),
        'goal su azione': actions.count_documents({'type_name': 'shot', 'result_name': 'success', 'player_id': player_wyId}),
        'cross': actions.count_documents({'type_name': 'cross', 'result_name': 'success', 'player_id': player_wyId}),
        'intercettazioni': actions.count_documents({'type_name': 'interception', 'result_name': 'success', 'player_id': player_wyId}),
        'salvataggi': actions.count_documents({'type_name': 'clearance', 'result_name': 'success', 'player_id': player_wyId}),
        'dribling': actions.count_documents({'type_name': 'dribble', 'result_name': 'success', 'player_id': player_wyId}),
        'gol su punizione corta': actions.count_documents({'type_name': 'freekick_short', 'result_name': 'success', 'player_id': player_wyId}),
        'contrasti': actions.count_documents({'type_name': 'tackle', 'result_name': 'success', 'player_id': player_wyId})
    }

    return list(stats.values())

URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
robotto_thin = FontManager(URL4)

def generate_radar_chart(player_wyId, output_file):
    params = ["passaggi", "goal su azione", "cross", "intercettazioni", "salvataggi", "dribling", "gol su punizione corta", "contrasti"]
    low = [0, 0, 0, 0, 0, 0, 0, 0]
    high = [2000, 40, 80, 80, 50, 150, 15, 90]

    player_values = fetch_player_data(player_wyId)

    radar = Radar(params, low, high, num_rings=4, ring_width=1, center_circle_radius=1)

    fig, ax = radar.setup_axis()  # format axis as a radar
    rings_inner = radar.draw_circles(ax=ax, facecolor='#ffb2b2', edgecolor='#fc5f5f')  # draw circles
    radar_output = radar.draw_radar(player_values, ax=ax,
                                kwargs_radar={'facecolor': '#aa65b2'},
                                kwargs_rings={'facecolor': '#66d8ba'})  # draw the radar
    radar_poly, rings_outer, vertices = radar_output
    lines = radar.spoke(ax=ax, color='#a6a4a1', linestyle='--', zorder=2)

    radar.draw_range_labels(ax=ax, fontsize=15, color='#000000')
    radar.draw_param_labels(ax=ax, fontsize=25, color='#000000')

    plt.savefig(output_file)
    plt.close(fig)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python radar.py <player_wyId> <output_file>")
        sys.exit(1)

    player_wyId = int(sys.argv[1])
    output_file = sys.argv[2]
    generate_radar_chart(player_wyId, output_file)
