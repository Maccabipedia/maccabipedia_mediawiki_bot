import pytest

from maccabipediabot.maintenance.videos.restore_deleted_football_video import (
    GameMetadata,
    VIDEO_TYPE_TO_WIKI_FIELD,
    parse_game_metadata,
    wiki_page_url,
)
from maccabipediabot.maintenance.videos.youtube.title import FULL_MATCH, HIGHLIGHTS


def _game_page_wikitext(**overrides: str) -> str:
    fields = {
        "עונה": "2018/19",
        "מפעל": "הליגה האירופית",
        "שלב במפעל": "סיבוב שלישי - משחק 2",
        "שם יריבה": "פיוניק",
        "תוצאת משחק מכבי": "2",
        "תוצאת משחק יריבה": "1",
    }
    fields.update(overrides)
    lines = "\n".join(f"|{k}={v}" for k, v in fields.items())
    return "{{קטלוג משחקים\n" + lines + "\n}}"


def test_parse_game_metadata_reads_all_fields_and_normalizes_season():
    result = parse_game_metadata(_game_page_wikitext(), page_title_hint="test")
    assert result == GameMetadata(
        season="2018-19",
        competition="הליגה האירופית",
        stage="סיבוב שלישי - משחק 2",
        opponent="פיוניק",
        maccabi_score=2,
        opponent_score=1,
    )


def test_parse_game_metadata_normalizes_season_with_dash_already():
    result = parse_game_metadata(_game_page_wikitext(**{"עונה": "2008-09"}), page_title_hint="test")
    assert result.season == "2008-09"


def test_parse_game_metadata_raises_when_template_missing():
    with pytest.raises(LookupError, match="Template"):
        parse_game_metadata("just some text with no template", page_title_hint="test")


def test_parse_game_metadata_raises_on_missing_required_field():
    wikitext = "{{קטלוג משחקים\n|עונה=2018/19\n|מפעל=הליגה האירופית\n}}"
    with pytest.raises(LookupError, match="שלב במפעל"):
        parse_game_metadata(wikitext, page_title_hint="test")


def test_parse_game_metadata_raises_on_empty_required_field():
    with pytest.raises(LookupError, match="שלב במפעל"):
        parse_game_metadata(_game_page_wikitext(**{"שלב במפעל": ""}), page_title_hint="test")


def test_parse_game_metadata_handles_whitespace_around_values():
    wikitext = _game_page_wikitext(**{"שם יריבה": "  פיוניק  "})
    assert parse_game_metadata(wikitext, page_title_hint="test").opponent == "פיוניק"


def test_wiki_page_url_encodes_hebrew_characters():
    title = "משחק:16-02-2009 הפועל תל אביב נגד מכבי תל אביב - גביע המדינה"
    url = wiki_page_url(title)
    assert url.startswith("https://www.maccabipedia.co.il/")
    assert all(ord(c) < 128 for c in url)
    assert "%D7%9E%D7%A9%D7%97%D7%A7" in url
    assert ":" in url


def test_wiki_page_url_preserves_colon_namespace_separator():
    assert wiki_page_url("משחק:foo") == "https://www.maccabipedia.co.il/" + "%D7%9E%D7%A9%D7%97%D7%A7" + ":foo"


def test_video_type_to_wiki_field_covers_both_types():
    assert VIDEO_TYPE_TO_WIKI_FIELD[FULL_MATCH] == "משחק מלא"
    assert VIDEO_TYPE_TO_WIKI_FIELD[HIGHLIGHTS] == "תקציר וידאו"
    assert set(VIDEO_TYPE_TO_WIKI_FIELD.keys()) == {FULL_MATCH, HIGHLIGHTS}
