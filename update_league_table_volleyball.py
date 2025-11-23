import logging
from dataclasses import dataclass

import mwparserfromhell
import pandas as pd
import requests

import sys, requests, ssl

print("Python version:", sys.version)
print("Requests version:", requests.__version__)
print("SSL version:", ssl.OPENSSL_VERSION)

from pywikibot_boilerplate import run_boilerplate
from volleyball_common import TEAM_NAMES_REPLACER

# Local overrides for team names mapping. Use the original team name string from the IVA
# table as the key and the desired modified name as the value. If a team name is not
# present in either this local dict or the imported TEAM_NAMES_REPLACER, the original
# name will be used unchanged.
# Example:
# LOCAL_TEAM_NAMES_REPLACER = {
#     'מכבי תל אביב': 'מכבי ת"א',
# }
LOCAL_TEAM_NAMES_REPLACER = {
    # put entries here as 'original_team_name': 'modified_team_name'
}

LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA = 'תבנית:טבלת ליגת כדורעף 2025/26'
_TABLE_STATUS_KEY = 'טבלה'

IVA_LEAGUE_TABLE_URL = 'https://iva.org.il/league/?LeagueId=7505&cYear=2026'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

import pywikibot as pw


@dataclass
class VolleyballTableTeamRecord:
    name: str
    games: int
    wins: int
    losses: int
    points_in_game_for: int
    points_in_game_against: int
    sets_for: int
    sets_against: int
    points: int

    def adapt_to_mediawiki_code(self) -> str:
        return '^'.join(
            str(o) for o in
            [self.name, self.games, self.wins, self.losses, self.points_in_game_for, self.points_in_game_against,
             self.sets_for, self.sets_against, self.points])


def parse_team_record(raw_team_record: pd.Series) -> VolleyballTableTeamRecord:
    team_name = raw_team_record['קבוצה']  # Take everything after the first dot
    games = raw_team_record["מש'"]
    wins = raw_team_record["נצ'"]
    losses = raw_team_record["הפ'"]
    points_in_game_against, points_in_game_for = raw_team_record["סה\"כ נקודות"].split("-")
    sets_against, sets_for = raw_team_record["סטים"].split("-")
    points = raw_team_record["נקודות"]
    return VolleyballTableTeamRecord(name=team_name, games=games, wins=wins, losses=losses,
                                     points_in_game_for=points_in_game_for,
                                     points_in_game_against=points_in_game_against, sets_for=sets_for,
                                     sets_against=sets_against, points=points)


def fetch_league_data_from_iva():
    iva_league_table_page_response = requests.get(IVA_LEAGUE_TABLE_URL, verify=False)

    tables = pd.read_html(iva_league_table_page_response.content)
    volleyball_league_table = tables[0]

    parsed_team_records = []
    for raw_table_team_record in volleyball_league_table.iterrows():
        parsed_team_records.append(parse_team_record(raw_table_team_record[1]))

    # Merge the global replacer with local overrides; local overrides take precedence.
    merged_replacer = {**TEAM_NAMES_REPLACER, **LOCAL_TEAM_NAMES_REPLACER}

    for team_record in parsed_team_records:
        team_record.name = merged_replacer.get(team_record.name, team_record.name)

    aggregated_record_to_be_filled_in_table_template_key = ",\n".join(
        team_record.adapt_to_mediawiki_code() for team_record in parsed_team_records)

    logging.info(
        f'Finished to build wikicode for volleyball league table: {aggregated_record_to_be_filled_in_table_template_key}')
    return aggregated_record_to_be_filled_in_table_template_key


def update_volleyball_league_table_template() -> None:
    logging.info(f'Fetching league table template page: {LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA} '
                 f'from url: {IVA_LEAGUE_TABLE_URL}')
    league_table_data = fetch_league_data_from_iva()

    league_table_template_page = pw.Page(site, LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)

    parsed_mw_text = mwparserfromhell.parse(league_table_template_page.text)
    table_template = parsed_mw_text.filter_templates(LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)[0]
    table_template.add(_TABLE_STATUS_KEY, league_table_data)

    league_table_template_page.text = parsed_mw_text

    league_table_template_page.save(summary="MaccabiBot - Update Volleyball league table")

    logging.info('Finished to save league table!')


if __name__ == '__main__':
    update_volleyball_league_table_template()
