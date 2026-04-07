from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from maccabistats.models.player_game_events import GoalTypes

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from datetime import timedelta
from collections import Counter


class MaccabiGamesImportantGoalsStats(object):
    """
    This class will handle all important goals statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def get_top_scorers_for_advantage(self):
        """
        Get all players who score goal that made maccabi the lead team AFTER the goal was scored.
        """

        return self.get_top_scorers(1, 1)

    def get_top_scorers(self, minimum_diff_for_maccabi: int = -2, maximum_diff_for_maccabi: int = 1,
                        goal_condition=None) -> List[Tuple[str, float]]:
        if goal_condition is None:
            goal_condition = lambda x: True

        maccabi_goals = [goal for game in self.games for goal in game.goals() if
                         goal['team'] == "מכבי תל אביב" and goal['goal_type'] != GoalTypes.OWN_GOAL.value]
        maccabi_important_goals = [
            goal for goal in maccabi_goals if
            (minimum_diff_for_maccabi <= goal['maccabi_score'] - goal['not_maccabi_score'] <= maximum_diff_for_maccabi)
            and goal_condition(goal)]

        important_goals_scorers_names = [goal['name'] for goal in maccabi_important_goals]
        return Counter(important_goals_scorers_names).most_common()

    def get_top_scorers_by_percentage_from_all_their_goals(
            self, minimum_diff_for_maccabi: int = -2, maximum_diff_for_maccabi: int = 1,
            minimum_important_goals: int = 10, goal_condition=None) -> List[Tuple[str, float]]:
        """
        Return the important goals percentage for each player from his total goals.
        Only for those who scored at least (minimum_important_goals).
        """
        players_total_goals = Counter(dict(self.maccabi_games_stats.players.best_scorers))
        players_important_goals = Counter(
            dict(self.get_top_scorers(minimum_diff_for_maccabi, maximum_diff_for_maccabi,
                                      goal_condition=goal_condition)))

        best_players = Counter()
        for player_name, total_goals_for_player in players_total_goals.items():
            if players_important_goals[player_name] >= minimum_important_goals:
                key_name = "{player} - {total_goals} goals".format(player=player_name,
                                                                   total_goals=total_goals_for_player)
                best_players[key_name] = round(players_important_goals[player_name] / total_goals_for_player * 100, 5)

        return best_players.most_common()

    def get_top_players_for_goals_per_game(self, minimum_diff_for_maccabi: int = -2, maximum_diff_for_maccabi: int = 1,
                                           minimum_games: int = 10, goal_condition=None) -> List[Tuple[str, float]]:
        """
        Return the important goals per game for each player, only for those who played at least (minimum_games).
        """
        players_total_played = Counter(dict(self.maccabi_games_stats.players.most_played))
        players_important_goals = Counter(
            dict(self.get_top_scorers(minimum_diff_for_maccabi, maximum_diff_for_maccabi,
                                      goal_condition=goal_condition)))

        best_players = Counter()
        for player_name, total_games_for_player in players_total_played.items():
            if total_games_for_player >= minimum_games:
                key_name = "{player} - {total_games} games".format(player=player_name,
                                                                   total_games=total_games_for_player)
                best_players[key_name] = round(players_important_goals[player_name] / total_games_for_player, 5)

        return best_players.most_common()

    def get_top_scorers_in_last_minutes(self, minimum_diff_for_maccabi=-2, maximum_diff_for_maccabi=1, from_minute=75):
        return self.get_top_scorers(minimum_diff_for_maccabi, maximum_diff_for_maccabi,
                                    lambda g: g['time_occur'] > str(timedelta(minutes=from_minute)))

    def get_top_scorers_in_last_minutes_by_percentage_from_all_their_goals(
            self, minimum_diff_for_maccabi: int = -2, maximum_diff_for_maccabi: int = 1,
            from_minute: int = 75, minimum_important_goals: int = 10) -> List[Tuple[str, float]]:
        """
        Return the important goals percentage (in the last minutes) for each player from his total goals,
        Only for those who scored at least (minimum_important_goals).
        """
        return self.get_top_scorers_by_percentage_from_all_their_goals(
            minimum_diff_for_maccabi=minimum_diff_for_maccabi,
            maximum_diff_for_maccabi=maximum_diff_for_maccabi,
            minimum_important_goals=minimum_important_goals,
            goal_condition=lambda g: g['time_occur'] > str(timedelta(minutes=from_minute)))

    def get_top_players_for_goals_in_last_minutes_per_game(self, minimum_diff_for_maccabi: int = -2,
                                                           maximum_diff_for_maccabi: int = 1, minimum_games: int = 10,
                                                           from_minute: int = 75) -> List[Tuple[str, float]]:
        """
        Return the important goals per game for each player, only for those who played at least (minimum_games).
        """
        return self.get_top_players_for_goals_per_game(minimum_diff_for_maccabi=minimum_diff_for_maccabi,
                                                       maximum_diff_for_maccabi=maximum_diff_for_maccabi,
                                                       minimum_games=minimum_games,
                                                       goal_condition=lambda g: g['time_occur'] > str(
                                                           timedelta(minutes=from_minute)))
