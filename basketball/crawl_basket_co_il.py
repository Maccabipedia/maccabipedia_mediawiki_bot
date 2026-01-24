"""
This script crawls basket.co.il for Maccabi Tel Aviv games and player stats.
It extracts game metadata and detailed player statistics for specific seasons.

Run: python basketball/crawl_basket_co_il.py
"""
import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple

try:
    from basketball.basketball_game import BasketballGame, PlayerSummary
except ImportError:
    from basketball_game import BasketballGame, PlayerSummary

import aiohttp
import bs4
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pydantic.json import pydantic_encoder

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

SEASON_23_24_TEAM_ID = 1096
BASKET_CO_IL_SITE_MACCABI_BASE_PAGE = "https://basket.co.il/team.asp?TeamId={team_id}"
COMPETITION_NAME = 'ליגת Winner סל'
BASKET_CO_IL_SITE_PREFIX = 'https://basket.co.il/'

# Using project root relative path for agents-temp as per .agent/AGENTS.md
BASKETBALL_BASE_FOLDER = Path(__file__).parent.parent / ".agents-temp"
RESULTS_FILE = BASKETBALL_BASE_FOLDER / 'basket_co_il_results.json'

MAX_CONNECTIONS = 100


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
            total_rebounds=optional_int(13),
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
        
        # Try finding by h2 header first (modern structure)
        header = soup.find(lambda tag: tag.name == "h2" and "לוח משחקים" in tag.get_text())
        if header:
            table = header.find_next("table", class_="stats_tbl")
        else:
            # Fallback for older seasons where header might be inside the table
            table = soup.find(lambda tag: tag.name == "table" and "stats_tbl" in tag.get("class", []) and "לוח משחקים" in tag.get_text())
        
        if not table:
            raise RuntimeError(f"Could not find games table for season {season} at {season_url}")

        rows = table.select("tr.row")

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
        
        # Target seasons: 1988/89 to 2001/02
        target_seasons = [
            '1988/89', '1989/90', '1990/91', '1991/92', '1992/93', '1993/94', '1994/95',
            '1995/96', '1996/97', '1997/98', '1998/99', '1999/00', '2000/01', '2001/02'
        ]
        
        season_tasks = []
        for season, team_id in seasons_to_team_ids.items():
            if season in target_seasons:
                season_tasks.append(extract_games_links_from_seasons_pages(session, season, team_id))
            else:
                logging.debug(f"Skipping season {season} as it is not in the target range")

        basketball_games_from_season_pages = await asyncio.gather(*season_tasks)

    logging.info(f"Writing file to: {RESULTS_FILE}")
    RESULTS_FILE.write_text(json.dumps(basketball_games_from_season_pages, default=pydantic_encoder))


if __name__ == '__main__':
    logging.info("Started fetch games")
    asyncio.run(crawl_game_pages())
    logging.info("finished fetch games")
