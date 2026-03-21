from datetime import timedelta

import pytest

from maccabistats_player_event import PlayerEvent


# ---------------------------------------------------------------------------
# from_maccabipedia_format — parsing
# ---------------------------------------------------------------------------

def test_parse_basic_goal():
    event = PlayerEvent.from_maccabipedia_format("יוסי כהן::10::גול::45::מכבי")
    assert event.name == "יוסי כהן"
    assert event.number == "10"
    assert event.event_type == "גול"
    assert event.sub_event_type is None
    assert event.minute_occur == 45
    assert event.maccabi_player is True
    assert event.team == "מכבי"


def test_parse_opponent_event():
    event = PlayerEvent.from_maccabipedia_format("שחקן יריב::7::כרטיס צהוב::30::יריבה")
    assert event.maccabi_player is False
    assert event.team == "יריבה"


def test_parse_event_with_sub_event():
    event = PlayerEvent.from_maccabipedia_format("יוסי כהן::10::גול-פנדל::45::מכבי")
    assert event.event_type == "גול"
    assert event.sub_event_type == "פנדל"


def test_parse_event_with_game_part():
    event = PlayerEvent.from_maccabipedia_format("יוסי כהן::10::גול::45::מכבי::מחצית שניה")
    assert event.game_part == "מחצית שניה"


def test_parse_no_game_part_is_none():
    event = PlayerEvent.from_maccabipedia_format("יוסי כהן::10::גול::45::מכבי")
    assert event.game_part is None


def test_parse_no_number_uses_sentinel():
    event = PlayerEvent.from_maccabipedia_format("יוסי כהן::אין-מספר::הרכב::0::מכבי")
    assert event.number == "אין-מספר"


def test_parse_invalid_format_raises():
    with pytest.raises(TypeError):
        PlayerEvent.from_maccabipedia_format("שם בלבד")


# ---------------------------------------------------------------------------
# __maccabipedia__ — serialization
# ---------------------------------------------------------------------------

def test_serialize_no_sub_event():
    event = PlayerEvent("יוסי כהן", "10", timedelta(minutes=45), "גול", None, True)
    assert event.__maccabipedia__() == "יוסי כהן::10::גול::45::מכבי\n"


def test_serialize_with_sub_event():
    event = PlayerEvent("יוסי כהן", "10", timedelta(minutes=45), "גול", "פנדל", True)
    assert event.__maccabipedia__() == "יוסי כהן::10::גול-פנדל::45::מכבי\n"


def test_serialize_opponent():
    event = PlayerEvent("שחקן יריב", "7", timedelta(minutes=30), "כרטיס צהוב", None, False)
    assert event.__maccabipedia__() == "שחקן יריב::7::כרטיס צהוב::30::יריבה\n"


def test_serialize_with_game_part():
    event = PlayerEvent("יוסי כהן", "10", timedelta(minutes=45), "גול", None, True, game_part="מחצית שניה")
    assert event.__maccabipedia__() == "יוסי כהן::10::גול::45::מכבי::מחצית שניה\n"


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

def test_roundtrip_simple():
    original = "יוסי כהן::10::גול::45::מכבי"
    assert PlayerEvent.from_maccabipedia_format(original).__maccabipedia__().strip("\n") == original


def test_roundtrip_with_sub_event():
    original = "יוסי כהן::10::גול-פנדל::45::מכבי"
    assert PlayerEvent.from_maccabipedia_format(original).__maccabipedia__().strip("\n") == original


def test_roundtrip_with_game_part():
    original = "יוסי כהן::10::גול::45::מכבי::מחצית שניה"
    assert PlayerEvent.from_maccabipedia_format(original).__maccabipedia__().strip("\n") == original


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_maccabi_squad_before_opponent_squad():
    maccabi = PlayerEvent("מכבי", "1", timedelta(0), "הרכב", None, True)
    opponent = PlayerEvent("יריב", "1", timedelta(0), "הרכב", None, False)
    assert maccabi < opponent


def test_cards_sorted_by_minute():
    earlier = PlayerEvent("שחקן א", "5", timedelta(minutes=30), "כרטיס צהוב", None, True)
    later = PlayerEvent("שחקן ב", "8", timedelta(minutes=60), "כרטיס צהוב", None, True)
    assert earlier < later


def test_goals_sorted_by_minute():
    earlier = PlayerEvent("שחקן א", "5", timedelta(minutes=20), "גול", None, True)
    later = PlayerEvent("שחקן ב", "8", timedelta(minutes=80), "גול", None, True)
    assert earlier < later
