import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from basketball.basketball_game import BasketballGame

import aiohttp
import bs4
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pydantic.json import pydantic_encoder

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

BASKETBALL_BASE_FOLDER = Path("C:\\") / "maccabi" / "basketball"
RESULTS_FILE = BASKETBALL_BASE_FOLDER / 'results.json'
CACHE_FOLDER = BASKETBALL_BASE_FOLDER / 'cache'
PAGE_IS_GAME_CACHE_FILE = CACHE_FOLDER / 'is_game_cache.json'
MACCABI_TLV_BASE_GAME_URL_UNFORMATTED = "https://www.maccabi.co.il/gameZone.asp?gameID={game_number}"
MACCABI_TEL_AVIV_NAME = "מכבי תל אביב"

SHOULD_SAVE_TO_CACHE = True

MAX_CONNECTIONS = 100

GAMES_NUMBER_TO_FETCH = range(0, 18000)

is_game_cache_in_memory = {}


async def fetch_basketball_game(session: ClientSession, game_number: int) -> str:
    game_cache_file = CACHE_FOLDER / f"{game_number}.txt"

    if game_cache_file.is_file():
        logging.debug(f"Getting game number: {game_number} from cache")
        return game_cache_file.read_text()

    formatted_game_url = MACCABI_TLV_BASE_GAME_URL_UNFORMATTED.format(game_number=game_number)

    try:
        async with session.get(formatted_game_url) as response:
            logging.info(f"Fetching game: {formatted_game_url}")

            content = await response.text()
            if SHOULD_SAVE_TO_CACHE:
                logging.debug(f'Saving game file to cache: {game_cache_file}')
                game_cache_file.write_text(content)

            return content

    except Exception:
        logging.exception("Could not fetch game page")


def parse_inner_div_game(element: bs4.element.Tag, game_url: str) -> BasketballGame:
    home_team_name, away_team_name, *aa = [s.strip() for s in
                                           element.find("h2", {"class": "yellow he"}).text.split(" - ")]
    if len(aa) > 0:
        a = 2
    params = [s.strip() for s in element.find("span", {"class": "he"}).text.split("|")]
    if len(params) == 3:
        competition, fixture, raw_date = params
    elif len(params) == 4:
        competition, fixture, raw_date, location = params
    elif len(params) == 5:
        competition, fixture, raw_date, hour, location = params
    elif len(params) == 6:
        competition, fixture, raw_date, hour, tv, location = params
    else:
        raise RuntimeError(f"Unknown params: {params}")

    home_team_score = int(element.find("div", {"class": "leftPart he"}).text)
    away_team_score = int(element.find("div", {"class": "rightPart he"}).text)
    game_date = datetime.strptime(raw_date, '%d/%m/%Y')

    return BasketballGame(home_team_name=home_team_name,
                          away_team_name=away_team_name,
                          competition=competition,
                          fixture=fixture,
                          game_date=game_date,
                          home_team_score=home_team_score,
                          away_team_score=away_team_score,
                          game_url=game_url)


async def parse_basketball_game(session: ClientSession, game_number: int) -> BasketballGame:
    global is_game_cache_in_memory
    if not is_game_cache_in_memory.get(str(game_number), True):
        logging.debug("Not a maccabi/real game, found from global cache, skipping")
        return

    game_page_content = await fetch_basketball_game(session, game_number)

    parsed_soup = BeautifulSoup(game_page_content, 'html.parser')
    game_area_content = parsed_soup.find("div", {"id": "gameArea"})

    if game_area_content is None or MACCABI_TEL_AVIV_NAME not in game_area_content.text:
        logging.debug("Not a maccabi/real game, skipping")
        is_game_cache_in_memory[game_number] = False
        return

    b = parse_inner_div_game(game_area_content,
                             game_url=MACCABI_TLV_BASE_GAME_URL_UNFORMATTED.format(game_number=game_number))
    is_game_cache_in_memory[game_number] = True
    return b


async def crawl_game_pages():
    PAGE_IS_GAME_CACHE_FILE.touch(exist_ok=True)
    global is_game_cache_in_memory
    is_game_cache_in_memory = json.loads(PAGE_IS_GAME_CACHE_FILE.read_text())
    logging.info(f'Loaded {len(is_game_cache_in_memory)} game from global cache')

    limited_connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    async with aiohttp.ClientSession(connector=limited_connector) as session:
        tasks = [parse_basketball_game(session, game_number) for game_number in GAMES_NUMBER_TO_FETCH]
        try:
            games = await asyncio.gather(*tasks)
        except:
            logging.info(f'Starting to write is_game_cache to disk ({len(is_game_cache_in_memory)} games)')
            PAGE_IS_GAME_CACHE_FILE.write_text(json.dumps(is_game_cache_in_memory))
            logging.info('Finished to write is_game_cache to disk')

            raise

    non_empty_games = [game for game in games if game is not None]

    logging.info(f"Writing file to: {RESULTS_FILE}")
    RESULTS_FILE.write_text(json.dumps(non_empty_games, default=pydantic_encoder))


if __name__ == '__main__':
    logging.info("Started fetch games")
    asyncio.run(crawl_game_pages())
    logging.info("finished fetch games")
