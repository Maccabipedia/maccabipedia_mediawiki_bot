import argparse
import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import aiohttp
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from maccabipediabot.basketball._crawler_utils import (
    season_from_date,
    write_results,
)
from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.translations import (
    basket_co_il_competition_name,
    normalize_player_name,
    team_name_to_hebrew,
)

logger = logging.getLogger(__name__)

SEASON_23_24_TEAM_ID = 1096
BASKET_CO_IL_SITE_MACCABI_BASE_PAGE = "https://basket.co.il/team.asp?TeamId={team_id}"
COMPETITION_NAME = 'ליגת Winner סל'
BASKET_CO_IL_SITE_PREFIX = 'https://basket.co.il/'

MAX_CONNECTIONS = 100


@dataclass(frozen=True)
class GameDiscoveryMeta:
    """Metadata known about a game from the discovery step (before per-game scrape)."""
    game_id: int
    scrape_url: str
    game_date: datetime
    is_maccabi_home: bool
    opponent_name: str
    home_team_score: int
    away_team_score: int
    competition: str


def parse_game_page(html: str, meta: GameDiscoveryMeta) -> BasketballGame:
    """Parse one basket.co.il game-zone.asp HTML page into a BasketballGame.

    Extracts: header (fixture, stadium, referees, crowd), per-quarter scores,
    box-score (coach + player stats per team).
    """
    soup = BeautifulSoup(html, "html.parser")

    header = _parse_header(soup)
    quarter_scores = _parse_quarter_scores(soup, meta.is_maccabi_home)
    box_score = _parse_box_score(soup, meta.is_maccabi_home)

    return BasketballGame(
        home_team_name="מכבי תל אביב" if meta.is_maccabi_home else meta.opponent_name,
        away_team_name=meta.opponent_name if meta.is_maccabi_home else "מכבי תל אביב",
        competition=meta.competition,
        fixture=header["fixture"],
        game_date=meta.game_date,
        home_team_score=meta.home_team_score,
        away_team_score=meta.away_team_score,
        game_url=[meta.scrape_url],
        arena=header["stadium"],
        crowd=header["crowd"],
        referee=header["main_referee"],
        referee_assistants=header["assistant_referees"],
        first_quarter_maccabi_points=quarter_scores["maccabi"][0],
        second_quarter_maccabi_points=quarter_scores["maccabi"][1],
        third_quarter_maccabi_points=quarter_scores["maccabi"][2],
        fourth_quarter_maccabi_points=quarter_scores["maccabi"][3],
        first_overtime_maccabi_points=quarter_scores["maccabi"][4],
        second_overtime_maccabi_points=quarter_scores["maccabi"][5],
        third_overtime_maccabi_points=quarter_scores["maccabi"][6],
        fourth_overtime_maccabi_points=quarter_scores["maccabi"][7],
        first_quarter_opponent_points=quarter_scores["opponent"][0],
        second_quarter_opponent_points=quarter_scores["opponent"][1],
        third_quarter_opponent_points=quarter_scores["opponent"][2],
        fourth_quarter_opponent_points=quarter_scores["opponent"][3],
        first_overtime_opponent_points=quarter_scores["opponent"][4],
        second_overtime_opponent_points=quarter_scores["opponent"][5],
        third_overtime_opponent_points=quarter_scores["opponent"][6],
        fourth_overtime_opponent_points=quarter_scores["opponent"][7],
        maccabi_coach=box_score["maccabi_coach"],
        opponent_coach=box_score["opponent_coach"],
        maccabi_players=box_score["maccabi_players"],
        opponent_players=box_score["opponent_players"],
        season=season_from_date(meta.game_date),
    )


