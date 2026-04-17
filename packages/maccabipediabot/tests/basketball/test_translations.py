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
