from maccabipediabot.maintenance.videos.restore_deleted_football_video import (
    VIDEO_TYPE_TO_WIKI_FIELD,
    wiki_page_url,
)
from maccabipediabot.maintenance.videos.youtube.title import FULL_MATCH, HIGHLIGHTS


def test_wiki_page_url_encodes_hebrew_characters():
    title = "משחק:16-02-2009 הפועל תל אביב נגד מכבי תל אביב - גביע המדינה"
    url = wiki_page_url(title)
    assert url.startswith("https://www.maccabipedia.co.il/")
    # Underscore-separated and percent-encoded — ASCII-only so YouTube linkifies it.
    assert all(ord(c) < 128 for c in url)
    assert "%D7%9E%D7%A9%D7%97%D7%A7" in url  # the "משחק" namespace
    assert ":" in url  # namespace separator stayed literal


def test_wiki_page_url_preserves_colon_namespace_separator():
    assert wiki_page_url("משחק:foo") == "https://www.maccabipedia.co.il/" + "%D7%9E%D7%A9%D7%97%D7%A7" + ":foo"


def test_video_type_to_wiki_field_covers_both_types():
    assert VIDEO_TYPE_TO_WIKI_FIELD[FULL_MATCH] == "משחק מלא"
    assert VIDEO_TYPE_TO_WIKI_FIELD[HIGHLIGHTS] == "תקציר וידאו"
    assert set(VIDEO_TYPE_TO_WIKI_FIELD.keys()) == {FULL_MATCH, HIGHLIGHTS}
