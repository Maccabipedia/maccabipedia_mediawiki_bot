import logging

import mwparserfromhell
import requests

from pywikibot_boilerplate import run_boilerplate

_LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA = 'תבנית:טבלת_ליגת_כדורסל_2025/26'
_TABLE_STATUS_KEY = 'טבלה'

OPPONENTS_NAMES_TO_UNICODE = {"Maccabi Tel Aviv": "מכבי תל אביב",
                              "Hapoel Tel Aviv": "הפועל תל אביב",
                              "Hapoel Gilboa/Galil": "הפועל העמק",
                              "Maccabi Raanana": "מכבי עירוני רעננה",
                              "Maccabi Ironi Ramat Gan": "מכבי עירוני רמת גן",
                              "Hapoel Holon": "הפועל חולון",
                              "Hapoel Galil Elyon": "הפועל גליל עליון",
                              "Hapoel Jerusalem": "הפועל ירושלים",
                              "Maccabi Rishon LeZion": "מכבי ראשון לציון",
                              "Hapoel Beer Sheva": "הפועל באר שבע",
                              "Elitzur Netanya": "אליצור עירוני נתניה",
                              "Ironi Nes Ziona": "עירוני נס ציונה",
                              "Bnei Herzliya": "בני הרצליה",
                              "Ironi Kiryat Ata": "עירוני קרית אתא"
                              }


LINKS_TO_FETCH_LEAGUE_TABLE_FROM = [
    "https://prod-cdn-public-api.livescore.com/v1/api/app/stage/basketball/israel/super-league/2"
]

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

import pywikibot as pw


def fetch_league_table_data():
    stats = []

    for url in LINKS_TO_FETCH_LEAGUE_TABLE_FROM:
        resp = requests.get(url)
        table = resp.json()["Stages"][0]["LeagueTable"]["L"][0]["Tables"][0]["team"]
        for row in table:
            stats.append(
                "^".join(
                    [
                        OPPONENTS_NAMES_TO_UNICODE.get(row["Tnm"], row["Tnm"]),
                        str(row["pld"]),
                        row["winn"],
                        row["lstn"],
                        str(row["gf"]),
                        str(row["ga"]),
                        row["ptsn"],
                    ]
                )
            )
    prettified_result = ",\n".join(stats)

    logging.info(f'Fetched league table data: {prettified_result}')
    return prettified_result


def update_league_table_status() -> None:
    logging.info(f'Fetching current league table from: {LINKS_TO_FETCH_LEAGUE_TABLE_FROM}')
    league_table_data = fetch_league_table_data()

    league_table_template_page = pw.Page(site, _LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)

    parsed_mw_text = mwparserfromhell.parse(league_table_template_page.text)
    table_template = parsed_mw_text.filter_templates(_LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)[0]
    table_template.add(_TABLE_STATUS_KEY, league_table_data)

    league_table_template_page.text = parsed_mw_text

    league_table_template_page.save(summary="MaccabiBot - Update league table")


if __name__ == '__main__':
    update_league_table_status()
