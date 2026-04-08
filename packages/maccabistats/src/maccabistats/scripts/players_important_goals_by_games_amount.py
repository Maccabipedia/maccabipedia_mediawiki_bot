from dataclasses import dataclass
from typing import Dict, Tuple, Any, Optional

from bidi import algorithm as bidialg
from matplotlib import pyplot as plt

from maccabistats import *

_PLAYERS_TO_SHOW_NAME = 20
_PLAYERS_TO_SHOW_IN_GRAPH = 50


@dataclass
class PlayersImportantGoals:
    player_to_played_games: Dict[str, int]

    player_to_important_goals: Dict[str, int]
    player_to_important_goals_per_game: Dict[str, float]

    player_to_important_goals_last_minutes: Dict[str, int]
    player_to_important_goals_last_minutes_per_game: Dict[str, float]

    player_to_important_goals_advantage_only: Dict[str, int]

    player_to_important_goals_percentage_from_total_goals: Dict[str, int]

    @staticmethod
    def _remove_per_game_text(player_name: str) -> str:
        return player_name.split("-")[0].strip()

    @property
    def players_important_goals_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {player_name: (player_goals, self.player_to_played_games.get(player_name, 1)) for
                player_name, player_goals in self.player_to_important_goals.items()}

    @property
    def players_important_goals_last_minutes_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {player_name: (player_goals, self.player_to_played_games.get(player_name, 1)) for
                player_name, player_goals in self.player_to_important_goals_last_minutes.items()}

    @property
    def players_important_goals_advantage_only_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {player_name: (player_goals, self.player_to_played_games.get(player_name, 1)) for
                player_name, player_goals in self.player_to_important_goals_advantage_only.items()}

    @property
    def players_important_goals_per_game_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {self._remove_per_game_text(player_name): (
            player_goals_per_game, self.player_to_played_games.get(self._remove_per_game_text(player_name), 1)) for
            player_name, player_goals_per_game in self.player_to_important_goals_per_game.items()}

    @property
    def players_important_goals_last_minutes_per_game_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {self._remove_per_game_text(player_name): (
            player_goals_per_game, self.player_to_played_games.get(self._remove_per_game_text(player_name), 1)) for
            player_name, player_goals_per_game in self.player_to_important_goals_last_minutes_per_game.items()}

    @property
    def players_important_goals_percentage_from_games_and_games(self) -> Dict[str, Tuple[int, int]]:
        return {self._remove_per_game_text(player_name): (
            player_goals_per_game, self.player_to_played_games.get(self._remove_per_game_text(player_name), 1)) for
            player_name, player_goals_per_game in self.player_to_important_goals_percentage_from_total_goals.items()}


def get_players_important_goals_stats() -> PlayersImportantGoals:
    maccabi_games = load_from_maccabipedia_source().official_games

    return PlayersImportantGoals(
        player_to_played_games=dict(maccabi_games.players.most_played),
        player_to_important_goals=dict(maccabi_games.important_goals.get_top_scorers(0, 1)),
        player_to_important_goals_per_game=dict(
            maccabi_games.important_goals.get_top_players_for_goals_per_game(0, 1, minimum_games=20)),
        player_to_important_goals_last_minutes=dict(
            maccabi_games.important_goals.get_top_scorers_in_last_minutes(0, 1)),
        player_to_important_goals_last_minutes_per_game=
        dict(maccabi_games.important_goals.get_top_players_for_goals_in_last_minutes_per_game(0, 1, minimum_games=20)),
        player_to_important_goals_advantage_only=dict(maccabi_games.important_goals.get_top_scorers_for_advantage()),
        player_to_important_goals_percentage_from_total_goals=dict(
            maccabi_games.important_goals.get_top_scorers_by_percentage_from_all_their_goals(0, 1))
    )


def show_player_important_goals_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים שכבשו הכי הרבה שערים חשובים.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה.\n'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_and_games)


def show_player_important_goals_last_minutes_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים שכבשו הכי הרבה שערים חשובים ברבע השעה האחרונה בלבד.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_last_minutes_and_games)


def show_player_important_goals_advantage_only_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים שכבשו הכי הרבה שערים חשובים שהובילו ליתרון בלבד.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_advantage_only_and_games)


def show_player_important_goals_per_game_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים שכבשו הכי הרבה שערים חשובים - ממוצע למשחק.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה.\n'
        '* מוצגים רק שחקנים עם 20 משחקים רשמיים לפחות.'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_per_game_and_games)


def show_player_important_goals_last_minutes_per_game_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים שכבשו הכי הרבה שערים חשובים ברבע השעה האחרונה בלבד - ממוצע למשחק.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה.\n'
        '* מוצגים רק שחקנים עם 20 משחקים רשמיים לפחות.'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_last_minutes_per_game_and_games,
                                         names_to_positions={
                                             'נתן פנץ': (13, -7),
                                             'ציון צמח': (0, 10),
                                             'יעקב נומדר': (-20, -13),
                                         })


def show_player_important_goals_percentage_from_goals_to_games_graph(players_stats: PlayersImportantGoals):
    plt.title(bidialg.get_display(
        'השחקנים לפי אחוז השערים החשובים מסך השערים הכללי שלהם.\n'
        'שער חשוב: שער שבזכותו מכבי השוותה או נכנסה להובלה'))
    plt.xlabel(bidialg.get_display('שערים חשובים'))
    plt.ylabel(bidialg.get_display('כמות משחקים'))

    show_graph_from_player_stat_to_games(players_stats.players_important_goals_percentage_from_games_and_games,
                                         names_to_positions={
                                             'האריד מדוניאנין': (10, 15),
                                             'אורי קדמי': (-35, -15),
                                             'אורי מלמיליאן': (5, 5),
                                             'איליה יבוריאן': (-5, -15),
                                         })


def show_graph_from_player_stat_to_games(player_stats_to_games: Dict[str, Tuple[Any, int]],
                                         names_to_positions: Optional[Dict[str, Tuple]] = None) -> None:
    # we get too much overlaps, there seems to not be an easy solution for that in matplotlib
    names_to_positions = names_to_positions or {}

    x, y = list(zip(*player_stats_to_games.values()))
    plt.scatter(x[:_PLAYERS_TO_SHOW_IN_GRAPH], y[:_PLAYERS_TO_SHOW_IN_GRAPH])

    for player_name, player_values in list(player_stats_to_games.items())[:_PLAYERS_TO_SHOW_NAME]:
        position = names_to_positions.get(player_name, (5, 0))

        plt.annotate(bidialg.get_display(player_name),
                     xy=player_values,
                     xytext=position,
                     textcoords='offset points')

    plt.show()


if __name__ == '__main__':
    players_important_goals_stats = get_players_important_goals_stats()

    # show_player_important_goals_to_games_graph(players_important_goals_stats)
    # show_player_important_goals_last_minutes_to_games_graph(players_important_goals_stats)
    # show_player_important_goals_per_game_to_games_graph(players_important_goals_stats)
    # show_player_important_goals_last_minutes_per_game_to_games_graph(players_important_goals_stats)
    # show_player_important_goals_advantage_only_to_games_graph(players_important_goals_stats)
    show_player_important_goals_percentage_from_goals_to_games_graph(players_important_goals_stats)
