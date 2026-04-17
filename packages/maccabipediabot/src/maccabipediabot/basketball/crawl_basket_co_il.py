import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.translations import normalize_player_name

import aiohttp
import bs4
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
from pydantic.json import pydantic_encoder

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

SEASON_23_24_TEAM_ID = 1096
BASKET_CO_IL_SITE_MACCABI_BASE_PAGE = "https://basket.co.il/team.asp?TeamId={team_id}"
COMPETITION_NAME = 'ליגת Winner סל'
BASKET_CO_IL_SITE_PREFIX = 'https://basket.co.il/'

BASKETBALL_BASE_FOLDER = Path("C:\\") / "maccabi" / "basketball"
RESULTS_FILE = BASKETBALL_BASE_FOLDER / 'basket_co_il_results.json'

MAX_CONNECTIONS = 100


@dataclass(frozen=True)
class GameDiscoveryMeta:
    """Metadata known about a game from the discovery step (before per-game scrape)."""
    game_id: int
    scrape_url: str
    page_title: str
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
    Mirrors basketball_game_uploader/src/services/game-parser/basket/basket-game-parser.service.ts.
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
        season=_season_from_date(meta.game_date),
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
    crowd: int | None = None
    if h5:
        stadium = h5.get_text(",", strip=True).split(",")[0].strip()
        crowd_div = h5.select_one("div.link-1")
        if crowd_div and "צופים:" in crowd_div.get_text():
            text = crowd_div.get_text().split("צופים:")[1].strip()
            digits = re.sub(r"[^\d]", "", text)
            if digits:
                crowd = int(digits)

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
    """Extract per-quarter and per-OT scores from `table.stats_tbl.categories`.

    Returns {maccabi: list, opponent: list}, each list 8 entries
    [Q1,Q2,Q3,Q4,OT1,OT2,OT3,OT4] with None for absent periods.
    """
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
    """Extract coaches and player stats from the per-team `table.stats_tbl` tables."""
    tables = soup.select("table.stats_tbl")
    if len(tables) < 4:
        return {
            "maccabi_coach": "",
            "opponent_coach": "",
            "maccabi_players": [],
            "opponent_players": [],
        }
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
    """Parse player rows from one team's box-score table.

    Layout: header rows first, then `<tr class="row">` per player. The first
    `tr.row` is the column header; players start at the second.
    """
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
            is_starting_five=bool(tds[2].get_text(strip=True)),
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


def _season_from_date(d: datetime) -> str:
    """Return season string like '2024/25'. Israeli basketball season runs Sep–Jun."""
    year = d.year
    if d.month >= 9:
        return f"{year}/{(year + 1) % 100:02d}"
    return f"{year - 1}/{year % 100:02d}"


def parse_players_events_from_soup_table_element(soup_table: BeautifulSoup) -> list[PlayerSummary]:
    rows = soup_table.find_all('tr')
    # rows 0-1 are not real headers, it's team name and stats category like: "rebounds"
    header_cells = rows[2].find_all(['th', 'td'])
    headers = [cell.get_text(strip=True) for cell in header_cells]
    if headers != ['#', 'שם שחקן', 'חמ', 'דק', 'נק', 'זרק/קלע', '%', 'זרק/קלע', '%', 'זרק/קלע', '%', 'הג', 'הת', 'סהכ',
                   'של', 'על', 'חט', 'אב', 'אס', 'של', 'על', 'מדד', '+/-'] and headers != ['#', 'שם שחקן', 'חמ', 'דק', 'נק', 'זרק/קלע', '%', 'זרק/קלע', '%', 'זרק/קלע', '%', 'הג', 'הת', 'סהכ', 'של', 'על', 'חט', 'אב', 'אס', 'של', 'על', 'מדד']:
        raise RuntimeError(f"We should work only on familiar headers: {headers}")

    def parse_attempts_scored(cell):
        # "13/4" → (13, 4)
        match = re.match(r'(\d+)\s*/\s*(\d+)', cell.text)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            raise RuntimeError(f"Could not parse: {cell.text}")

    players = []

    # Iterate over player rows
    for row in rows[3:]:
        cells = row.find_all('td')
        if not cells:
            continue  # skip empty rows

        if cells[1].get_text(strip=True) in ('קבוצתי', 'סה"כ', '-'):
            continue  # Skip summary rows

        two_points = parse_attempts_scored(cells[5])
        three_points = parse_attempts_scored(cells[7])
        one_points = parse_attempts_scored(cells[9])


        def optional_int(cell_id: int):
            return None if cells[cell_id].get_text(strip=True) in ['-', ''] else int(cells[cell_id].get_text(strip=True))


        player = PlayerSummary(
            number=int(cells[0].get_text(strip=True)),
            name=cells[1].get_text(strip=True),
            is_starting_five=cells[2].get_text(strip=True) == '*',
            minutes_played=optional_int(3),
            total_points=int(cells[4].get_text(strip=True)),
            three_scores_attempts=three_points[1],
            three_scores_scored=three_points[0],
            field_goals_attempts=two_points[1],
            field_goals_scored=two_points[0],
            free_throws_attempts=one_points[1],
            free_throws_scored=one_points[0],
            defensive_rebounds=optional_int(11),
            offensive_rebounds=optional_int(12),
            personal_total_fouls=optional_int(14),
            steals=optional_int(16),
            turnovers=optional_int(17),
            assists=optional_int(18),
            blocks=optional_int(19)
        )

        players.append(player)

    return players


