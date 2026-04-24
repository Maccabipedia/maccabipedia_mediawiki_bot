"""Upload a backup video to MaccabiPedia's YouTube channel and add it to a season playlist.

This is the YouTube-only step. For the full pipeline (upload + wiki page update) use
`restore_deleted_football_video`.
"""
import argparse
import logging
from pathlib import Path

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.maintenance.videos.youtube.client import (
    add_video_to_playlist,
    ensure_playlist,
    upload_video,
    youtube_client,
)

logger = logging.getLogger(__name__)


def upload_and_add_to_playlist(video_path: Path, title: str, playlist_title: str, description: str) -> str:
    youtube = youtube_client()
    playlist_id = ensure_playlist(youtube, playlist_title)
    video_id = upload_video(youtube, video_path, title, description)
    add_video_to_playlist(youtube, playlist_id, video_id)
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Path to video file")
    parser.add_argument("--title", required=True, help="Video title (use title.format_video_title)")
    parser.add_argument("--playlist", required=True, help="Playlist title, e.g. 'מכביפדיה | עונת 2008/09'")
    parser.add_argument("--description", required=True, help="Description (typically the URL-encoded wiki page URL)")
    args = parser.parse_args()

    setup_logging(level=logging.INFO)
    video_path = Path(args.file)
    if not video_path.is_file():
        raise SystemExit(f"File not found: {video_path}")

    video_id = upload_and_add_to_playlist(video_path, args.title, args.playlist, args.description)
    logger.info("Uploaded https://www.youtube.com/watch?v=%s", video_id)


if __name__ == "__main__":
    main()
