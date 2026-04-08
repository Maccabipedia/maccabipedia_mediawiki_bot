"""Tests for GameData, TeamInGame, and PlayerInGame model properties."""
import datetime
from datetime import timedelta

from maccabistats.models.player_game_events import GameEventTypes, GoalTypes


class TestGameData:
    def test_is_maccabi_home_team__home_game(self, maccabi_games):
        game = maccabi_games.games[0]  # Game 1: Maccabi home
        assert game.is_maccabi_home_team is True

    def test_is_maccabi_home_team__away_game(self, maccabi_games):
        game = maccabi_games.games[1]  # Game 2: Maccabi away
        assert game.is_maccabi_home_team is False

    def test_maccabi_team__returns_correct_team(self, maccabi_games):
        game = maccabi_games.games[1]  # away game
        assert game.maccabi_team.name == "מכבי תל אביב"
        assert game.not_maccabi_team.name == 'בית"ר ירושלים'

    def test_maccabi_score(self, maccabi_games):
        assert maccabi_games.games[0].maccabi_score == 3

    def test_maccabi_score_diff__win(self, maccabi_games):
        assert maccabi_games.games[0].maccabi_score_diff == 2

    def test_maccabi_score_diff__loss(self, maccabi_games):
        assert maccabi_games.games[1].maccabi_score_diff == -2

    def test_maccabi_score_diff__tie(self, maccabi_games):
        assert maccabi_games.games[2].maccabi_score_diff == 0

    def test_is_maccabi_win(self, maccabi_games):
        assert maccabi_games.games[0].is_maccabi_win is True
        assert maccabi_games.games[1].is_maccabi_win is False
        assert maccabi_games.games[2].is_maccabi_win is False

    def test_technical_result(self, maccabi_games):
        assert maccabi_games.games[9].technical_result is True
        assert maccabi_games.games[0].technical_result is False

    def test_date_resolution_strips_time(self, maccabi_games):
        game = maccabi_games.games[0]
        assert game.date.hour == 0
        assert game.date.minute == 0
        assert game.date.second == 0

    def test_season(self, maccabi_games):
        assert maccabi_games.games[0].season == "2019/20"
        assert maccabi_games.games[6].season == "2020/21"

    def test_goals__returns_ordered_goal_events_with_running_score(self, maccabi_games):
        game = maccabi_games.games[0]  # 3-1 win
        goals = game.goals()
        assert len(goals) == 4
        # Goals should be ordered by time
        times = [g['time_occur'] for g in goals]
        assert times == sorted(times)

    def test_league_fixture__parses_number(self, maccabi_games):
        assert maccabi_games.games[0].league_fixture == 1

    def test_league_fixture__non_league_returns_none(self, maccabi_games):
        assert maccabi_games.games[3].league_fixture is None  # Cup game

    def test_played_before_and_after(self, maccabi_games):
        game = maccabi_games.games[0]  # 2019-09-14
        assert game.played_before(datetime.datetime(2020, 1, 1)) is True
        assert game.played_after(datetime.datetime(2019, 1, 1)) is True
        assert game.played_before(datetime.datetime(2019, 1, 1)) is False

    def test_json_dict(self, maccabi_games):
        d = maccabi_games.games[0].json_dict()
        assert d['competition'] == "ליגת העל"
        assert d['home_team']['name'] == "מכבי תל אביב"
        assert d['away_team']['score'] == 1


class TestTeamInGame:
    def test_lineup_players(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team
        assert len(team.lineup_players) == 11

    def test_played_players__includes_subs(self, maccabi_games):
        team = maccabi_games.games[4].maccabi_team  # Game 5: has a sub
        played = team.played_players
        played_names = {p.name for p in played}
        assert "שחקן_יב" in played_names  # sub in player

    def test_players_from_bench(self, maccabi_games):
        team = maccabi_games.games[4].maccabi_team
        bench = team.players_from_bench
        assert len(bench) == 1
        assert bench[0].name == "שחקן_יב"

    def test_scored_players(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team  # Game 1: שחקן_א and שחקן_ב score
        scorers = {p.name for p in team.scored_players}
        assert scorers == {"שחקן_א", "שחקן_ב"}

    def test_lineup_count_with_benched_player(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team  # Game 1 has 11 lineup + 1 benched
        assert len(team.lineup_players) == 11
        assert len(team.players) == 12  # includes benched

    def test_assist_players(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team
        assisters = {p.name for p in team.assist_players}
        assert assisters == {"שחקן_ג"}

    def test_yellow_carded_players(self, maccabi_games):
        team = maccabi_games.games[1].maccabi_team  # Game 2: שחקן_א gets yellow
        assert len(team.yellow_carded_players) == 1
        assert team.yellow_carded_players[0].name == "שחקן_א"

    def test_red_carded_players__straight_red(self, maccabi_games):
        team = maccabi_games.games[1].maccabi_team  # Game 2: שחקן_ו gets straight red
        red = team.red_carded_players
        assert len(red) == 1
        assert red[0].name == "שחקן_ו"

    def test_red_carded_players__second_yellow(self, maccabi_games):
        team = maccabi_games.games[7].maccabi_team  # Game 8: שחקן_ד gets 2nd yellow
        red = team.red_carded_players
        assert len(red) == 1
        assert red[0].name == "שחקן_ד"

    def test_not_played_players__benched(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team  # Game 1: שחקן_יג is benched
        not_played = team.not_played_players
        benched_names = {p.name for p in not_played}
        assert "שחקן_יג" in benched_names

    def test_captain(self, maccabi_games):
        team = maccabi_games.games[0].maccabi_team
        assert team.captain.name == "שחקן_א"

    def test_has_goal_from_bench(self, maccabi_games):
        assert maccabi_games.games[5].maccabi_team.has_goal_from_bench is True  # Game 6
        assert maccabi_games.games[0].maccabi_team.has_goal_from_bench is False


class TestPlayerInGame:
    def test_played_in_game__lineup(self, maccabi_games):
        player = maccabi_games.games[0].maccabi_team.players[0]
        assert player.played_in_game is True

    def test_played_in_game__sub_in(self, maccabi_games):
        # Game 2: שחקן_יב comes on as sub
        team = maccabi_games.games[1].maccabi_team
        sub_player = [p for p in team.players if p.name == "שחקן_יב"][0]
        assert sub_player.played_in_game is True

    def test_scored(self, maccabi_games):
        player = maccabi_games.games[0].maccabi_team.players[0]  # שחקן_א scored
        assert player.scored is True

    def test_scored_after_sub_in(self, maccabi_games):
        # Game 6: שחקן_יב subs in at 70, scores at 85
        team = maccabi_games.games[5].maccabi_team
        sub_player = [p for p in team.players if p.name == "שחקן_יב"][0]
        assert sub_player.scored_after_sub_in is True

    def test_event_count_by_type(self, maccabi_games):
        player = maccabi_games.games[0].maccabi_team.players[0]  # 2 goals
        assert player.event_count_by_type(GameEventTypes.GOAL_SCORE) == 2

    def test_goals_count_by_goal_type(self, maccabi_games):
        player = maccabi_games.games[2].maccabi_team.players[0]  # penalty goal
        assert player.goals_count_by_goal_type(GoalTypes.PENALTY) == 1

    def test_get_as_normal_player(self, maccabi_games):
        player_in_game = maccabi_games.games[0].maccabi_team.players[0]
        normal = player_in_game.get_as_normal_player()
        assert normal.name == player_in_game.name
        assert normal.number == player_in_game.number
        assert not hasattr(normal, 'events') or not isinstance(normal.events, list) if hasattr(normal, 'events') else True
