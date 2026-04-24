# -*- coding: utf-8 -*-
import logging
from collections.abc import Iterator
from collections import deque
from typing import Dict
import html

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from maccabistats.config import MaccabiStatsConfigSingleton

logger = logging.getLogger(__name__)

_MAX_LIMIT_PER_REQUEST = 5000  # mediawiki api hardcoded limit
_MUST_HAVE_FIELDS = "_pageName"

# MaccabiPedia occasionally serves transient 415 from an openresty proxy (normal server is nginx);
# seen twice in six days at ~19:00 UTC. Retry across those blips instead of failing the daily job.
_RETRYABLE_STATUSES = (408, 415, 429, 500, 502, 503, 504)


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=_RETRYABLE_STATUSES,
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class MaccabiPediaCargoChunksCrawler(Iterator):
    def __init__(self, tables_name, tables_fields, join_tables_on="", where_condition="1=1"):
        """

        :param tables_name: The table name to crawl
        :type tables_name: str
        :param tables_fields: Which fields to extract from the table
        :type tables_fields: str
        :param join_tables_on: Which field to join the given tables by
        :type join_tables_on: str
        :param where_condition: The condition of the query
        :type where_condition: str
        """

        self.base_crawling_address = MaccabiStatsConfigSingleton.maccabipedia.base_crawling_address

        self.tables_name = tables_name
        assert _MUST_HAVE_FIELDS in tables_fields, f"This class is depends on those fields to be queried: {_MUST_HAVE_FIELDS}"
        self.tables_fields = tables_fields
        self.join_tables_on = join_tables_on
        self.where_condition = where_condition

        self._current_offset = 0
        self._finished_to_crawl = False
        self._already_fetched_data_queue = deque()
        self._session = _build_session()

    @property
    def full_crawl_address(self):
        # Cargo for mediawiki 1.35 has a bug that enforce us to send some params with empty values
        return f"{self.base_crawling_address}" \
               f"&tables={self.tables_name}" \
               f"&fields={self.tables_fields}" \
               f"&join_on={self.join_tables_on}" \
               f"&limit={_MAX_LIMIT_PER_REQUEST}" \
               f"&offset={self._current_offset}" \
               f"&where={self.where_condition}" \
               f"&group_by=" \
               f"&order_by=" \
               f"&having="

    def _request_more_data(self):
        """
        Fetch more data from maccabipedia according to self.full_crawl_address
        """

        # Get data
        request_result = self._session.get(self.full_crawl_address, timeout=30)
        if request_result.status_code != 200:
            logging.exception(f"Error while fetching data from address: {self.full_crawl_address}, "
                              f"status code: {request_result.status_code}, text: {request_result.text}")
            raise ValueError(f"status code {request_result.status_code} while fetching data from maccabipedia")

        current_request_as_json = request_result.json()
        self._current_offset += _MAX_LIMIT_PER_REQUEST

        # We have received smaller amount than the limit, that is the last query
        if len(current_request_as_json) < _MAX_LIMIT_PER_REQUEST:
            self._finished_to_crawl = True

        # Add to queue for iteration
        [self._already_fetched_data_queue.append(self._decode_maccabipedia_data_and_remove_nones(data)) for data in
         current_request_as_json]

    @staticmethod
    def _decode_maccabipedia_data_and_remove_nones(maccabipedia_data) -> Dict:

        maccabipedia_data_without_nulls = {k: v for k, v in maccabipedia_data.items() if v is not None}

        if 'Opponent' in maccabipedia_data_without_nulls:
            maccabipedia_data_without_nulls['Opponent'] = html.unescape(maccabipedia_data_without_nulls['Opponent'])
        if 'Stadium' in maccabipedia_data_without_nulls:
            maccabipedia_data_without_nulls['Stadium'] = html.unescape(maccabipedia_data_without_nulls['Stadium'])

        return maccabipedia_data_without_nulls

    def __next__(self):
        if not self._already_fetched_data_queue:
            # Whether no data in the queue and the last request returned less than the limit
            if self._finished_to_crawl:
                raise StopIteration()

            self._request_more_data()
            # Check whether no more data is available on the server (and local - queue)
            if not self._already_fetched_data_queue:
                raise StopIteration()

        return self._already_fetched_data_queue.pop()

    @classmethod
    def create_games_crawler(cls):
        return cls(tables_name=MaccabiStatsConfigSingleton.maccabipedia.games_data_query.tables_names,
                   tables_fields=MaccabiStatsConfigSingleton.maccabipedia.games_data_query.fields_names,
                   join_tables_on=MaccabiStatsConfigSingleton.maccabipedia.games_data_query.join_on)

    @classmethod
    def create_games_events_crawler(cls):
        return cls(tables_name=MaccabiStatsConfigSingleton.maccabipedia.games_events_query.tables_names,
                   tables_fields=MaccabiStatsConfigSingleton.maccabipedia.games_events_query.fields_names)