def _parse_header(soup: BeautifulSoup) -> dict:
    """Extract fixture, stadium, referees, crowd from #wrap_inner_3."""
    container = soup.select_one("#wrap_inner_3")
    if not container:
        raise RuntimeError("game-zone page missing #wrap_inner_3")

    h4 = container.select_one("h4")
    fixture = ""
    if h4:
        img = h4.find("img")
        if img and img.next_sibling:
            sibling_text = (img.next_sibling.get_text() if hasattr(img.next_sibling, "get_text")
                            else str(img.next_sibling))
            fixture = sibling_text.strip().replace("סל", "").strip()

    h5 = container.select_one("h5")
    stadium = ""
    if h5:
        stadium = h5.get_text(",", strip=True).split(",")[0].strip()

    # Crowd ('צופים: NNNN') lives somewhere inside #wrap_inner_3 — exact selector
    # has shifted over time, so just search the container text.
    crowd: int | None = None
    container_text = container.get_text(" ", strip=True).replace("\xa0", " ")
    crowd_match = re.search(r"צופים:\s*(\d[\d,]*)", container_text)
    if crowd_match:
        crowd = int(crowd_match.group(1).replace(",", ""))

    h6 = container.select_one("h6")
    main_referee = ""
    assistant_referees: list[str] = []
    if h6:
        text = re.sub(r"\s+", " ", h6.get_text()).strip()
        if "שופטים:" in text:
            after = text.split("שופטים:", 1)[1]
            if "משקיף:" in after:
                after = after.split("משקיף:", 1)[0]
            refs = [r.strip() for r in after.split(",") if r.strip()]
            if refs:
                main_referee = refs[0]
                assistant_referees = refs[1:]

    return {
        "fixture": fixture,
        "stadium": stadium,
        "main_referee": main_referee,
        "assistant_referees": assistant_referees,
        "crowd": crowd,
    }


def _parse_quarter_scores(soup: BeautifulSoup, is_maccabi_home: bool) -> dict:
    """Returns {maccabi: list, opponent: list}; each list is 8 entries
    [Q1,Q2,Q3,Q4,OT1,OT2,OT3,OT4] with None for absent periods."""
    cats = soup.select("table.stats_tbl.categories")
    if not cats:
        raise RuntimeError("game-zone page missing table.stats_tbl.categories")
    rows = cats[0].select("tr")
    if len(rows) < 3:
        raise RuntimeError("score table has fewer than 3 rows")

    # row 0 = header (period labels), row 1 = home team scores, row 2 = away team scores
    home_cells = [td.get_text(strip=True) for td in rows[1].select("td")][1:]
    away_cells = [td.get_text(strip=True) for td in rows[2].select("td")][1:]

    def _to_quarters(cells: list[str]) -> list[int | None]:
        out: list[int | None] = []
        for cell in cells:
            try:
                out.append(int(cell))
            except (ValueError, TypeError):
                out.append(None)
        return out[:8] + [None] * max(0, 8 - len(out))

    home_scores = _to_quarters(home_cells)
    away_scores = _to_quarters(away_cells)

    if is_maccabi_home:
        return {"maccabi": home_scores, "opponent": away_scores}
    return {"maccabi": away_scores, "opponent": home_scores}


def _parse_box_score(soup: BeautifulSoup, is_maccabi_home: bool) -> dict:
    tables = soup.select("table.stats_tbl")
    if len(tables) < 4:
        raise RuntimeError(
            f"game-zone page has fewer than 4 stats_tbl tables (got {len(tables)}); "
            "site layout likely changed"
        )
    home_table, away_table = tables[2], tables[3]

    home_coach = _coach_from_table(home_table)
    away_coach = _coach_from_table(away_table)
    home_players = _parse_player_rows(home_table)
    away_players = _parse_player_rows(away_table)

    if is_maccabi_home:
        return {
            "maccabi_coach": home_coach,
            "opponent_coach": away_coach,
            "maccabi_players": home_players,
            "opponent_players": away_players,
        }
    return {
        "maccabi_coach": away_coach,
        "opponent_coach": home_coach,
        "maccabi_players": away_players,
        "opponent_players": home_players,
    }


