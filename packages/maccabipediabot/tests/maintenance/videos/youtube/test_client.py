"""Tests for the runtime guards in `youtube/client.py` that were added in the PR
review-fix pass (pagination safety cap; playlist-insert response verification).
Without these, a future cleanup could silently remove the guards as paranoia.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from maccabipediabot.maintenance.videos.youtube.client import (
    add_video_to_playlist,
    find_playlist_id,
)


class _PaginatedPlaylists:
    """Fake youtube.playlists() resource that always returns `nextPageToken`.

    Used to exercise the safety-cap branch in `find_playlist_id` (a misbehaving or
    unbounded API shouldn't hang the caller).
    """

    def __init__(self) -> None:
        self.calls = 0

    def playlists(self):  # matches google-api-python-client's chained API
        return self

    def list(self, **_kwargs: Any):
        return self

    def execute(self) -> dict[str, Any]:
        self.calls += 1
        return {
            "items": [{"snippet": {"title": f"fake-{self.calls}"}, "id": f"id-{self.calls}"}],
            "nextPageToken": "always-more",
        }


def test_find_playlist_id_caps_pagination_at_20_pages():
    fake = _PaginatedPlaylists()
    with pytest.raises(RuntimeError, match="exceeded 20 pages"):
        find_playlist_id(fake, "title-that-never-matches")
    assert fake.calls == 20


def test_find_playlist_id_returns_match_without_full_sweep():
    fake = Mock()
    fake.playlists.return_value.list.return_value.execute.return_value = {
        "items": [
            {"snippet": {"title": "other"}, "id": "pl-other"},
            {"snippet": {"title": "target"}, "id": "pl-target"},
        ],
    }
    assert find_playlist_id(fake, "target") == "pl-target"


def test_find_playlist_id_returns_none_when_channel_has_no_match():
    fake = Mock()
    fake.playlists.return_value.list.return_value.execute.return_value = {
        "items": [{"snippet": {"title": "unrelated"}, "id": "pl-1"}],
    }
    assert find_playlist_id(fake, "missing") is None


def test_add_video_to_playlist_raises_when_response_ids_mismatch():
    fake = Mock()
    # Response for a DIFFERENT video — simulates silent no-op / wrong write target.
    fake.playlistItems.return_value.insert.return_value.execute.return_value = {
        "snippet": {
            "playlistId": "wrong-playlist",
            "resourceId": {"kind": "youtube#video", "videoId": "wrong-video"},
        }
    }
    with pytest.raises(RuntimeError, match="unexpected response"):
        add_video_to_playlist(fake, playlist_id="expected-playlist", video_id="expected-video")


def test_add_video_to_playlist_succeeds_when_response_matches():
    fake = Mock()
    fake.playlistItems.return_value.insert.return_value.execute.return_value = {
        "snippet": {
            "playlistId": "the-playlist",
            "resourceId": {"kind": "youtube#video", "videoId": "the-video"},
        }
    }
    add_video_to_playlist(fake, playlist_id="the-playlist", video_id="the-video")
