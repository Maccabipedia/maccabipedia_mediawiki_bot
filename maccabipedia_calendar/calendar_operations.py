import logging
from typing import Any, Dict, List, Optional

import googleapiclient

from google_calendar_api import get_global_google_service_account

_logger = logging.getLogger(__name__)

_DEFAULT_NUMBER_OF_EVENTS_TO_FETCH = 2500

Event = Dict[str, Any]


def fetch_games_from_calendar(calendar_id: str, fetch_after_this_time: str,
                              max_events_to_fetch: Optional[int] = _DEFAULT_NUMBER_OF_EVENTS_TO_FETCH) -> List[Event]:
    google_service_account = get_global_google_service_account()

    _logger.info(f'Getting all of the event starting from time: {fetch_after_this_time}')

    events_result = google_service_account.events().list(
        calendarId=calendar_id,
        timeMin=fetch_after_this_time,
        singleEvents=True,
        maxResults=max_events_to_fetch,
        orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        _logger.info('No upcoming events found')
    else:
        _logger.info(f'Found {len(events)} upcoming events')

    return events


def upload_event(event: Dict, calendar_id: str) -> None:
    """
    Creating new event and uploading it to calendar

    :param event: Event to upload
    :param calendar_id: Calendar to upload to
    """

    google_service_account = get_global_google_service_account()

    event_result = google_service_account.events().insert(calendarId=calendar_id, body=event).execute()

    _logger.info("Created event:")
    _logger.info(f"- id: {event_result['id']}")
    _logger.info(f"- summary: {event_result['summary']}")
    _logger.info(f"- starts at: {event_result['start']['dateTime']}")
    _logger.info(f"- ends at: {event_result['end']['dateTime']}")


def update_event(new_event: Dict, event_id: str, calendar_id: str) -> None:
    google_service_account = get_global_google_service_account()

    event_result = google_service_account.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body={
            "summary": new_event['summary'],
            "location": new_event['location'],
            "description": new_event['description'],
            "source": new_event['source'],
            "extendedProperties": new_event['extendedProperties'],
            "start": new_event['start'],
            "end": new_event['end'],
        },
    ).execute()

    _logger.info("Updated event:")
    _logger.info(f"- id: {event_result['id']}")
    _logger.info(f"- summary: {event_result['summary']}")
    _logger.info(f"- starts at: {event_result['start']['dateTime']}")
    _logger.info(f"- ends at: {event_result['end']['dateTime']}")


def delete_event(event_id: str, calendar_id: str) -> None:
    """
    Deleting event from calendar

    :param event_id: id of the event to delete
    :param calendar_id: id of the calendar
    """
    google_service_account = get_global_google_service_account()

    try:
        _logger.info(f'Deleting event with ID: {event_id}')

        google_service_account.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        ).execute()

        _logger.info("Event deleted")
    except googleapiclient.errors.HttpError:
        _logger.exception("Failed to delete event due to:")