def _coach_from_table(table: Tag) -> str:
    """The coach is the second link in the team's table header (`<a>...:NAME</a>`)."""
    links = table.select("tr td a")
    if len(links) < 2:
        return ""
    text = links[1].get_text() or ""
    parts = text.split(":")
    return parts[1].strip() if len(parts) > 1 else ""


def _parse_player_rows(table: Tag) -> list[PlayerSummary]:
    """Layout: header rows first, then `<tr class="row">` per player. The first
    `tr.row` is the column header; players start at the second."""
    rows = table.select("tr")
    if not rows:
        return []

    start_index = -1
    seen = 0
    for i, row in enumerate(rows):
        if "row" in row.get("class", []):
            seen += 1
            if seen == 2:
                start_index = i
                break
    if start_index == -1:
        return []

    players: list[PlayerSummary] = []
    for row in rows[start_index:-1]:  # last row is totals
        tds = row.select("td")
        if len(tds) < 21:
            continue

        def _to_int(text: str | None) -> int:
            try:
                return int((text or "").strip())
            except (ValueError, TypeError):
                return 0

        def _split_stat(text: str | None) -> tuple[int, int]:
            if not text:
                return (0, 0)
            parts = text.split("/")
            return (_to_int(parts[0]), _to_int(parts[1]) if len(parts) > 1 else 0)

        fg_scored, fg_attempts = _split_stat(tds[5].get_text())
        tg_scored, tg_attempts = _split_stat(tds[7].get_text())
        ft_scored, ft_attempts = _split_stat(tds[9].get_text())

        number_link = tds[0].select_one("a")
        name_link = tds[1].select_one("a")
        raw_name = name_link.get_text(strip=True) if name_link else ""

        players.append(PlayerSummary(
            number=_to_int(number_link.get_text() if number_link else None) or None,
            name=normalize_player_name(raw_name),
            is_starting_five=tds[2].get_text(strip=True) == "*",
            minutes_played=_to_int(tds[3].get_text()),
            total_points=_to_int(tds[4].get_text()),
            field_goals_attempts=fg_attempts,
            field_goals_scored=fg_scored,
            three_scores_attempts=tg_attempts,
            three_scores_scored=tg_scored,
            free_throws_attempts=ft_attempts,
            free_throws_scored=ft_scored,
            defensive_rebounds=_to_int(tds[11].get_text()),
            offensive_rebounds=_to_int(tds[12].get_text()),
            personal_total_fouls=_to_int(tds[14].get_text()),
            steals=_to_int(tds[16].get_text()),
            turnovers=_to_int(tds[17].get_text()),
            assists=_to_int(tds[18].get_text()),
            blocks=_to_int(tds[19].get_text()),
        ))
    return players




