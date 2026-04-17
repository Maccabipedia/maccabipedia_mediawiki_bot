"""Crawler for euroleaguebasketball.net.

Parses the server-injected __NEXT_DATA__ JSON on each page; no DOM scraping
or headless browser. Mirrors basketball_game_uploader's euroleague parser.
"""
import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.translations import (
    person_name_to_hebrew,
    stadium_name_to_hebrew,
    team_name_to_hebrew,
)

logger = logging.getLogger(__name__)

TEAM_RESULTS_URL = (
    "https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi-rapyd-tel-aviv/games/tel/"
)
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
COMPETITION_NAME_HE = "יורוליג"
MACCABI_TEAM_NAME_ENG = "Maccabi Rapyd Tel Aviv"
GAME_URL_PREFIX = "https://www.euroleaguebasketball.net"


@dataclass(frozen=True)
class EuroleagueGameMeta:
    """Metadata about a Euroleague game from the team-results discovery step."""
    scrape_url: str
    page_title: str
    game_date: datetime
    is_maccabi_home: bool
    opponent_name_eng: str
    home_team_score: int
    away_team_score: int
    fixture: str


def extract_next_data(html: str) -> dict[str, Any]:
    """Pull and parse the <script id="__NEXT_DATA__"> JSON blob from a Euroleague page."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.select_one("script#__NEXT_DATA__")
    if not script:
        raise RuntimeError("page is missing __NEXT_DATA__ script")
    return json.loads(script.text)


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HTTP_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def _flip_name(name: str) -> str:
    """Convert "LASTNAME, FIRSTNAME" → "Firstname Lastname"; titlecase as a courtesy."""
    if not name:
        return ""
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        return f"{first.title()} {last.title()}"
    return name.title()


def parse_game_page(next_data: dict, meta: EuroleagueGameMeta) -> BasketballGame:
    """Parse a Euroleague game-center page's __NEXT_DATA__ into a BasketballGame."""
    raw = next_data["props"]["pageProps"]["mappedData"]["rawGameInfo"]
    home, away = raw["home"], raw["away"]

    home_coach = person_name_to_hebrew(_flip_name((home.get("coach") or {}).get("name") or ""))
    away_coach = person_name_to_hebrew(_flip_name((away.get("coach") or {}).get("name") or ""))
    home_players = [_to_player(p) for p in home.get("players") or []]
    away_players = [_to_player(p) for p in away.get("players") or []]

    if meta.is_maccabi_home:
        maccabi_players, opponent_players = home_players, away_players
        maccabi_coach, opponent_coach = home_coach, away_coach
    else:
        maccabi_players, opponent_players = away_players, home_players
        maccabi_coach, opponent_coach = away_coach, home_coach

    main_referee, assistant_referees = _parse_referees(raw.get("referees") or [])
    venue_name = stadium_name_to_hebrew((raw.get("venue") or {}).get("name") or "")

    home_q = home.get("quarters") or {}
    away_q = away.get("quarters") or {}
    if meta.is_maccabi_home:
        maccabi_q, opponent_q = home_q, away_q
    else:
        maccabi_q, opponent_q = away_q, home_q

    opponent_name_he = team_name_to_hebrew(meta.opponent_name_eng)

    return BasketballGame(
        home_team_name="מכבי תל אביב" if meta.is_maccabi_home else opponent_name_he,
        away_team_name=opponent_name_he if meta.is_maccabi_home else "מכבי תל אביב",
        competition=COMPETITION_NAME_HE,
        fixture=f"מחזור {meta.fixture}" if meta.fixture and meta.fixture.isdigit() else (meta.fixture or ""),
        game_date=meta.game_date,
        home_team_score=meta.home_team_score,
        away_team_score=meta.away_team_score,
        game_url=[meta.scrape_url],
        arena=venue_name,
        crowd=raw.get("audience"),
        referee=main_referee,
        referee_assistants=assistant_referees,
        maccabi_coach=maccabi_coach,
        opponent_coach=opponent_coach,
        maccabi_players=maccabi_players,
        opponent_players=opponent_players,
        first_quarter_maccabi_points=maccabi_q.get("q1"),
        second_quarter_maccabi_points=maccabi_q.get("q2"),
        third_quarter_maccabi_points=maccabi_q.get("q3"),
        fourth_quarter_maccabi_points=maccabi_q.get("q4"),
        first_overtime_maccabi_points=maccabi_q.get("ot1"),
        second_overtime_maccabi_points=maccabi_q.get("ot2"),
        third_overtime_maccabi_points=maccabi_q.get("ot3"),
        fourth_overtime_maccabi_points=maccabi_q.get("ot4"),
        first_quarter_opponent_points=opponent_q.get("q1"),
        second_quarter_opponent_points=opponent_q.get("q2"),
        third_quarter_opponent_points=opponent_q.get("q3"),
        fourth_quarter_opponent_points=opponent_q.get("q4"),
        first_overtime_opponent_points=opponent_q.get("ot1"),
        second_overtime_opponent_points=opponent_q.get("ot2"),
        third_overtime_opponent_points=opponent_q.get("ot3"),
        fourth_overtime_opponent_points=opponent_q.get("ot4"),
        season=_season_from_date(meta.game_date),
    )


def _parse_referees(referees: list[dict]) -> tuple[str, list[str]]:
    """Return (main_referee_he, assistant_referees_he) from the referees list."""
    names_he = [person_name_to_hebrew(_flip_name(r.get("name") or "")) for r in referees if r.get("name")]
    if not names_he:
        return "", []
    return names_he[0], names_he[1:]


