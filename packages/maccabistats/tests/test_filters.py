"""Tests for MaccabiGamesStats filtering methods."""
import datetime


class TestCompetitionFilters:
    def test_league_games(self, maccabi_games):
        league = maccabi_games.league_games
        assert len(league) == 8
        assert all(g.competition == "ליגת העל" for g in league)

    def test_trophy_games(self, maccabi_games):
        trophy = maccabi_games.trophy_games
        assert len(trophy) == 1
        assert trophy.games[0].competition == "גביע המדינה"

    def test_official_games(self, maccabi_games):
        official = maccabi_games.official_games
        assert len(official) == 9  # all except friendly

    def test_non_official_games(self, maccabi_games):
        non_official = maccabi_games.non_official_games
        assert len(non_official) == 1
        assert non_official.games[0].competition == "ידידות"

    def test_get_games_by_competition(self, maccabi_games):
        cup = maccabi_games.get_games_by_competition("גביע המדינה")
        assert len(cup) == 1

    def test_get_games_by_competition__list(self, maccabi_games):
        both = maccabi_games.get_games_by_competition(["ליגת העל", "גביע המדינה"])
        assert len(both) == 9


class TestHomeAwayFilters:
    def test_home_games(self, maccabi_games):
        home = maccabi_games.home_games
        assert len(home) == 7

    def test_away_games(self, maccabi_games):
        away = maccabi_games.away_games
        assert len(away) == 3


class TestResultFilters:
    def test_maccabi_wins(self, maccabi_games):
        assert len(maccabi_games.maccabi_wins) == 6

    def test_maccabi_losses(self, maccabi_games):
        assert len(maccabi_games.maccabi_losses) == 2

    def test_maccabi_ties(self, maccabi_games):
        assert len(maccabi_games.maccabi_ties) == 2

    def test_technical_result_games(self, maccabi_games):
        assert len(maccabi_games.technical_result_games) == 1


class TestTeamFilter:
    def test_get_games_against_team(self, maccabi_games):
        vs_haifa = maccabi_games.get_games_against_team("מכבי חיפה")
        assert len(vs_haifa) == 3

    def test_get_games_against_team__beer_sheva(self, maccabi_games):
        vs_bs = maccabi_games.get_games_against_team("הפועל באר שבע")
        assert len(vs_bs) == 2


class TestDateFilters:
    def test_played_before(self, maccabi_games):
        before = maccabi_games.played_before(datetime.datetime(2020, 1, 1))
        assert len(before) == 5

    def test_played_after(self, maccabi_games):
        after = maccabi_games.played_after(datetime.datetime(2020, 9, 1))
        assert len(after) == 4

    def test_played_at__string(self, maccabi_games):
        at = maccabi_games.played_at("14-09-2019")
        assert len(at) == 1

    def test_first_game_date(self, maccabi_games):
        assert maccabi_games.first_game_date == "14-09-2019"

    def test_last_game_date(self, maccabi_games):
        assert maccabi_games.last_game_date == "07-11-2020"


class TestPlayerCoachSeasonFilters:
    def test_get_games_by_coach(self, maccabi_games):
        coach_a = maccabi_games.get_games_by_coach("אברם גרנט")
        assert len(coach_a) == 6

    def test_get_games_by_referee(self, maccabi_games):
        ref_a = maccabi_games.get_games_by_referee("יורם דוידוביץ")
        assert len(ref_a) == 4

    def test_get_games_by_season(self, maccabi_games):
        s1 = maccabi_games.get_games_by_season("2019/20")
        assert len(s1) == 6

    def test_get_games_by_player_name(self, maccabi_games):
        # אבי נמני plays in all 10 games
        games = maccabi_games.get_games_by_player_name("אבי נמני")
        assert len(games) == 10

    def test_get_games_by_played_player_name(self, maccabi_games):
        # ערן זהבי plays (sub in) in games 2, 5, 6
        games = maccabi_games.get_games_by_played_player_name("ערן זהבי")
        assert len(games) == 3

    def test_get_games_by_stadium(self, maccabi_games):
        bloomfield = maccabi_games.get_games_by_stadium("בלומפילד")
        assert len(bloomfield) == 7

    def test_get_games_by_day_at_month(self, maccabi_games):
        # Game 1 is on Sept 14
        games = maccabi_games.get_games_by_day_at_month(14, 9)
        assert len(games) == 1


class TestAvailableProperties:
    def test_available_competitions(self, maccabi_games):
        assert set(maccabi_games.available_competitions) == {"ליגת העל", "גביע המדינה", "ידידות"}

    def test_available_opponents(self, maccabi_games):
        assert len(maccabi_games.available_opponents) == 5

    def test_available_stadiums(self, maccabi_games):
        assert "בלומפילד" in maccabi_games.available_stadiums

    def test_available_players_names(self, maccabi_games):
        names = maccabi_games.available_players_names
        assert "אבי נמני" in names

    def test_available_referees(self, maccabi_games):
        assert len(maccabi_games.available_referees) == 4

    def test_available_coaches(self, maccabi_games):
        assert set(maccabi_games.available_coaches) == {"אברם גרנט", "פאולו סוזה"}

    def test_available_seasons(self, maccabi_games):
        assert maccabi_games.available_seasons == ["2019/20", "2020/21"]


class TestMaccabiGamesStatsBasics:
    def test_len(self, maccabi_games):
        assert len(maccabi_games) == 10

    def test_getitem(self, maccabi_games):
        game = maccabi_games[0]
        assert game.competition == "ליגת העל"

    def test_iter(self, maccabi_games):
        games = list(maccabi_games)
        assert len(games) == 10

    def test_repr(self, maccabi_games):
        r = repr(maccabi_games)
        assert "10 games" in r

    def test_description_chaining(self, maccabi_games):
        filtered = maccabi_games.home_games.maccabi_wins
        assert "Home games" in filtered.description
        assert "Wins only" in filtered.description

    def test_played_games_by_player_name(self, maccabi_games):
        by_player = maccabi_games.played_games_by_player_name()
        assert len(by_player["אבי נמני"]) == 10
        assert len(by_player["ערן זהבי"]) == 3
        # Unknown player returns empty
        assert len(by_player["unknown"]) == 0