async def enrich_game(session: ClientSession, game: BasketballGame) -> None:
    """Fetch the per-game page and fill in the rest of the BasketballGame fields."""
    url = game.game_url[0] if isinstance(game.game_url, list) else game.game_url
    async with session.get(url) as response:
        logging.info("Fetching per-game data: %s", url)
        content = await response.text()

    is_maccabi_home = game.home_team_name == "מכבי תל אביב"
    opponent = game.away_team_name if is_maccabi_home else game.home_team_name
    game_id_match = re.search(r"GameId=(\d+)", url)
    if not game_id_match:
        raise ValueError(f"Cannot extract GameId from URL: {url}")
    game_id = int(game_id_match.group(1))

    meta = GameDiscoveryMeta(
        game_id=game_id,
        scrape_url=url,
        game_date=game.game_date,
        is_maccabi_home=is_maccabi_home,
        opponent_name=opponent,
        home_team_score=game.home_team_score,
        away_team_score=game.away_team_score,
        competition=game.competition,
    )
    parsed = parse_game_page(content, meta)

    game.arena = parsed.arena
    game.crowd = parsed.crowd
    game.referee = parsed.referee
    game.referee_assistants = parsed.referee_assistants
    game.maccabi_coach = parsed.maccabi_coach
    game.opponent_coach = parsed.opponent_coach
    game.maccabi_players = parsed.maccabi_players
    game.opponent_players = parsed.opponent_players
    game.first_quarter_maccabi_points = parsed.first_quarter_maccabi_points
    game.second_quarter_maccabi_points = parsed.second_quarter_maccabi_points
    game.third_quarter_maccabi_points = parsed.third_quarter_maccabi_points
    game.fourth_quarter_maccabi_points = parsed.fourth_quarter_maccabi_points
    game.first_overtime_maccabi_points = parsed.first_overtime_maccabi_points
    game.second_overtime_maccabi_points = parsed.second_overtime_maccabi_points
    game.third_overtime_maccabi_points = parsed.third_overtime_maccabi_points
    game.fourth_overtime_maccabi_points = parsed.fourth_overtime_maccabi_points
    game.first_quarter_opponent_points = parsed.first_quarter_opponent_points
    game.second_quarter_opponent_points = parsed.second_quarter_opponent_points
    game.third_quarter_opponent_points = parsed.third_quarter_opponent_points
    game.fourth_quarter_opponent_points = parsed.fourth_quarter_opponent_points
    game.first_overtime_opponent_points = parsed.first_overtime_opponent_points
    game.second_overtime_opponent_points = parsed.second_overtime_opponent_points
    game.third_overtime_opponent_points = parsed.third_overtime_opponent_points
    game.fourth_overtime_opponent_points = parsed.fourth_overtime_opponent_points

async def build_seasons_games_metadata_from_season_url(session: ClientSession, season_url: str, season: str) -> list[
    BasketballGame]:
    async with (session.get(season_url) as response):
        logging.info(f"Fetching all games from season: {season}")

        content = await response.text()
        soup = BeautifulSoup(content, "html.parser")
        rows = soup.find(lambda tag: tag.name == "h2" and "לוח משחקים" in tag.get_text()) \
            .find_next("table", class_="stats_tbl") \
            .select("tr.row")

        games = []
        for row in rows:
            cells = row.find_all("td")

            date_td = cells[0]
            time_td = cells[1]

            raw_game_date = date_td.contents[0].strip()
            game_date = datetime.strptime(raw_game_date, "%d/%m/%Y")  # Convert to datetime object
            hour = time_td.get_text(strip=True)

            raw_stage = cells[2].get_text(strip=True)
            # We skip problematic game dates in here, these rows doesn't contain competition in basket site
            # Many games of חצאי גמר are written w/o competition
            if not COMPETITION_NAME in raw_stage and raw_stage != 'פיינל פור - חצאי הגמר' and 'ליגת העל - בית הגמר' not in raw_stage:
                raise RuntimeError(f'Could not find {COMPETITION_NAME} in {raw_stage}, can not parse this game page')

            # Patch for game from '14/10/2012'
            if raw_stage == 'גמר ליגת Winner סל':
                raw_stage = 'ליגת Winner סל, גמר'

            if raw_stage == 'פיינל פור - חצאי הגמר':
                raw_stage = 'ליגת Winner סל, פיינל פור - חצאי הגמר'

            fixture = raw_stage.split(',')[1].strip()

            home_team = cells[3].get_text(strip=True)
            away_team = cells[4].get_text(strip=True)

            score_cell = cells[5]

            # Get game URL, raise if not found
            a_tag = score_cell.find("a")
            if not a_tag or "href" not in a_tag.attrs:
                raise RuntimeError(f"Game URL not found for {home_team} vs {away_team}")
            game_url = a_tag["href"]

            # Parse score and URL
            if 'img/icon_news.png' in str(score_cell):
                logging.info(f'Skipping future game: {game_url}')
                continue

            score_text = score_cell.get_text(strip=True)

            # Validate and parse score
            score_text = score_text.split('(')[0].strip()  # Remove the part inside parentheses (e.g., (1))

            try:
                home_score, away_score = map(int, score_text.split('-'))
            except (ValueError, IndexError):
                raise ValueError(f"Invalid score format: '{score_text}' for {home_team} vs {away_team}")

            basketball_game = BasketballGame(
                home_team_name=home_team,
                away_team_name=away_team,
                home_team_score=home_score,
                away_team_score=away_score,
                competition=COMPETITION_NAME,
                fixture=fixture,
                game_date=game_date,
                game_url=f'{BASKET_CO_IL_SITE_PREFIX}{game_url}',
                season=season,
                hour=hour,
                maccabi_players=[],
                opponent_players=[])

            games.append(basketball_game)
    return games


