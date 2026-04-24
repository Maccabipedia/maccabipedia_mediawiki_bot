from maccabipediabot.maintenance.videos.youtube.title import (
    FULL_MATCH,
    HIGHLIGHTS,
    format_video_title,
    season_playlist_title,
)


def test_format_highlights_with_loss_reverses_score_for_bidi():
    # Maccabi TA lost 0-2 at Hapoel TA, State Cup round 9, 16-02-2009.
    title = format_video_title(
        season="2008-09",
        competition="גביע המדינה",
        round_name="סיבוב ט",
        maccabi_score=0,
        opponent="הפועל תל אביב",
        opponent_score=2,
        video_type=HIGHLIGHTS,
    )
    assert title == (
        "עונת 2008-09 גביע המדינה סיבוב ט "
        "מכבי תל אביב - הפועל תל אביב (2-0) תקציר"
    )


def test_format_full_match_with_win():
    # 1995-96 championship-clinching win vs Beitar: Maccabi TA 3-1 Beitar Jerusalem.
    title = format_video_title(
        season="1995-96",
        competition="ליגה לאומית",
        round_name="מחזור 34",
        maccabi_score=3,
        opponent="ביתר ירושלים",
        opponent_score=1,
        video_type=FULL_MATCH,
    )
    assert title == (
        "עונת 1995-96 ליגה לאומית מחזור 34 "
        "מכבי תל אביב - ביתר ירושלים (1-3) משחק מלא"
    )


def test_format_score_is_stored_opponent_first_for_bidi():
    # Explicit non-palindrome check: Maccabi 3, Ajax 2 must appear as "(2-3)" in storage
    # so the BIDI renderer flips it to "(3-2)" visually — Hebrew readers see Maccabi=3.
    title = format_video_title(
        season="2004-05",
        competition="ליגת האלופות",
        round_name="שלב הבתים - מחזור 4",
        maccabi_score=3,
        opponent="אייאקס אמסטרדם",
        opponent_score=2,
        video_type=FULL_MATCH,
    )
    assert "(2-3)" in title
    assert "(3-2)" not in title


def test_season_playlist_title():
    assert season_playlist_title("2008-09") == "מכביפדיה | עונת 2008/09"
    assert season_playlist_title("1999-00") == "מכביפדיה | עונת 1999/00"
