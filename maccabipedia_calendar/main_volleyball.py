import json
import logging
import os
import sys
from zoneinfo import ZoneInfo

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import re
from datetime import datetime, timedelta
from typing import Dict, List

import requests
from dotenv import load_dotenv

from calendar_operations import fetch_games_from_calendar, update_event, upload_event, delete_event, Event
from google_calendar_api import initialize_global_google_service_account_from_memory_json
# Hack with adding dirname to sys path!
from upload_volleyball_games_from_iva_site import extract_games_metadata
from volleyball_game import VolleyballGame

_logger = logging.getLogger(__name__)


def search_event_in_calendar(event: Dict, events_list: List) -> Dict:
    """
    Checking if the parsed game is exists in the calendar by comparing links to game page in the official site.
    If it is, return the existing event, else return empty

    :param event: event to search
    :param events_list: list of events to compare to
    :return: event or empty object
    """

    if events_list:
        for temp_event in events_list:
            if 'extendedProperties' in temp_event and 'extendedProperties' in event:
                if event['extendedProperties']['shared']['maccabipedia_id'] == \
                        temp_event['extendedProperties']['shared']['maccabipedia_id']:
                    if 'id' in temp_event:
                        return temp_event
                    else:
                        return event

    return {}

def sync_future_games_to_calendar(potential_new_events: List[Event], existing_event: List[Event], calendar_id: str) -> None:
    _logger.info("--- Adding & Updating Events: ---")

    for potential_new_event in potential_new_events:
        curr_event = search_event_in_calendar(potential_new_event, existing_event)
        if curr_event != {}:
            if potential_new_event['summary'] != curr_event['summary'] or potential_new_event['description'] != curr_event['description'] \
                    or potential_new_event['start'] != curr_event['start'] or potential_new_event['location'] != curr_event['location']:
                update_event(potential_new_event, curr_event['id'], calendar_id)
        else:
            upload_event(potential_new_event, calendar_id)


def delete_unnecessary_events(events_list: List[Event], future_calendars_events: List[Event], calendar_id: str) -> None:
    """
    Deleting canceled/delayed/irrelevant events.
    Event which is in the calendar but not in the events list will be deleted
    """
    _logger.info("--- Deleting Events: ---")

    for event in future_calendars_events:
        exist_event = search_event_in_calendar(event, events_list)

        if exist_event == {}:
            _logger.info(f"Deleting event {event['summary']}")
            delete_event(event['id'], calendar_id)


def format_result(game: VolleyballGame) -> str:
    if game.maccabi_result is None and game.opponent_result is None:
        return f"המשחק טרם שוחק"  # Future game:

    if game.maccabi_result > game.opponent_result:
        return f"נצחון {game.maccabi_result} - {game.opponent_result}"

    return f"הפסד {game.maccabi_result} - {game.opponent_result}"


def cast_game_to_google_event(game: VolleyballGame) -> Event:
    # Get link to game page at maccabipedia
    response = requests.get(
        f"https://www.maccabipedia.co.il/index.php?title=Special:CargoExport&format=json&tables=Volleyball_Games&fields=_pageName&where=Volleyball_Games.Date='{game.date.date().strftime('%Y-%m-%d')}'")
    page_name = json.loads(response.text)
    if page_name and '_pageName' in page_name[0]:
        page_name = page_name[0]['_pageName']
        page_name = re.sub(r"\s+", '_', page_name)  # Replacing spaces/whitespace with underscore
        game_page_link = f'\n<a href="https://maccabipedia.co.il/{page_name}">עמוד המשחק</a>'
    else:
        page_name = ''
        game_page_link = f'\n<a href="https://maccabipedia.co.il">מכביפדיה</a>'

    maccabipedia_id = f"{game.opponent} {game.fixture} {game.competition}"

    # Make sure the game date will include timezone info (used when checking whether this is an existing event)
    game.date = game.date.replace(tzinfo = ZoneInfo('Asia/Jerusalem'))
    event = {
        'summary': f"[עף] {game.opponent} - {game.home_away}",
        'location': game.stadium,
        'description': f"{game.competition}, {game.fixture}\n{format_result(game)}{game_page_link}",
        'start': {
            'dateTime': game.date.isoformat(),
            'timeZone': "Asia/Jerusalem",
        },
        'end': {
            'dateTime': (game.date + timedelta(hours=2)).isoformat(),
            'timeZone': "Asia/Jerusalem",
        },
        'source': {
            'url': f'https://www.maccabipedia.co.il/{page_name}',
            'title': 'עמוד המשחק'
        },
        'extendedProperties': {
            'shared': {
                'maccabipedia_id': maccabipedia_id,
            }
        },
    }
    _logger.info(event)
    return event


def main(google_credentials: str, calendar_id: str):
    current_datetime = datetime.utcnow()
    current_time = current_datetime.isoformat() + 'Z'  # current datetime - to update and add upcoming games only

    initialize_global_google_service_account_from_memory_json(google_credentials)

    future_calendars_events = fetch_games_from_calendar(calendar_id, fetch_after_this_time=current_time)
    games_from_iva_site = extract_games_metadata(include_future_games=True)
    # filter in only event from the current_time and later (as we do in the calendar fetch)
    future_games_from_iva_site = [game for game in games_from_iva_site if game.date >= current_datetime]

    upcoming_events_from_iva_site = [cast_game_to_google_event(game) for game in future_games_from_iva_site]
    sync_future_games_to_calendar(upcoming_events_from_iva_site, future_calendars_events, calendar_id)
    delete_unnecessary_events(upcoming_events_from_iva_site, future_calendars_events, calendar_id)

    # Uncomment this in case you need to old games
    # add_history_games(seasons, calendar_id)


def entry_point() -> None:
    # noinspection PyBroadException
    try:
        logging.info("Starting!")
        load_dotenv()

        google_credentials = os.environ['GOOGLE_CREDENTIALS']
        calendar_id = os.environ['VOLLEYBALL_CALENDAR_ID']

        main(google_credentials, calendar_id)
    except Exception:
        logging.exception(f"Unhandled exception (exiting the program): ")
        exit(1)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    entry_point()
