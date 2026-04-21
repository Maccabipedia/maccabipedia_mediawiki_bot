"""End-to-end restore of a deleted football video:

  1. Upload the local backup to MaccabiPedia's YouTube channel.
  2. Add the new video to its season playlist (creating the playlist if missing).
  3. Update the matching field on the wiki game page to point at the new URL.

Pre-flight: the target wiki field must be empty. If it's already filled we abort
before touching YouTube (don't clobber a working link).

If upload succeeds but the wiki step fails, the video ID is logged loudly so the
operator can run `update_wiki_video_field` separately to finish the job. There is no
rollback: YouTube uploads cost 1,600 quota units and the daily cap is 10,000, so
re-uploading on every retry would burn through the quota fast.

Scope: football only. Basketball/volleyball use different wiki templates and Cargo
tables; a ball-sports variant can reuse the youtube/ helpers if needed.
"""
import argparse
import logging
import urllib.parse
from pathlib import Path

import mwparserfromhell as mw
import pywikibot as pw

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.common.wiki_login import get_site
from maccabipediabot.maintenance.videos.update_wiki_video_field import (
    TEMPLATE_NAME,
    set_video_field,
)
from maccabipediabot.maintenance.videos.youtube.title import (
    FULL_MATCH,
    HIGHLIGHTS,
    VideoType,
    format_video_title,
    season_playlist_title,
)
from maccabipediabot.maintenance.videos.youtube.upload import upload_and_add_to_playlist

logger = logging.getLogger(__name__)

VIDEO_TYPE_TO_WIKI_FIELD: dict[VideoType, str] = {
    FULL_MATCH: "משחק מלא",
    HIGHLIGHTS: "תקציר וידאו",
}

CLI_VIDEO_TYPE_TO_INTERNAL: dict[str, VideoType] = {
    "full-match": FULL_MATCH,
    "highlights": HIGHLIGHTS,
}


def wiki_page_url(wiki_page_title: str) -> str:
    """URL-encode the title so YouTube's auto-linkifier treats the description as clickable."""
    return "https://www.maccabipedia.co.il/" + urllib.parse.quote(wiki_page_title.replace(" ", "_"), safe=":")


def _check_wiki_field_empty(site: pw.Site, wiki_page_title: str, field: str) -> None:
    """Abort if the target wiki field already has a value — we don't want to clobber it.

    Race note: a concurrent edit between this check and `set_video_field`'s save can still
    happen; set_video_field re-checks at save time and raises if the field became non-empty.
    """
    page = pw.Page(site, wiki_page_title)
    if not page.exists():
        raise LookupError(f"Wiki page not found: {wiki_page_title}")
    parsed = mw.parse(page.text)
    templates = parsed.filter_templates(matches=lambda tmpl: tmpl.name.strip() == TEMPLATE_NAME)
    if not templates:
        raise LookupError(f"Template '{TEMPLATE_NAME}' not found on {wiki_page_title}")
    existing = str(templates[0].get(field).value).strip() if templates[0].has(field) else ""
    if existing:
        raise ValueError(
            f"Wiki field '{field}' on {wiki_page_title} is already set to '{existing}'. "
            f"Refusing to clobber. If the existing value is broken, clear it manually first."
        )


def restore(
    *,
    video_path: Path,
    wiki_page_title: str,
    season: str,
    competition: str,
    round_name: str,
    opponent: str,
    maccabi_score: int,
    opponent_score: int,
    video_type: VideoType,
) -> str:
    if not video_path.is_file():
        raise FileNotFoundError(f"Backup video not found: {video_path}")

    wiki_field = VIDEO_TYPE_TO_WIKI_FIELD[video_type]
    site = get_site()
    _check_wiki_field_empty(site, wiki_page_title, wiki_field)

    youtube_title = format_video_title(
        season=season,
        competition=competition,
        round_name=round_name,
        maccabi_score=maccabi_score,
        opponent=opponent,
        opponent_score=opponent_score,
        video_type=video_type,
    )
    description = wiki_page_url(wiki_page_title)
    playlist_title = season_playlist_title(season)

    logger.info("Uploading %s as %r to %r", video_path, youtube_title, playlist_title)
    video_id = upload_and_add_to_playlist(video_path, youtube_title, playlist_title, description)
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info("Uploaded %s — now updating wiki field %r on %s", video_url, wiki_field, wiki_page_title)

    try:
        set_video_field(site, wiki_page_title, wiki_field, video_url)
    except Exception:
        logger.exception(
            "Upload succeeded (%s) but wiki update failed. Run update_wiki_video_field "
            "manually with --page %r --field %r --url %s",
            video_url, wiki_page_title, wiki_field, video_url,
        )
        raise
    return video_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", required=True, help="Path to backup video file")
    parser.add_argument("--wiki-page", required=True, help="Full wiki page title (e.g. 'משחק:...')")
    parser.add_argument("--season", required=True, help="Season in YYYY-YY form (e.g. 2008-09)")
    parser.add_argument("--competition", required=True, help="Competition name as it appears on the wiki page")
    parser.add_argument("--round", dest="round_name", required=True, help="Round name (e.g. 'מחזור 21', 'סיבוב ט')")
    parser.add_argument("--opponent", required=True, help="Opponent team name")
    parser.add_argument("--maccabi-score", type=int, required=True)
    parser.add_argument("--opponent-score", type=int, required=True)
    parser.add_argument(
        "--video-type", required=True, choices=sorted(CLI_VIDEO_TYPE_TO_INTERNAL.keys()),
    )
    args = parser.parse_args()

    setup_logging(level=logging.INFO)
    pw.config.verbose_output = False

    video_id = restore(
        video_path=Path(args.file),
        wiki_page_title=args.wiki_page,
        season=args.season,
        competition=args.competition,
        round_name=args.round_name,
        opponent=args.opponent,
        maccabi_score=args.maccabi_score,
        opponent_score=args.opponent_score,
        video_type=CLI_VIDEO_TYPE_TO_INTERNAL[args.video_type],
    )
    logger.info("Done. https://www.youtube.com/watch?v=%s", video_id)


if __name__ == "__main__":
    main()
