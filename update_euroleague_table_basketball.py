import logging

import mwparserfromhell
import requests

from pywikibot_boilerplate import run_boilerplate

TABLE_TEMPLATE_ON_MACCABIPEDIA = 'תבנית:טבלת_יורוליג_2025/26'
TABLE_STATUS_KEY = 'טבלה'

OPPONENTS_NAMES_TO_UNICODE = {"Maccabi Tel Aviv": "מכבי תל אביב",
                              "Zalgiris Kaunas": "ז'לגיריס קובנה",
                              "Crvena Zvezda Beograd": "הכוכב האדום בלגרד",
                              "Hapoel Tel Aviv": "הפועל תל אביב",
                              "Olympiacos B.C.": "אולימפיאקוס",
                              "Monaco": "מונקו",
                              "Real Madrid": "ריאל מדריד",
                              "Valencia": "ולנסיה",
                              "Panathinaikos": "פנאתינייקוס",
                              "Barcelona": "ברצלונה",
                              "FC Bayern Munchen": "באיירן מינכן",
                              "Paris Basketball": "פריז בסקטבול",
                              "Olimpia Milano": "ארמאני מילאנו",
                              "Fenerbahçe": "פנרבחצ'ה",
                              "Virtus Bologna": "וירטוס בולוניה",
                              "BC Dubai": "דובאי",
                              "Anadolu Efes": "אנאדולו אפס",
                              "Saski Baskonia": "בסקוניה",
                              "Partizan": "פרטיזן בלגרד",
                              "ASVEL Lyon-Villeurbanne": "ליון-וילרבן",
                              }


LINKS_TO_FETCH_TABLE_FROM = [
    "https://prod-cdn-public-api.livescore.com/v1/api/app/stage/basketball/euro-league/euroleague-regular-season/2"
]

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

import pywikibot as pw


def fetch_table_data():
    stats = []

    for url in LINKS_TO_FETCH_TABLE_FROM:
        resp = requests.get(url)
        table = resp.json()["Stages"][0]["LeagueTable"]["L"][0]["Tables"][0]["team"]
        for row in table:
            wins = int(row["winn"])
            losses = int(row["lstn"])
            points = wins * 2 + losses * 1
            stats.append(
                "^".join(
                    [
                        OPPONENTS_NAMES_TO_UNICODE.get(row["Tnm"], row["Tnm"]),
                        str(row["pld"]),
                        row["winn"],
                        row["lstn"],
                        str(row["gf"]),
                        str(row["ga"]),
                        str(points),
                    ]
                )
            )
    prettified_result = ",\n".join(stats)

    logging.info(f'Fetched table data: {prettified_result}')
    return prettified_result


def update_table_status() -> None:
    logging.info(f'Fetching current table from: {LINKS_TO_FETCH_TABLE_FROM}')
    table_data = fetch_table_data()

    table_template_page = pw.Page(site, TABLE_TEMPLATE_ON_MACCABIPEDIA)

    parsed_mw_text = mwparserfromhell.parse(table_template_page.text)
    table_template = parsed_mw_text.filter_templates(TABLE_TEMPLATE_ON_MACCABIPEDIA)[0]
    table_template.add(TABLE_STATUS_KEY, table_data)

    table_template_page.text = parsed_mw_text

    table_template_page.save(summary="MaccabiBot - Update euroleague table")


if __name__ == '__main__':
    update_table_status()
