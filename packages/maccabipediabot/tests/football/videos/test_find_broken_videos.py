import requests
from datetime import date
from unittest.mock import Mock, patch

import pytest

from maccabipediabot.football.videos.find_broken_videos import BrokenVideo, format_report


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
