"""Tests for MaccabiGamesRefereesStats."""


class TestRefereesStats:
    def test_most_judged_referee(self, maccabi_games):
        judged = dict(maccabi_games.referees.most_judged_referee)
        assert judged["יורם דוידוביץ"] == 4
        assert judged["אלי חקמון"] == 3
        assert judged["רועי ריינשרייבר"] == 2
        assert judged["גל לייבוביץ"] == 1

    def test_best_referee(self, maccabi_games):
        best = dict(maccabi_games.referees.best_referee)
        # יורם דוידוביץ: games 1(W),3(T),7(W),10(W) = 3 wins
        assert best["יורם דוידוביץ"] == 3

    def test_worst_referee(self, maccabi_games):
        worst = dict(maccabi_games.referees.worst_referee)
        # אלי חקמון: games 2(L),5(W),8(L) = 2 losses
        assert worst["אלי חקמון"] == 2

    def test_best_referee_by_percentage(self, maccabi_games):
        result = dict(maccabi_games.referees.best_referee_by_percentage)
        # גל לייבוביץ: 1 game, 1 win = 100%
        assert result["גל לייבוביץ - 1"] == 100.0
        # יורם דוידוביץ: 4 games, 3 wins = 75%
        assert result["יורם דוידוביץ - 4"] == 75.0

    def test_worst_referee_by_percentage(self, maccabi_games):
        result = dict(maccabi_games.referees.worst_referee_by_percentage)
        # אלי חקמון: 3 games, 2 losses = 66.67%
        assert result["אלי חקמון - 3"] == 66.67