async def enrich_game(session: ClientSession, game: BasketballGame) -> None:
    async with (session.get(game.game_url) as response):
        logging.info(f"Fetching all players events for game: {game.game_url}")

        content = await response.text()
        soup = BeautifulSoup(content, "html.parser")

        players_stats = soup.find_all(lambda tag: tag.name == "table" and "שם שחקן" in tag.get_text())

        if len(players_stats) != 2:
            raise RuntimeError(f"Could not find 2 player stats for game: {game.game_url}")

        def is_maccabi_table(text):
            return "מכבי תל אביב" in text or "מכבי Playtika תל אביב" in text or "מכבי פוקס תל אביב" in text or "מכבי אלקטרה תל אביב" in text or "מכבי עלית תל אביב" in text # There are sponsor in between maybe

        if is_maccabi_table(players_stats[0].text) and not is_maccabi_table(players_stats[1].text):
            maccabi_players = parse_players_events_from_soup_table_element(players_stats[0])
            opponent_players = parse_players_events_from_soup_table_element(players_stats[1])
        elif is_maccabi_table(players_stats[1].text) and not is_maccabi_table(players_stats[0].text):
            maccabi_players = parse_players_events_from_soup_table_element(players_stats[1])
            opponent_players = parse_players_events_from_soup_table_element(players_stats[0])
        else:
            raise RuntimeError('Can not find maccabi players events')

        game.maccabi_players = maccabi_players
        game.opponent_players = opponent_players

        more_game_data = soup.find("div", class_='more_data').text.replace('\xa0', ' ').strip()
        if "צופים: " in more_game_data:
            game.crowd = more_game_data.split("צופים: ")[1].strip()

        a=6

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

    for game in season_games:
        try:
            await enrich_game(session, game)
        except Exception:
            logging.exception(f"Could not enrich game: {game.game_url}")

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


async def crawl_game_pages():
    limited_connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    async with aiohttp.ClientSession(connector=limited_connector) as session:
        seasons_to_team_ids = await get_team_ids_for_all_seasons(session)
        logging.info(f'Seasons to team ids: {seasons_to_team_ids}')

        logging.info(f'Extracting specific games links from seasons pages')
        season_tasks = [extract_games_links_from_seasons_pages(session, season, team_id) for (season, team_id) in
                        seasons_to_team_ids.items()]

        basketball_games_from_season_pages = await asyncio.gather(*season_tasks)

    logging.info(f"Writing file to: {RESULTS_FILE}")
    RESULTS_FILE.write_text(json.dumps(basketball_games_from_season_pages, default=pydantic_encoder))


if __name__ == '__main__':
    logging.info("Started fetch games")
    asyncio.run(crawl_game_pages())
    logging.info("finished fetch games")
