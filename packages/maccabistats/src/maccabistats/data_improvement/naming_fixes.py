from difflib import SequenceMatcher
from itertools import combinations
import logging

logger = logging.getLogger(__name__)

SIMILARITY_MINIMAL_RATIO = 0.9


class NamingErrorsFinder(object):
    """
    This class is responsible for trying find similar names for each attribute of MaccabiGamesStats like:
    player named "avi nimni" and "avi nimmni" and so on.

    ratio = 1.0 wont be print because we use set for all objects.
    """

    def __init__(self, maccabi_games_stats, minimal_ratio_to_alert=SIMILARITY_MINIMAL_RATIO):
        """
        :type maccabi_games_stats: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
        :param minimal_ratio_to_alert: the minimum ratio to report about naming similarity for.
        :type: float
        """

        self.games = maccabi_games_stats
        self.minimal_ratio = minimal_ratio_to_alert

    def show_naming_similarities(self):
        """
        Check for all naming errors and print them!
        """

        total_diff = 0
        total_diff += self.__print_coaches_naming_similarities()
        total_diff += self.__print_referees_naming_similarities()
        total_diff += self.__print_opponents_naming_similarities()
        total_diff += self.__print_stadiums_naming_similarities()
        total_diff += self.__print_players_naming_similarities()

        return total_diff

    # We use set to reduce duplication of the same players (or other object that are equal).
    def __print_coaches_naming_similarities(self):
        return self.__print_couples_naming_similarity(combinations(set(self.games.available_coaches), 2), "Coaches")

    def __print_referees_naming_similarities(self):
        return self.__print_couples_naming_similarity(combinations(set(self.games.available_referees), 2), "Referees")

    def __print_opponents_naming_similarities(self):
        return self.__print_couples_naming_similarity(combinations(set(self.games.available_opponents), 2), "Opponents")

    def __print_stadiums_naming_similarities(self):
        return self.__print_couples_naming_similarity(combinations(set(self.games.available_stadiums), 2), "Stadiums")

    def __print_players_naming_similarities(self):
        return self.__print_couples_naming_similarity(combinations(set([p.name for p in self.games.available_players]), 2), "Players")

    def __print_couples_naming_similarity(self, couples_combinations, prefix_to_print):
        diff = 0
        for couple in couples_combinations:
            current_ratio = self.__similarity_of_two_names(*couple)
            if current_ratio > self.minimal_ratio:
                diff += 1
                logger.info("{prefix}: {} - {}, ratio - {ratio}".format(prefix=prefix_to_print, *couple, ratio=round(current_ratio, 2)))

        return diff

    @staticmethod
    def __similarity_of_two_names(first, second):
        """
        Check the similarity of two names, returns the similarity between 0 and 1.
        :type first: str
        :type second: str
        :rtype: float
        """

        return SequenceMatcher(None, first, second).ratio()

    @staticmethod
    def get_similar_names(name, optional_similar_names, ratio=SIMILARITY_MINIMAL_RATIO):
        """
        Returns the list of similar names from the given list (which above the given ratio)
        :param name: THe name to check similarity with
        :type name: str
        :param optional_similar_names: The names to check similarity against the main name
        :type optional_similar_names: list of str
        :param ratio: The minimal ratio of similarity (0.0 - 1.0)
        :type ratio: float
        :return: Similar names
        :rtype: list of str
        """
        return [optional_name for optional_name in optional_similar_names if
                NamingErrorsFinder.__similarity_of_two_names(name, optional_name) > ratio]
