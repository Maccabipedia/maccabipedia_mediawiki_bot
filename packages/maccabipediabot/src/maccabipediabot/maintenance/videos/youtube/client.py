import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from maccabipediabot.maintenance.videos.youtube.auth import TOKEN_FILE

logger = logging.getLogger(__name__)

SPORTS_CATEGORY_ID = "17"
MACCABIPEDIA_CHANNEL_ID = "UCxnAYpW-2OJUXbrSil5EeQQ"

# Python's `mimetypes` misidentifies video extensions that share a suffix with
# non-video formats (`.ts` → Qt Linguist, `.flv` sometimes missing). Override.
_VIDEO_MIMETYPES = {
    ".ts": "video/mp2t",
    ".m2ts": "video/mp2t",
    ".mts": "video/mp2t",
    ".flv": "video/x-flv",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
}


def youtube_client():
    if not TOKEN_FILE.is_file():
        raise SystemExit(
            f"YouTube OAuth token not found at {TOKEN_FILE}. Run "
            f"`uv run python -m maccabipediabot.maintenance.videos.youtube.auth` first."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())
    client = build("youtube", "v3", credentials=creds)
    _verify_bound_to_maccabipedia(client)
    return client


def _verify_bound_to_maccabipedia(youtube) -> None:
    """Fail fast if the token authorizes some account other than @MaccabiPedia.

    This catches the brand-account pitfall: a personal Google account can authenticate
    successfully but not own any channel, or own a different one. Without this check
    a mis-scoped token silently creates duplicate playlists under the wrong channel.
    """
    resp = youtube.channels().list(part="id", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise SystemExit(
            "Authenticated Google account owns no YouTube channel. Re-run auth and pick "
            "the MaccabiPedia brand account on the consent screen."
        )
    channel_id = items[0]["id"]
    if channel_id != MACCABIPEDIA_CHANNEL_ID:
        raise SystemExit(
            f"Token is bound to channel {channel_id}, not MaccabiPedia "
            f"({MACCABIPEDIA_CHANNEL_ID}). Re-run auth and pick MaccabiPedia."
        )


def find_playlist_id(youtube, title: str) -> str | None:
    # The MaccabiPedia channel has ~30 playlists today, max ~200 realistically. Cap
    # the paginated sweep at 20 pages (1000 playlists) so a misbehaving API can't hang.
    next_page_token = None
    max_pages = 20
    for _ in range(max_pages):
        resp = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=next_page_token,
        ).execute()
        for item in resp.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        next_page_token = resp.get("nextPageToken")
        if not next_page_token:
            return None
    raise RuntimeError(
        f"find_playlist_id: exceeded {max_pages} pages while searching for '{title}'. "
        f"Channel has more playlists than the safety cap expects — bump max_pages."
    )


def create_playlist(youtube, title: str) -> str:
    resp = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title},
            "status": {"privacyStatus": "public"},
        },
    ).execute()
    return resp["id"]


def ensure_playlist(youtube, title: str) -> str:
    existing = find_playlist_id(youtube, title)
    if existing:
        return existing
    return create_playlist(youtube, title)


def upload_video(youtube, video_path: Path, title: str, description: str = "") -> str:
    mimetype = _VIDEO_MIMETYPES.get(video_path.suffix.lower())
    media = MediaFileUpload(str(video_path), resumable=True, mimetype=mimetype)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": SPORTS_CATEGORY_ID,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info("Uploading... %d%%", int(status.progress() * 100))
    return response["id"]


def add_video_to_playlist(youtube, playlist_id: str, video_id: str) -> None:
    resp = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }
        },
    ).execute()
    # Guard against silent insert failure (e.g. deleted/renamed playlist between
    # ensure_playlist and this call). The API raises on HTTP errors; also verify the
    # response carries the expected IDs so we don't report success on a no-op.
    snippet = resp.get("snippet", {})
    if snippet.get("playlistId") != playlist_id or snippet.get("resourceId", {}).get("videoId") != video_id:
        raise RuntimeError(
            f"Playlist insert returned an unexpected response: {resp!r} — video {video_id} "
            f"may not have been added to playlist {playlist_id}"
        )