def _to_player(p: dict) -> PlayerSummary:
    stats = p.get("stats") or {}
    raw_name = p.get("name") or ""
    name = person_name_to_hebrew(_flip_name(raw_name))
    return PlayerSummary(
        name=name,
        number=_to_int_or_none(p.get("dorsal")),
        is_starting_five=bool(p.get("startFive")),
        minutes_played=_seconds_to_minutes(stats.get("timePlayed")),
        total_points=_to_int(stats.get("points")),
        field_goals_attempts=_to_int(stats.get("fieldGoalsAttempted2")),
        field_goals_scored=_to_int(stats.get("fieldGoalsMade2")),
        three_scores_attempts=_to_int(stats.get("fieldGoalsAttempted3")),
        three_scores_scored=_to_int(stats.get("fieldGoalsMade3")),
        free_throws_attempts=_to_int(stats.get("freeThrowsAttempted")),
        free_throws_scored=_to_int(stats.get("freeThrowsMade")),
        defensive_rebounds=_to_int(stats.get("defensiveRebounds")),
        offensive_rebounds=_to_int(stats.get("offensiveRebounds")),
        total_rebounds=_to_int(stats.get("totalRebounds")),
        assists=_to_int(stats.get("assists")),
        steals=_to_int(stats.get("steals")),
        turnovers=_to_int(stats.get("turnovers")),
        blocks=_to_int(stats.get("blocksFavour")),
        # Euroleague stat key has a typo; tolerate either spelling.
        personal_total_fouls=_to_int(stats.get("foulsCommited") or stats.get("foulsCommitted")),
    )


def _seconds_to_minutes(seconds) -> int | None:
    """Convert timePlayed (seconds) → whole minutes (round up if any seconds played)."""
    if seconds is None:
        return None
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return None
    if s <= 0:
        return 0
    return s // 60 + (1 if s % 60 else 0)


def _to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_int_or_none(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _season_from_date(d: datetime) -> str:
    year = d.year
    if d.month >= 9:
        return f"{year}/{(year + 1) % 100:02d}"
    return f"{year - 1}/{year % 100:02d}"


def discover_games_from_html(html: str, limit: int | None = None) -> list[EuroleagueGameMeta]:
    """Parse the team-results page HTML and return discovery metas for finished games.

    Sorted descending by date; optionally capped at N most-recent.
    """
    data = extract_next_data(html)
    results = data["props"]["pageProps"]["results"]["results"]

    metas: list[EuroleagueGameMeta] = []
    for r in results:
        # Only finished games. Status "result" is what the team-results page returns for past games.
        status = (r.get("status") or "").lower()
        if status not in {"result", "finished"} and not r.get("isPreviousGame"):
            continue

        date_str = r.get("date") or ""
        if not date_str:
            continue
        try:
            game_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            continue

        home, away = r.get("home") or {}, r.get("away") or {}
        home_score = _to_int_or_none(home.get("score"))
        away_score = _to_int_or_none(away.get("score"))
        if home_score is None or away_score is None:
            continue

        home_name = (home.get("name") or "").strip()
        is_maccabi_home = home_name == MACCABI_TEAM_NAME_ENG
        opponent_name_eng = (away.get("name") if is_maccabi_home else home.get("name") or "").strip()

        url_path = r.get("url") or ""
        if not url_path:
            continue
        scrape_url = url_path if url_path.startswith("http") else f"{GAME_URL_PREFIX}{url_path}"

        round_obj = r.get("round") or {}
        fixture = str(round_obj.get("round") or "")

        metas.append(EuroleagueGameMeta(
            scrape_url=scrape_url,
            page_title="",  # filled in below using translated team names
            game_date=game_dt,
            is_maccabi_home=is_maccabi_home,
            opponent_name_eng=opponent_name_eng,
            home_team_score=home_score,
            away_team_score=away_score,
            fixture=fixture,
        ))

    metas.sort(key=lambda m: m.game_date, reverse=True)
    if limit:
        metas = metas[:limit]

    finalized: list[EuroleagueGameMeta] = []
    for m in metas:
        opponent_he = team_name_to_hebrew(m.opponent_name_eng)
        home_he = "מכבי תל אביב" if m.is_maccabi_home else opponent_he
        away_he = opponent_he if m.is_maccabi_home else "מכבי תל אביב"
        date = m.game_date.strftime("%d-%m-%Y")
        title = f"כדורסל:{date} {home_he} נגד {away_he} - {COMPETITION_NAME_HE}"
        finalized.append(EuroleagueGameMeta(
            scrape_url=m.scrape_url,
            page_title=title,
            game_date=m.game_date,
            is_maccabi_home=m.is_maccabi_home,
            opponent_name_eng=m.opponent_name_eng,
            home_team_score=m.home_team_score,
            away_team_score=m.away_team_score,
            fixture=m.fixture,
        ))
    return finalized


def discover_games_latest_season(limit: int | None = None) -> list[EuroleagueGameMeta]:
    """Fetch the team-results page and discover Maccabi's finished Euroleague games."""
    return discover_games_from_html(fetch_html(TEAM_RESULTS_URL), limit=limit)


def _write_results(games: list[BasketballGame], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([g.model_dump(mode="json") for g in games], ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Wrote %d games to %s", len(games), output_path)


def _run_latest_season(limit: int | None) -> list[BasketballGame]:
    metas = discover_games_latest_season(limit=limit)
    logger.info("Discovered %d Euroleague games", len(metas))
    out: list[BasketballGame] = []
    for meta in metas:
        try:
            html = fetch_html(meta.scrape_url)
            out.append(parse_game_page(extract_next_data(html), meta))
        except Exception:
            logger.exception("Failed to parse %s", meta.scrape_url)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl euroleaguebasketball.net for Maccabi games.")
    parser.add_argument("--season", choices=("latest",), default="latest")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    games = _run_latest_season(args.limit)
    _write_results(games, args.output)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    main()
