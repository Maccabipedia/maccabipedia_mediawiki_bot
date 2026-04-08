"""Tests for MaccabiGamesPlayersStats."""


class TestBestScorers:
    def test_best_scorers_order(self, maccabi_games):
        scorers = maccabi_games.players.best_scorers
        # אבי נמני: 8 goals across games (2+0+1+1+2+0+1+1+0+0 = 8)
        assert scorers[0] == ("אבי נמני", 8)

    def test_best_scorers_second(self, maccabi_games):
        scorers = dict(maccabi_games.players.best_scorers)
        # אלי דריקס: 2 goals (1+0+0+1+0+0+0+0+0+0)
        assert scorers["אלי דריקס"] == 2

    def test_best_scorers_sub_player(self, maccabi_games):
        scorers = dict(maccabi_games.players.best_scorers)
        # ערן זהבי: 2 goals (game 5 at 80min + game 6 at 85min)
        assert scorers["ערן זהבי"] == 2

    def test_best_scorers_by_penalty(self, maccabi_games):
        penalty_scorers = dict(maccabi_games.players.best_scorers_by_penalty)
        assert penalty_scorers.get("אבי נמני", 0) == 1  # Game 3 penalty

    def test_best_scorers_by_head(self, maccabi_games):
        header_scorers = dict(maccabi_games.players.best_scorers_by_head)
        # אלי דריקס: headers in game 1 and game 4
        assert header_scorers.get("אלי דריקס", 0) == 2

    def test_best_scorers_by_freekick(self, maccabi_games):
        fk_scorers = dict(maccabi_games.players.best_scorers_by_freekick)
        assert fk_scorers.get("אבי נמני", 0) == 1  # Game 4 free kick


class TestBestAssisters:
    def test_best_assisters(self, maccabi_games):
        assisters = maccabi_games.players.best_assisters
        # חיים רביבו assists in games 1(2), 4(2), 5(2), 7(1), 8(1) = 8
        assert assisters[0][0] == "חיים רביבו"
        assert assisters[0][1] == 8

    def test_most_goals_involved(self, maccabi_games):
        involved = dict(maccabi_games.players.most_goals_involved)
        # אבי נמני: 8 goals + 0 assists = 8
        # חיים רביבו: 0 goals + 8 assists = 8
        assert involved["חיים רביבו"] == 8
        assert involved["אבי נמני"] == 8


class TestAssistTypes:
    def test_best_assisters_by_corner(self, maccabi_games):
        corner_assists = dict(maccabi_games.players.best_assisters_by_corner)
        # חיים רביבו: corner assists in game 1 and game 4
        assert corner_assists.get("חיים רביבו", 0) == 2


class TestMostPlayed:
    def test_most_played(self, maccabi_games):
        played = dict(maccabi_games.players.most_played)
        # אבי נמני plays in all 10 games
        assert played["אבי נמני"] == 10

    def test_most_played_sub_player(self, maccabi_games):
        played = dict(maccabi_games.players.most_played)
        # ערן זהבי plays 3 games (sub in)
        assert played["ערן זהבי"] == 3


class TestGameConditions:
    def test_most_winners(self, maccabi_games):
        winners = dict(maccabi_games.players.most_winners)
        # אבי נמני played all 10 games, 6 are wins
        assert winners["אבי נמני"] == 6

    def test_most_losers(self, maccabi_games):
        losers = dict(maccabi_games.players.most_losers)
        assert losers["אבי נמני"] == 2

    def test_most_unbeaten(self, maccabi_games):
        unbeaten = dict(maccabi_games.players.most_unbeaten)
        # 6 wins + 2 ties = 8 unbeaten
        assert unbeaten["אבי נמני"] == 8

    def test_most_clean_sheet(self, maccabi_games):
        clean = dict(maccabi_games.players.most_clean_sheet)
        # 4 clean sheets
        assert clean["אבי נמני"] == 4


class TestCards:
    def test_most_yellow_carded(self, maccabi_games):
        yellows = dict(maccabi_games.players.most_yellow_carded)
        # אבי נמני: 1 yellow (game 2)
        # שייע גלזר: 1 yellow (game 5)
        # טל בן חיים: 1 yellow (game 8)
        assert yellows.get("אבי נמני", 0) == 1
        assert yellows.get("שייע גלזר", 0) == 1

    def test_most_red_carded(self, maccabi_games):
        reds = dict(maccabi_games.players.most_red_carded)
        # שייע גלזר: straight red in game 2
        # טל בן חיים: second yellow in game 8 (counts as red)
        assert reds.get("שייע גלזר", 0) == 1
        assert reds.get("טל בן חיים", 0) == 1


class TestSubstitutions:
    def test_most_substitute_in(self, maccabi_games):
        sub_ins = dict(maccabi_games.players.most_substitute_in)
        # ערן זהבי: 3 sub ins (games 2, 5, 6)
        assert sub_ins["ערן זהבי"] == 3

    def test_most_substitute_off(self, maccabi_games):
        sub_offs = dict(maccabi_games.players.most_substitute_off)
        # חיים רביבו: 1 sub out (game 2)
        # גיורא שפיגל: 1 sub out (game 5)
        # אלי דריקס: 1 sub out (game 6)
        assert sub_offs.get("חיים רביבו", 0) == 1


class TestCaptains:
    def test_most_captains(self, maccabi_games):
        captains = dict(maccabi_games.players.most_captains)
        assert captains["אבי נמני"] == 10


class TestPenaltyStopped:
    def test_most_penalty_stopped(self, maccabi_games):
        stopped = dict(maccabi_games.players.most_penalty_stopped)
        # אלכסנדר אובארוב stops penalties in games 4 and 9
        assert stopped.get("אלכסנדר אובארוב", 0) == 2


