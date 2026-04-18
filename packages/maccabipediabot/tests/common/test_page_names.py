from datetime import date

from maccabipediabot.common.page_names import build_game_page_name


def test_build_game_page_name_formats_hebrew_string():
    result = build_game_page_name(
        prefix='משחק',
        game_date=date(1977, 5, 14),
        home_team='מכבי תל אביב',
        away_team='הפועל תל אביב',
        competition='ליגת העל',
    )
    assert result == 'משחק:14-05-1977 מכבי תל אביב נגד הפועל תל אביב - ליגת העל'


def test_build_game_page_name_respects_sport_prefix():
    result = build_game_page_name(
        prefix='כדורסל',
        game_date=date(2004, 4, 29),
        home_team='מכבי תל אביב',
        away_team='סקאליני בולוניה',
        competition='יורוליג',
    )
    assert result.startswith('כדורסל:29-04-2004 ')