async def extract_games_links_from_seasons_pages(session: ClientSession, season: str, team_id: str) -> list[
    BasketballGame]:
    season_games = await build_seasons_games_metadata_from_season_url(
        session,
        BASKET_CO_IL_SITE_MACCABI_BASE_PAGE.format(team_id=team_id),
        season)

    enriched = 0
    failures: list[str] = []
    for game in season_games:
        try:
            await enrich_game(session, game)
            enriched += 1
        except Exception as exc:
            logging.exception("Could not enrich game: %s", game.game_url)
            failures.append(f"{game.game_url}: {exc!r}")

    if season_games and enriched == 0:
        raise RuntimeError(
            f"All {len(season_games)} games for season {season} failed to enrich. "
            f"First error: {failures[0]}"
        )
    if failures:
        logging.warning("season %s: enriched %d/%d games (%d failed)",
                        season, enriched, len(season_games), len(failures))
    return season_games


async def get_team_ids_for_all_seasons(session: ClientSession) -> dict[str, str]:
    async with session.get(BASKET_CO_IL_SITE_MACCABI_BASE_PAGE.format(team_id=SEASON_23_24_TEAM_ID)) as response:
        logging.info(f"Fetching all seasons team id")

        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')

        # Select all <option> elements inside the <select> inside <form id="seasons">
        options = soup.select("form#seasons select#TeamId option")

        # Create a dict form season str to team id
        seasons_to_team_ids = {opt.text.strip().replace('-', '/'): opt["value"] for opt in options if opt.get("value")}

        return seasons_to_team_ids


GAMES_ALL_FEED_URL = "https://basket.co.il/pbp/json/games_all.json"
MACCABI_TEAM_NAME_ENG = "Maccabi Tel-Aviv"
GAME_PAGE_URL_TEMPLATE = "https://basket.co.il/game-zone.asp?GameId={game_id}"


def discover_games_latest_season(limit: int | None = None) -> list[GameDiscoveryMeta]:
    """Fetch basket.co.il's current-season feed, return Maccabi finished games sorted desc by date."""
    resp = requests.get(GAMES_ALL_FEED_URL, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Unexpected games_all response: status={resp.status_code} "
            f"ctype={resp.headers.get('Content-Type')}\n{resp.text[:300]}"
        )

    # The feed is served as text/html and starts with a UTF-8 BOM, so json() fails.
    payload = json.loads(resp.content.decode("utf-8-sig"))
    games = payload[0]["games"]

    maccabi_games = [g for g in games
                     if g.get("team_name_eng_1") == MACCABI_TEAM_NAME_ENG
                     or g.get("team_name_eng_2") == MACCABI_TEAM_NAME_ENG]

    def _is_finished(g: dict) -> bool:
        # Both scores must be present (not None / not empty string) AND at least one
        # team must have scored. basket.co.il's feed marks unplayed-but-scheduled games
        # with 0-0 as a placeholder; in basketball a real result of 0-0 doesn't happen.
        s1, s2 = g.get("score_team1"), g.get("score_team2")
        if s1 in (None, "") or s2 in (None, ""):
            return False
        try:
            return int(s1) + int(s2) > 0
        except (TypeError, ValueError):
            return False

    finished = [g for g in maccabi_games if _is_finished(g)]

    def _sort_key(game: dict) -> datetime:
        d, m, y = game["game_date_txt"].split("/")
        return datetime(int(y), int(m), int(d))

    finished.sort(key=_sort_key, reverse=True)
    if limit:
        finished = finished[:limit]

    metas: list[GameDiscoveryMeta] = []
    unknown_competition_games: list[dict] = []
    for g in finished:
        d, m, y = g["game_date_txt"].split("/")
        time_str = g.get("game_time") or "00:00"
        hour, minute = time_str.split(":") if ":" in time_str else ("0", "0")
        game_dt = datetime(int(y), int(m), int(d), int(hour), int(minute))

        home_team = team_name_to_hebrew(g["team_name_eng_1"])
        away_team = team_name_to_hebrew(g["team_name_eng_2"])
        is_maccabi_home = home_team == "מכבי תל אביב"
        opponent = away_team if is_maccabi_home else home_team

        competition = basket_co_il_competition_name(g["game_type"])
        if not competition:
            unknown_competition_games.append(
                {"id": g.get("id"), "game_type": g.get("game_type"),
                 "date": g.get("game_date_txt"), "opp": opponent}
            )
            continue

        metas.append(GameDiscoveryMeta(
            game_id=int(g["id"]),
            scrape_url=GAME_PAGE_URL_TEMPLATE.format(game_id=g["id"]),
            game_date=game_dt,
            is_maccabi_home=is_maccabi_home,
            opponent_name=opponent,
            home_team_score=int(g["score_team1"]),
            away_team_score=int(g["score_team2"]),
            competition=competition,
        ))
    if unknown_competition_games:
        raise RuntimeError(
            "basket.co.il discovery encountered games with unknown game_type codes; "
            "extend translations._BASKET_GAME_TYPE before re-running. "
            f"Affected games: {unknown_competition_games}"
        )
    return metas