class TestPenaltyMissed:
    def test_most_penalty_missed(self, maccabi_games):
        missed = dict(maccabi_games.players.most_penalty_missed)
        # אבי נמני misses penalties in games 3 and 6
        assert missed.get("אבי נמני", 0) == 2


class TestBestScorersInOneGame:
    def test_best_scorers_in_one_game_with_two_goals(self, maccabi_games):
        # score_at_least=2: אבי נמני scored 2 in game 1 (min 15, 70) and game 5 (min 50, 70)
        result = dict(maccabi_games.players.best_scorers_in_one_game(score_at_least=2))
        assert result["אבי נמני"] == 2

    def test_best_scorers_in_one_game_excludes_below_threshold(self, maccabi_games):
        # score_at_least=2: אלי דריקס scored 1 per game max, should not appear
        result = dict(maccabi_games.players.best_scorers_in_one_game(score_at_least=2))
        assert "אלי דריקס" not in result

    def test_best_scorers_in_one_game_no_results_for_high_threshold(self, maccabi_games):
        # No player scores 5+ in any fixture game
        result = maccabi_games.players.best_scorers_in_one_game(score_at_least=5)
        assert len(result) == 0

    def test_best_scorers_in_one_game_with_one_goal(self, maccabi_games):
        # score_at_least=1: אבי נמני scores in games 1,3,4,5,7,8 = 6; אלי דריקס in games 1,4 = 2
        result = dict(maccabi_games.players.best_scorers_in_one_game(score_at_least=1))
        assert result["אבי נמני"] == 6
        assert result["אלי דריקס"] == 2

    def test_best_scorers_in_one_game_excludes_own_goals(self):
        # Build a minimal game where שייע גלזר scores only an own goal — should not qualify
        import datetime
        from maccabistats.models.player_game_events import GoalTypes
        from maccabistats.models.team_in_game import TeamInGame
        from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats
        from game_fixtures import _player, _lineup, _goal, _game
        from players_data_fixtures import create_stub_players_data

        game = _game(
            competition="ליגת העל", fixture="מחזור1", season="2020/21",
            date=datetime.datetime(2020, 1, 1),
            stadium="בלומפילד", referee="ref",
            home_team=TeamInGame("מכבי תל אביב", "מאמן", 0, [
                _player("שייע גלזר", 5, [_lineup(), _goal(30, GoalTypes.OWN_GOAL)]),
            ]),
            away_team=TeamInGame("יריב", "מאמן", 1, [_player("שוער", 1, [_lineup()])]),
        )
        games = MaccabiGamesStats([game], players_data=create_stub_players_data())
        result = dict(games.players.best_scorers_in_one_game(score_at_least=1))
        assert "שייע גלזר" not in result

    def test_best_scorers_in_one_game_is_sorted(self, maccabi_games):
        # Result must be sorted descending by count (most_common contract)
        result = maccabi_games.players.best_scorers_in_one_game(score_at_least=2)
        assert result[0] == ("אבי נמני", 2)


class TestBestAssistersInOneGame:
    def test_best_assisters_in_one_game_with_two_assists(self, maccabi_games):
        # assist_at_least=2: חיים רביבו assisted 2 in games 1, 4, and 5
        result = dict(maccabi_games.players.best_assisters_in_one_game(assist_at_least=2))
        assert result["חיים רביבו"] == 3

    def test_best_assisters_in_one_game_excludes_below_threshold(self, maccabi_games):
        # assist_at_least=2: no other player has 2+ assists in one game
        result = dict(maccabi_games.players.best_assisters_in_one_game(assist_at_least=2))
        assert "אבי נמני" not in result

    def test_best_assisters_in_one_game_with_one_assist(self, maccabi_games):
        # assist_at_least=1: חיים רביבו assists in games 1,4,5,7,8 = 5 qualifying games
        result = dict(maccabi_games.players.best_assisters_in_one_game(assist_at_least=1))
        assert result["חיים רביבו"] == 5


class TestOwnGoals:
    def test_best_scorers_excludes_own_goals(self, maccabi_games):
        scorers = dict(maccabi_games.players.best_scorers)
        # Own goals by opponents (רפי לוי in game 5, פרי נויפלד in game 7) should not appear
        assert "רפי לוי" not in scorers
        assert "פרי נויפלד" not in scorers

    def test_best_scorers_by_own_goal(self, maccabi_games):
        own_goal_scorers = dict(maccabi_games.players.best_scorers_by_own_goal)
        # אבי נמני scored 8 real goals, 0 own goals
        assert own_goal_scorers.get("אבי נמני", 0) == 0


class TestGoalsAfterSubIn:
    def test_most_goals_after_sub_in(self, maccabi_games):
        goals_after_sub = dict(maccabi_games.players.most_goals_after_sub_in)
        # ערן זהבי scores after sub in in games 5 and 6
        assert goals_after_sub.get("ערן זהבי", 0) == 2


class TestPercentages:
    def test_most_winners_by_percentage(self, maccabi_games):
        result = maccabi_games.players.most_winners_by_percentage(minimum_games_played=5)
        # Filter for players with >= 5 games
        assert len(result) > 0
        # Each entry is (name, percentage, total_games)
        for entry in result:
            assert entry.total_games >= 5

    def test_never_lost(self, maccabi_games):
        never_lost = maccabi_games.players.never_lost(minimum_games_to_player=1)
        never_lost_names = {p[0] for p in never_lost}
        # אבי נמני lost 2 games, should NOT be in never_lost
        assert "אבי נמני" not in never_lost_names
