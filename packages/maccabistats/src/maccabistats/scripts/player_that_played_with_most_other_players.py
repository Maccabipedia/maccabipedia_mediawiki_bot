from pprint import pformat
from typing import Tuple, List

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import squarify
from bidi import algorithm as bidialg

from maccabistats import *


def squarify_show_chart(best_players: List[Tuple]):
    sizes = [players_amount * players_amount for player_name, players_amount in top_players]
    labels = [f'{bidialg.get_display(player_name)} - {players_amount}' for player_name, players_amount in top_players]
    squarify.plot(sizes=sizes,
                  label=labels,
                  alpha=0.6,
                  color=['black', 'blue', 'yellow'],
                  pad=True
                  )
    plt.axis('off')
    plt.show()


def plotly_show_chart(best_players: List[Tuple]):
    labels = [f'{bidialg.get_display(player_name)} - {players_amount}' for player_name, players_amount in top_players]

    fig = px.treemap(names=labels,
                     parents=[""] * len(labels))
    fig.show()


def plotly_horizontal_bar_chart(best_players: List[Tuple]):
    # Reversed in order to have the top player inserted last (shown at the top of the chart)
    sizes = [players_amount for player_name, players_amount in reversed(best_players)]
    names = [player_name for player_name, players_amount in reversed(best_players)]
    quarter = int(len(best_players) / 4)

    colors = ['#195da6'] * (len(best_players) - 10)
    colors.extend(['#ffdd00'] * 10)  # Top 10 in yellow

    fig = go.Figure(go.Bar(
        x=names,
        y=sizes,
        orientation='v',
        text=sizes,
        textposition='outside',
        marker=dict(color=colors)
    ))

    fig.update_layout(
        title="מכביפדיה: מיהם השחקנים ששיתפו פעולה עם הכי הרבה שחקנים אחרים? שיתפו פעולה=שיחקו באותו המשחק, עשרת הגדולים בצהוב",
        title_x=0.5,
        title_xanchor='center',
        xaxis_title="שם שחקן",
        yaxis_title="מספר השחקנים ששיתפו איתם פעולה",
    )

    fig.show()


# For each player:
# 1) take the games he played at
# 2) From these games, calculate the amount of players that was participate in any game from these games
# 3) Decrease by one (the checked player itself)
# 4) The final number is the players number that this player played with~
if __name__ == '__main__':
    maccabipedia_games = load_from_maccabipedia_source().official_games

    # Change 'games_by_player_name' players games to be just "played players" from maccabi and not in the squad
    players_games = maccabipedia_games.played_games_by_player_name()
    players_to_available_players_len = dict()

    for player_name, games in players_games.items():
        # Get just the played players, -1 himself
        players_to_available_players_len[player_name] = len(games.players.most_played) - 1

    most_played_with_others_player = sorted(players_to_available_players_len.items(), key=lambda item: item[1],
                                            reverse=True)
    top_players = most_played_with_others_player[:30]
    print(f'Top: {pformat(top_players)}')

    # squarify_show_chart(top_players)
    # plotly_show_chart(top_players)
    plotly_horizontal_bar_chart(top_players)
