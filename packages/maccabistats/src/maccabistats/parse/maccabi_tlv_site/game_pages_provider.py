# -*- coding: utf-8 -*-
import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from maccabistats.config import MaccabiStatsConfigSingleton

logger = logging.getLogger(__name__)


class GamePageUnavailableError(Exception):
    """Raised when a game's page on maccabi-tlv.co.il still fails after retries."""


_MAX_FETCH_ATTEMPTS = 4
_FETCH_BACKOFF_SECONDS = 2
_REQUEST_TIMEOUT_SECONDS = 30


def _fetch_ok(url):
    """Fetch a URL with retries on 5xx / transient network errors.

    The maccabi-tlv.co.il site intermittently returns 500 for valid game pages
    (observed in CI run 24640051609), so a single failed request is not a signal
    to give up. We retry a handful of times and raise GamePageUnavailableError
    only if the page is still unreachable — it is better to fail the job loudly
    than to silently drop a game from the parse.
    """
    last_detail = "no attempts"
    for attempt in range(1, _MAX_FETCH_ATTEMPTS + 1):
        try:
            response = requests.get(url, timeout=_REQUEST_TIMEOUT_SECONDS)
        except requests.exceptions.RequestException as exc:
            last_detail = f"{type(exc).__name__}: {exc}"
            logger.warning("Fetch attempt %d/%d for %s failed: %s",
                           attempt, _MAX_FETCH_ATTEMPTS, url, last_detail)
        else:
            if response.status_code == 200:
                return response.content
            last_detail = f"HTTP {response.status_code}"
            if not 500 <= response.status_code < 600:
                raise GamePageUnavailableError(f"{last_detail} for {url}")
            logger.warning("Fetch attempt %d/%d for %s got %s",
                           attempt, _MAX_FETCH_ATTEMPTS, url, last_detail)

        if attempt < _MAX_FETCH_ATTEMPTS:
            time.sleep(_FETCH_BACKOFF_SECONDS * attempt)

    raise GamePageUnavailableError(
        f"{last_detail} after {_MAX_FETCH_ATTEMPTS} attempts for {url}")


folder_to_save_games_events_html_files_pattern = os.path.join(
    MaccabiStatsConfigSingleton.maccabi_site.folder_to_save_games_html_files, "game+{game_date}+events")

folder_to_save_games_squads_html_files_pattern = os.path.join(
    MaccabiStatsConfigSingleton.maccabi_site.folder_to_save_games_html_files, "game+{game_date}+squads")


def __get_beautifulsoup_parser_name():
    if MaccabiStatsConfigSingleton.maccabi_site.use_lxml_parser:
        logger.info("Using lxml parser for beautifulsoup")
        return "lxml"
    else:
        logger.info("Using html.parser for beautifulsoup")
        return "html.parser"


def save_game_web_page_to_disk(web_page):
    """
    :type web_page: str
    """

    game_events_web_page_content = requests.get(web_page).content
    game_squads_web_page_content = requests.get(web_page + "teams").content

    game_date = __extract_games_date(web_page)
    with open(folder_to_save_games_events_html_files_pattern.format(game_date=game_date),
              'wb') as maccabi_game_event_file:
        maccabi_game_event_file.write(game_events_web_page_content)
    with open(folder_to_save_games_squads_html_files_pattern.format(game_date=game_date),
              'wb') as maccabi_game_squad_file:
        maccabi_game_squad_file.write(game_squads_web_page_content)


def __extract_games_date(link):
    web_page = link.strip("/")  # Remove / at the end if exists for rsplit.
    game_date = web_page.rsplit("/")[-1]
    return game_date


# GameEvents #

def __get_game_events_bs_from_disk(link):
    game_date = __extract_games_date(link)

    with open(folder_to_save_games_events_html_files_pattern.format(game_date=game_date), 'rb') as game_events_file:
        return BeautifulSoup(game_events_file.read(), __get_beautifulsoup_parser_name())


def __does_game_events_bs_exists_on_disk(link):
    game_date = __extract_games_date(link)

    return os.path.isfile(folder_to_save_games_events_html_files_pattern.format(game_date=game_date))


def __get_game_events_bs_from_internet(link):
    return _fetch_ok(link)


def __download_game_events_page(link):
    game_events_web_page_content = __get_game_events_bs_from_internet(link)
    __save_game_events_bs_to_disk(link, game_events_web_page_content)
    return __get_game_events_bs_from_disk(link)


def __save_game_events_bs_to_disk(link, content):
    game_date = __extract_games_date(link)

    with open(folder_to_save_games_events_html_files_pattern.format(game_date=game_date),
              'wb') as maccabi_game_event_file:
        maccabi_game_event_file.write(content)


def get_game_events_bs_by_link(link):
    if MaccabiStatsConfigSingleton.maccabi_site.use_disk_as_cache_when_crawling:
        if __does_game_events_bs_exists_on_disk(link):
            return __get_game_events_bs_from_disk(link)
        else:
            return __download_game_events_page(link)
    else:
        return __download_game_events_page(link)


# GameSquads #

def __get_game_squads_bs_from_disk(link):
    game_date = __extract_games_date(link)

    with open(folder_to_save_games_squads_html_files_pattern.format(game_date=game_date), 'rb') as game_squads_file:
        return BeautifulSoup(game_squads_file.read(), __get_beautifulsoup_parser_name())


def __does_game_squads_bs_exists_on_disk(link):
    game_date = __extract_games_date(link)

    return os.path.isfile(folder_to_save_games_squads_html_files_pattern.format(game_date=game_date))


def __get_game_squads_bs_from_internet(link):
    return _fetch_ok(link + "teams")


def __download_game_squads_page(link):
    game_squads_web_page_content = __get_game_squads_bs_from_internet(link)
    __save_game_squads_bs_to_disk(link, game_squads_web_page_content)
    return __get_game_squads_bs_from_disk(link)


def __save_game_squads_bs_to_disk(link, content):
    game_date = __extract_games_date(link)

    with open(folder_to_save_games_squads_html_files_pattern.format(game_date=game_date),
              'wb') as maccabi_game_squad_file:
        maccabi_game_squad_file.write(content)


def get_game_squads_bs_by_link(link):
    if MaccabiStatsConfigSingleton.maccabi_site.use_disk_as_cache_when_crawling:
        if __does_game_squads_bs_exists_on_disk(link):
            return __get_game_squads_bs_from_disk(link)
        else:
            return __download_game_squads_page(link)
    else:
        return __download_game_squads_page(link)
