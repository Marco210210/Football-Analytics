import os
import pandas as pd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from mplsoccer import Pitch, FontManager
from pymongo import MongoClient
import sys

output_file = 'summary_chart.png'

# Controlla se il file summary_chart.png esiste già
# Inserito solo per velocizzare la demo live
if os.path.exists(output_file):
    print(f"Il file {output_file} esiste già. Non è necessario rigenerarlo.")
    plt.imshow(plt.imread(output_file))
    plt.axis('off')
else:
    # Connessione al database MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Soccer"]
    eventi_collezione = db["eventi"]
    squadre_collezione = db["squadre"]

    # Carica i dati dalle collezioni MongoDB
    eventi_df = pd.DataFrame(list(eventi_collezione.find()))
    squadre_df = pd.DataFrame(list(squadre_collezione.find()))

    # Filtra gli eventi per i soli "Touch"
    tocchi_df = eventi_df[eventi_df['eventId'] == 7]
    # Aggrega i dati degli eventi per ottenere il numero di tocchi in ciascuna area
    touches_df = tocchi_df.groupby('teamId').agg({
        'pos_orig_x': lambda x: ((x < 33).sum(), ((x >= 33) & (x <= 66)).sum(), (x > 66).sum())
    }).reset_index()

    # Splitta i dati aggregati in colonne separate per le tre aree
    touches_df[['Def 3rd', 'Mid 3rd', 'Att 3rd']] = pd.DataFrame(touches_df['pos_orig_x'].tolist(), index=touches_df.index)
    touches_df.drop(columns='pos_orig_x', inplace=True)

    # Merge con i nomi delle squadre
    df = touches_df.merge(squadre_df, left_on='teamId', right_on='wyId')
    df = df[['name', 'Def 3rd', 'Mid 3rd', 'Att 3rd']]

    # Normalizza i dati per ottenere le percentuali
    df_total = pd.DataFrame(df[['Def 3rd', 'Mid 3rd', 'Att 3rd']].sum())
    df_total.columns = ['total']
    df_total = df_total.T
    df_total = df_total.divide(df_total.sum(axis=1), axis=0) * 100
    df[['Def 3rd', 'Mid 3rd', 'Att 3rd']] = df[['Def 3rd', 'Mid 3rd', 'Att 3rd']].divide(df[['Def 3rd', 'Mid 3rd', 'Att 3rd']].sum(axis=1), axis=0) * 100
    df.sort_values(['Att 3rd', 'Def 3rd'], ascending=[True, False], inplace=True)

    fm = FontManager()
    path_eff = [path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()]
    pitch = Pitch(line_zorder=2, line_color='black', pad_top=20)

    bin_statistic = pitch.bin_statistic([0], [0], statistic='count', bins=(3, 1))

    GRID_HEIGHT = 0.8
    CBAR_WIDTH = 0.03
    fig, axs = pitch.grid(nrows=4, ncols=5, figheight=10,
                          grid_width=0.88, left=0.025,
                          endnote_height=0.03, endnote_space=0,
                          axis=False,
                          title_space=0.02, title_height=0.06, grid_height=GRID_HEIGHT)
    fig.set_facecolor('white')

    df.sort_values(by='name', inplace=True)
    teams = df['name'].values
    vmin = df[['Def 3rd', 'Mid 3rd', 'Att 3rd']].min().min()
    vmax = df[['Def 3rd', 'Mid 3rd', 'Att 3rd']].max().max()
    for i, ax in enumerate(axs['pitch'].flat[:len(teams)]):
        ax.text(60, -10, teams[i], ha='center', va='center', fontsize=25, fontproperties=fm.prop)
        bin_statistic['statistic'] = df.loc[df.name == teams[i], ['Def 3rd', 'Mid 3rd', 'Att 3rd']].values
        heatmap = pitch.heatmap(bin_statistic, ax=ax, cmap='coolwarm', vmin=vmin, vmax=vmax)
        annotate = pitch.label_heatmap(bin_statistic, color='white', fontproperties=fm.prop,
                                       path_effects=path_eff, fontsize=25, ax=ax,
                                       str_format='{0:.0f}%', ha='center', va='center')

    cbar_bottom = axs['pitch'][-1, 0].get_position().y0
    cbar_left = axs['pitch'][0, -1].get_position().x1 + 0.01
    ax_cbar = fig.add_axes((cbar_left, cbar_bottom, CBAR_WIDTH, GRID_HEIGHT - 0.036))
    cbar = plt.colorbar(heatmap, cax=ax_cbar)
    for label in cbar.ax.get_yticklabels():
        label.set_fontproperties(fm.prop)
        label.set_fontsize(25)

    plt.savefig(output_file)
    plt.imshow(plt.imread(output_file))
    plt.axis('off')
