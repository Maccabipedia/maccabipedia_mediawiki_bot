from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING
from typing import Tuple, List, Callable

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

CoachStats = Tuple[str, float]  # Coach name to the current stat (an int ranking)


class MaccabiGamesCoachesStats(object):
    """
    This class will handle all coaches statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats) -> None:
        self.games = maccabi_games_stats.games

    # region General scoring for coaches functions
    @property
    def most_clean_sheet_games_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: g.not_maccabi_team.score == 0)

    @property
    def most_games_with_goals_from_bench_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: 1 if g.maccabi_team.has_goal_from_bench else 0)

    @property
    def most_goals_for_maccabi_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: g.maccabi_team.score)

    @property
    def most_goals_against_maccabi_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: g.not_maccabi_team.score)

    @property
    def most_trained_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: 1)

    @property
    def most_winner_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: g.is_maccabi_win)

    @property
    def most_loser_coach(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: g.maccabi_score_diff < 0)

    @property
    def most_red_cards_to_players(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: sum(g.maccabi_team.red_carded_players_with_amount.values()))

    @property
    def most_yellow_cards_to_players(self) -> List[CoachStats]:
        return self._calculate_coaches_stats(lambda g: sum(g.maccabi_team.yellow_carded_players_with_amount.values()))

    # endregion

    # region Percentage functions
    def most_winner_coach_by_percentage(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_winner_coach, calculate_as_percentage=True,
                                                           minimum_games=minimum_games)

    def most_loser_coach_by_percentage(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_loser_coach, calculate_as_percentage=True,
                                                           minimum_games=minimum_games)

    def most_clean_sheet_games_coach_by_percentage(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_clean_sheet_games_coach,
                                                           calculate_as_percentage=True,
                                                           minimum_games=minimum_games)

    def most_games_with_goals_from_bench_coach_by_percentage(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_games_with_goals_from_bench_coach,
                                                           calculate_as_percentage=True,
                                                           minimum_games=minimum_games)

    # endregion

    # region Per game functions
    def most_goals_for_maccabi_per_game_coach(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_goals_for_maccabi_coach,
                                                           calculate_as_percentage=False,
                                                           minimum_games=minimum_games)

    def most_goals_against_maccabi_per_game_coach(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_goals_against_maccabi_coach,
                                                           calculate_as_percentage=False,
                                                           minimum_games=minimum_games)

    def most_red_cards_to_players_per_game_coach(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_red_cards_to_players,
                                                           calculate_as_percentage=False,
                                                           minimum_games=minimum_games)

    def most_yellow_cards_to_players_per_game_coach(self, minimum_games: int = 0) -> List[CoachStats]:
        return self._calculate_coaches_stat_relate_to_game(self.most_yellow_cards_to_players,
                                                           calculate_as_percentage=False,
                                                           minimum_games=minimum_games)

    # endregion

    def _calculate_coaches_stat_relate_to_game(self, coaches_stats_dict: List[CoachStats],
                                               calculate_as_percentage: bool,
                                               minimum_games: int = 0) -> List[CoachStats]:
        """
        Calculate a property of coach stat with a ratio to the coach trained games,
        Like:
        * total goals for maccabi PER game
        * maccabi wins percentage

        When calculating percentage you have to send a coaches_stats_dict which is a boolean property of a game,
        like is maccabi won? (0 or 1 per game), and not like amount of goals for maccabi.
        """

        trained_games = {coach: coach_games_number for coach, coach_games_number in self.most_trained_coach if
                         coach_games_number >= minimum_games}
        coaches_stats = Counter(dict(coaches_stats_dict))
        games_ratio = 100 if calculate_as_percentage else 1

        coaches = Counter()
        for coach_name, trained_times in trained_games.items():
            key_name = "{coach} - {trained}".format(coach=coach_name, trained=trained_times)
            coaches[key_name] = round(coaches_stats[coach_name] / trained_times * games_ratio, 2)

        return coaches.most_common()

    def _calculate_coaches_stats(self, game_score_callback: Callable) -> List[CoachStats]:
        """
        Calculate a stat for every coach, A stat is a property which gives a score to the coach for every game.
        Like:
        * Does maccabi won the game? if so - the score for the coach will be 1, otherwise - 0
        * How many goals maccabi scored in a game? this will be the score of the coach
        """
        coach_to_stat_score = defaultdict(lambda: 0)
        for game in self.games:
            coach_to_stat_score[game.maccabi_team.coach] += game_score_callback(game)

        return Counter(coach_to_stat_score).most_common()
