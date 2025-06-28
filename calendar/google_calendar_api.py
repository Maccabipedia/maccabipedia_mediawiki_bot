import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import googleapiclient
import googleapiclient.discovery
from google.oauth2 import service_account

_logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

_GLOBAL_GOOGLE_SERVICE_ACCOUNT = Optional[googleapiclient.discovery.Resource]

_CURRENT_FOLDER = Path(__file__).parent.absolute()
_DEFAULT_CREDENTIALS_FILE_PATH = _CURRENT_FOLDER / 'default-google-credentials.json'


@dataclass
class GoogleCalendarAPI:
    credentials_json_path: Path

    def authorize(self) -> googleapiclient.discovery.Resource:
        _logger.info("Authorizing to Google api")
        credentials = service_account.Credentials.from_service_account_file(str(self.credentials_json_path),
                                                                            scopes=SCOPES)
        _logger.info("Authorized to Google api successfully! Creating ServiceAccount api object")

        return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials, cache_discovery=False)


def initialize_global_google_service_account(credentials_json_path: Path) -> None:
    global _GLOBAL_GOOGLE_SERVICE_ACCOUNT

    _GLOBAL_GOOGLE_SERVICE_ACCOUNT = GoogleCalendarAPI(credentials_json_path).authorize()
    _logger.info("Initialized Global Google service account")


def initialize_global_google_service_account_from_memory_json(credentials: str) -> None:
    _logger.info(f"Initializing Global Google service account from memory json, json size: {len(credentials)}")
    _DEFAULT_CREDENTIALS_FILE_PATH.write_text(credentials)

    initialize_global_google_service_account(_DEFAULT_CREDENTIALS_FILE_PATH)


def get_global_google_service_account() -> googleapiclient.discovery.Resource:
    global _GLOBAL_GOOGLE_SERVICE_ACCOUNT

    if _GLOBAL_GOOGLE_SERVICE_ACCOUNT is None:
        raise RuntimeError("Global Google service account is not initialized")

    return _GLOBAL_GOOGLE_SERVICE_ACCOUNT
