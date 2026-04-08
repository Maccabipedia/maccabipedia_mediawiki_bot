import logging
from datetime import date
from pathlib import Path
from typing import Set

from bs4 import BeautifulSoup
from dateutil.parser import ParserError
from dateutil.parser import parse as datetime_parser

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

_logger = logging.getLogger(__name__)


class TransfermarktComparator:
    def __init__(self, maccabi_games_stats: MaccabiGamesStats, data_storage_folder: Path):
        self.maccabi_games_stats = maccabi_games_stats
        self.data_storage_folder = data_storage_folder

    def compare_games_date(self) -> None:
        _logger.info(f'Starting to compare player by player, starting from these with the most appearances')

        for player_html_file in self.data_storage_folder.glob('*.html'):
            _logger.info(f'Handling file: {player_html_file}')

            try:
                player_games = self.maccabi_games_stats.get_games_by_played_player_name(player_html_file.stem)
                self._compare_one_player(player_html_file, player_games)
            except Exception:
                _logger.exception(f'Could not compare games for player: {player_html_file.stem}, due to: ')

    def _compare_one_player(self, player_html_file: Path, player_games: MaccabiGamesStats) -> None:
        transfermarkt_games_dates = set(self._get_player_games_dates(player_html_file))

        maccabi_games_stats_dates = set([game.date.date() for game in player_games])

        transfermarkt_and_not_maccabipedia = transfermarkt_games_dates - maccabi_games_stats_dates
        maccabipedia_and_not_transfermarkt = maccabi_games_stats_dates - transfermarkt_games_dates

        _logger.info(f'Summary | Player: {player_html_file.stem}')
        if transfermarkt_and_not_maccabipedia:
            _logger.info(f'Only in Transfermarkt: {transfermarkt_and_not_maccabipedia}')

        # Transfermarkt may have some missing data, so we can't assume anything about this one:
        if maccabipedia_and_not_transfermarkt:
            _logger.debug(f'Only in MaccabiPedia: {maccabipedia_and_not_transfermarkt}')

    def _get_player_games_dates(self, player_html_file: Path) -> Set[date]:
        page_content = BeautifulSoup(player_html_file.read_text(encoding='utf8'), "html.parser")

        games_dates = []

        for potential_game_tr in page_content.find_all('tr'):
            td_childrens = potential_game_tr.find_all('td')
            if len(td_childrens) < 2:
                continue

            if potential_game_tr.attrs.get('class'):
                _logger.warning(f'Maybe did not played: {potential_game_tr.attrs["class"]}')
                continue

            try:
                potential_date = td_childrens[1].text
                # Format is similar to: MM/DD/YY
                if not all(c.isdigit() or c == '/' for c in potential_date) or len(potential_date) < 7:
                    _logger.info('Potential date does not have only numbers and slash or it is too short, skipping')
                    continue

                new_date = datetime_parser(potential_date, dayfirst=False, yearfirst=False)
                _logger.info(f'New date: {new_date}')

                games_dates.append(new_date)
            except ParserError:
                _logger.debug(f'Cant parse: {td_childrens[1]})')

        return set(game_date.date() for game_date in games_dates)