def fetch_game_html(scrape_url: str) -> str:
    """Fetch a basket.co.il game-zone.asp page as UTF-8 HTML."""
    resp = requests.get(scrape_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # basket.co.il sends bytes without a declared charset
    return resp.text


def _run_latest_season(limit: int | None) -> list[BasketballGame]:
    metas = discover_games_latest_season(limit=limit)
    logging.info("Discovered %d Maccabi games for latest season", len(metas))
    out: list[BasketballGame] = []
    failures: list[tuple[str, str]] = []
    for meta in metas:
        try:
            html = fetch_game_html(meta.scrape_url)
            out.append(parse_game_page(html, meta))
        except Exception as exc:
            logging.exception("Failed to parse %s (date=%s opp=%s)",
                              meta.scrape_url, meta.game_date.date(), meta.opponent_name)
            failures.append((meta.scrape_url, repr(exc)))
    if metas and not out:
        raise RuntimeError(
            f"All {len(metas)} discovered basket.co.il games failed to parse — "
            f"likely schema drift. First error: {failures[0][1]}"
        )
    if failures:
        logging.warning("basket.co.il: parsed %d/%d games (%d failed)",
                        len(out), len(metas), len(failures))
    return out


def main() -> None:
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser(description="Crawl basket.co.il for Maccabi games.")
    parser.add_argument("--season", choices=("latest", "all"), default="latest")
    parser.add_argument("--limit", type=int, default=None,
                        help="Cap the number of most-recent games (latest mode only).")
    parser.add_argument("--output", type=Path, required=True, help="Path to write JSON output.")
    args = parser.parse_args()

    if args.season == "latest":
        games = _run_latest_season(args.limit)
    else:
        async def _run_all() -> list[BasketballGame]:
            connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)
            async with aiohttp.ClientSession(connector=connector) as session:
                seasons_to_team_ids = await get_team_ids_for_all_seasons(session)
                logging.info("Seasons to team ids: %s", seasons_to_team_ids)
                season_tasks = [
                    extract_games_links_from_seasons_pages(session, season, team_id)
                    for season, team_id in seasons_to_team_ids.items()
                ]
                results_per_season = await asyncio.gather(*season_tasks)
            return [g for season in results_per_season for g in season]
        games = asyncio.run(_run_all())

    write_results(games, args.output)


if __name__ == "__main__":
    main()
