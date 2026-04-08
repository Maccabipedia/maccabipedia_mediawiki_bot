"""Validate that the synthetic fixture data is internally consistent.

Catches cases where TeamInGame.score diverges from actual goal events,
which would cause different stats modules to silently disagree.
"""
from maccabistats.models.player_game_events import GameEventTypes, GoalTypes


def test_score_matches_goal_events_for_non_technical_games(maccabi_games):
    """For non-technical games, the score field must match goal event counts."""
    for game in maccabi_games:
        if game.technical_result:
            continue

        # Count goals from events for each team
        maccabi_goal_events = sum(
            p.event_count_by_type(GameEventTypes.GOAL_SCORE)
            for p in game.maccabi_team.players
        )
        opponent_goal_events = sum(
            p.event_count_by_type(GameEventTypes.GOAL_SCORE)
            for p in game.not_maccabi_team.players
        )

        # Own goals by opponent count for maccabi and vice versa
        opponent_own_goals = sum(
            p.goals_count_by_goal_type(GoalTypes.OWN_GOAL)
            for p in game.not_maccabi_team.players
        )
        maccabi_own_goals = sum(
            p.goals_count_by_goal_type(GoalTypes.OWN_GOAL)
            for p in game.maccabi_team.players
        )

        expected_maccabi_score = maccabi_goal_events - maccabi_own_goals + opponent_own_goals
        expected_opponent_score = opponent_goal_events - opponent_own_goals + maccabi_own_goals

        assert game.maccabi_team.score == expected_maccabi_score, (
            f"{game}: maccabi score {game.maccabi_team.score} != "
            f"expected {expected_maccabi_score} from events"
        )
        assert game.not_maccabi_team.score == expected_opponent_score, (
            f"{game}: opponent score {game.not_maccabi_team.score} != "
            f"expected {expected_opponent_score} from events"
        )


def test_technical_result_game_has_no_goal_events(maccabi_games):
    """Technical result games should have score but no goal events (by fixture design)."""
    for game in maccabi_games:
        if not game.technical_result:
            continue
        maccabi_goals = sum(
            p.event_count_by_type(GameEventTypes.GOAL_SCORE)
            for p in game.maccabi_team.players
        )
        assert maccabi_goals == 0, (
            f"Technical game {game} has {maccabi_goals} goal events"
        )


def test_all_maccabi_games_have_lineup(maccabi_games):
    """Every non-technical game should have at least one lineup player."""
    for game in maccabi_games:
        lineup_count = len(game.maccabi_team.lineup_players)
        assert lineup_count > 0, f"{game}: no lineup players"
