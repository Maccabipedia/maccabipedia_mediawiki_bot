import logging
from dataclasses import dataclass

import mwparserfromhell
import pandas as pd
import requests

from pywikibot_boilerplate import run_boilerplate
from volleyball_common import TEAM_NAMES_REPLACER

LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA = 'תבנית:טבלת ליגת כדורעף 2024/25'
_TABLE_STATUS_KEY = 'טבלה'

IVA_LEAGUE_TABLE_URL = 'https://www.iva.org.il/league.asp?LeagueId=2334&cYear=2025'

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
    team_name = raw_team_record['קבוצה'].partition(".")[2].strip()  # Take everything after the first dot
    games = raw_team_record["מש'"]
    wins = raw_team_record["נצ'"]
    losses = raw_team_record["הפ'"]
    points_in_game_against, points_in_game_for = raw_team_record["נקודות"].split("-")
    sets_against, sets_for = raw_team_record["מערכות"].split("-")
    points = raw_team_record["נק'"]
    return VolleyballTableTeamRecord(name=team_name, games=games, wins=wins, losses=losses,
                                     points_in_game_for=points_in_game_for,
                                     points_in_game_against=points_in_game_against, sets_for=sets_for,
                                     sets_against=sets_against, points=points)


def fetch_league_data_from_iva():
    iva_league_table_page_response = requests.get(IVA_LEAGUE_TABLE_URL)

    tables = pd.read_html(iva_league_table_page_response.content)
    volleyball_league_table = tables[0]

    parsed_team_records = []
    for raw_table_team_record in volleyball_league_table.iterrows():
        parsed_team_records.append(parse_team_record(raw_table_team_record[1]))

    for team_record in parsed_team_records:
        team_record.name = TEAM_NAMES_REPLACER.get(team_record.name, team_record.name)

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
