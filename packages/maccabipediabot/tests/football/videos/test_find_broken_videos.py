import requests
from datetime import date
from unittest.mock import Mock, patch

import pytest

from maccabipediabot.football.videos.find_broken_videos import BrokenVideo, format_report, _fetch_from_table


def test_format_report_header_contains_count():
    broken = [
        BrokenVideo(
            page_name='משחק:01-01-2001 מכבי תל אביב נגד בית"ר ירושלים - ליגת העל',
            url="https://www.youtube.com/watch?v=abc123",
            video_type="משחק מלא",
        )
    ]
    report = format_report(broken, date(2026, 4, 8))
    assert "נמצאו 1" in report
    assert "2026-04-08" in report


def test_format_report_includes_page_name_url_and_type():
    broken = [
        BrokenVideo(
            page_name='משחק:01-01-2001 מכבי תל אביב נגד בית"ר ירושלים - ליגת העל',
            url="https://www.youtube.com/watch?v=abc123",
            video_type="משחק מלא",
        )
    ]
    report = format_report(broken, date(2026, 4, 8))
    assert 'משחק:01-01-2001 מכבי תל אביב נגד בית"ר ירושלים - ליגת העל' in report
    assert "https://www.youtube.com/watch?v=abc123" in report
    assert "משחק מלא" in report


def test_format_report_groups_multiple_broken_under_same_page():
    broken = [
        BrokenVideo("משחק:01-01-2001 א נגד ב - ליגה", "https://youtu.be/1", "תקציר ראשי"),
        BrokenVideo("משחק:01-01-2001 א נגד ב - ליגה", "https://youtu.be/2", "תקציר משני"),
        BrokenVideo("משחק:02-02-2002 ג נגד ד - ליגה", "https://youtu.be/3", "משחק מלא"),
    ]
    report = format_report(broken, date(2026, 4, 8))
    assert "נמצאו 3" in report
    assert report.count("משחק:01-01-2001 א נגד ב - ליגה") == 1
    assert "https://youtu.be/1" in report
    assert "https://youtu.be/2" in report
    assert "https://youtu.be/3" in report


def test_fetch_from_table_returns_video_entries():
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = [
        {
            "_pageName": "משחק:01-01-2001 מכבי תל אביב נגד בית\"ר ירושלים - ליגת העל",
            "FullGame": "https://www.youtube.com/watch?v=abc",
            "Highlights": None,
            "Highlights2": None,
        }
    ]
    fields = {"FullGame": "משחק מלא", "Highlights": "תקציר ראשי", "Highlights2": "תקציר משני"}
    with patch(
        "maccabipediabot.football.videos.find_broken_videos.requests.get",
        return_value=mock_response,
    ):
        entries = _fetch_from_table("Games_Videos", fields)

    assert len(entries) == 1
    assert entries[0] == (
        "משחק:01-01-2001 מכבי תל אביב נגד בית\"ר ירושלים - ליגת העל",
        "https://www.youtube.com/watch?v=abc",
        "משחק מלא",
    )


def test_fetch_from_table_skips_null_urls():
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = [
        {"_pageName": "משחק:01-01-2001 א נגד ב - ליגה", "FullGame": None, "Highlights": None, "Highlights2": None}
    ]
    fields = {"FullGame": "משחק מלא", "Highlights": "תקציר ראשי", "Highlights2": "תקציר משני"}
    with patch(
        "maccabipediabot.football.videos.find_broken_videos.requests.get",
        return_value=mock_response,
    ):
        entries = _fetch_from_table("Games_Videos", fields)

    assert entries == []


def test_fetch_from_table_raises_on_http_error():
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500")
    with patch(
        "maccabipediabot.football.videos.find_broken_videos.requests.get",
        return_value=mock_response,
    ):
        with pytest.raises(requests.HTTPError):
            _fetch_from_table("Games_Videos", {"FullGame": "משחק מלא"})
