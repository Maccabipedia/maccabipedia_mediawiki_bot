"""Tests for the unified basketball translations module."""
from datetime import datetime

from maccabipediabot.basketball.translations import (
    basket_co_il_competition_name,
    canonical_team_name,
    normalize_player_name,
    person_name_to_hebrew,
    stadium_name_to_hebrew,
    team_name_to_hebrew,
)


def test_team_name_to_hebrew_known_team():
    assert team_name_to_hebrew("Maccabi Tel-Aviv") == "מכבי תל אביב"


def test_team_name_to_hebrew_unknown_passes_through():
    assert team_name_to_hebrew("New Team Never Seen") == "New Team Never Seen"


def test_person_name_to_hebrew_known_player():
    assert person_name_to_hebrew("Wade Baldwin Iv") == "ווייד בולדווין"


def test_person_name_to_hebrew_unknown_passes_through():
    assert person_name_to_hebrew("Some Unknown Coach") == "Some Unknown Coach"


def test_stadium_name_to_hebrew_known():
    assert stadium_name_to_hebrew("MENORA MIVTACHIM ARENA") == "היכל מנורה מבטחים"


def test_stadium_name_to_hebrew_unknown_passes_through():
    assert stadium_name_to_hebrew("Some New Arena") == "Some New Arena"


def test_normalize_player_name_lundberg():
    assert normalize_player_name("גבריאל ''איפה'' לונדברג") == "איפה לונדברג"


def test_normalize_player_name_unknown_passes_through():
    assert normalize_player_name("טל ברודי") == "טל ברודי"


def test_basket_co_il_competition_name_super_league():
    assert basket_co_il_competition_name(5) == "ליגת העל"


def test_basket_co_il_competition_name_super_cup():
    assert basket_co_il_competition_name(34) == "הסופרקאפ הישראלי"


def test_basket_co_il_competition_name_unknown_returns_none():
    assert basket_co_il_competition_name(999) is None


def test_canonical_team_name_simple_rename():
    assert canonical_team_name("מכבי אלקטרה", datetime(2010, 5, 1)) == "מכבי תל אביב"


def test_canonical_team_name_no_rename_known_pass_through():
    assert canonical_team_name("הפועל ירושלים", datetime(2024, 1, 1)) == "הפועל ירושלים"


def test_canonical_team_name_year_range_pre_2005():
    # מכבי רמת עמידר → "מכבי רמת עמידר" (1957–2005) then "הכח עמידר רמת גן" (2005+)
    assert canonical_team_name("מכבי רמת עמידר", datetime(2000, 6, 1)) == "מכבי רמת עמידר"


def test_canonical_team_name_year_range_post_2005():
    assert canonical_team_name("מכבי רמת עמידר", datetime(2010, 6, 1)) == "הכח עמידר רמת גן"


def test_canonical_team_name_unknown_passes_through():
    assert canonical_team_name("שם לא ידוע", datetime(2024, 1, 1)) == "שם לא ידוע"


def test_person_lookup_handles_trailing_space_in_source_dict():
    """Some TS-source map keys had trailing spaces (e.g. "Sergio Llull "). Lookups
    using a trimmed or doubly-spaced name must still resolve."""
    assert person_name_to_hebrew("Sergio Llull") == "סרחיו יוי"
    assert person_name_to_hebrew("  Sergio   Llull  ") == "סרחיו יוי"
    assert person_name_to_hebrew("Andres Feliz") != "Andres Feliz"  # was "Andres Feliz " in source
    assert person_name_to_hebrew("Alex Len") != "Alex Len"
