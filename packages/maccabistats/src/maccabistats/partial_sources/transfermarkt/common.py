import logging
from typing import Tuple, Dict, List

import aiohttp
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

SEARCH_PLAYER_URL = 'https://www.transfermarkt.com/detailsuche/spielerdetail/suche'

# Data copied from Chrome developer tools
PLAYER_STATS_URL_PATTERN_UNFORMATTED = 'https://www.transfermarkt.com/sheran-yeini/leistungsdatendetails/spieler/{player_id}/plus/0?saison=&verein=119&liga=&wettbewerb=&pos=&trainer_id='

# Transfermarkt block python requests (nginx return 404)
FAKE_USER_AGENT = {'User-agent': 'Mozilla/5.0'}


# Use Chrome dev tools to perform one search than:
# 1) Right click on this requests, copy as curl cmd, take this data to:
# 2) https://curlconverter.com/ , convert to python and copy paste in here
# 3) Remove the player name field value (inject without any escaping)
def _get_predefined_request(player_name: str) -> Tuple[Dict, List]:
    headers = {
        'authority': 'www.transfermarkt.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'origin': 'https://www.transfermarkt.com',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.transfermarkt.com/detailsuche/spielerdetail/suche',
        'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
        'cookie': 'TMSESSID=mfm9357vdcfm08t2redtssies0; _sp_v1_uid=1:595:0adb7fba-7a08-46c6-9d02-69f373165a1c; _sp_v1_csv=null; _sp_v1_lt=1:; consentUUID=75c6e066-a20c-482f-9d64-9898add02c1d; euconsent-v2=CPPNYndPPNYndAGABCENB0CsAP_AAH_AABBYHetf_X_fb3_j-_59__t0eY1f9_7_v-0zjheds-8Nyd_X_L8X72M7vB36pq4KuR4Eu3LBAQdlHOHcTQmw6IkVqTPsbk2Mr7NKJ7PEmnMbe2dYGH9_n9XT_ZKY79_____7__-_____7_f__-__3_v5_V--wAAAAAAAACBwQBBgACgAAAggAABAoRCAACAESAAAAAIIQAKAJAAlUAASuAjMBAAAQGICEAAEAICEGAQAAAABIAEAIAWCAQAEQCAAEAAgAAAAhABAYASAgAAAgBIQAEQAQgQEEQAEHIQEBAAQQAoAIAABxIYAQBllACQFgkFIABAAC4AKAAqABkADgAHgAQAAwABlADQANQAeQBDAEUAJgAT4AqgCsAFgAN4AcwA9AB-AEIAIaARABEgCWAE0AKUAW4AwwBkQDKAMsAaoA2QB3gD2AHxAPsA_QCAQEXARgAjgBKQCggFLAKeAVcAuYBigDWAG0ANwAbwA9AB8gENgIdASIAmIBMoCbAE7AKHAUiApoBYoC0AFsALkAXeAvMBgQDBgGEgMNAYeAyQBk4DLgGcgM-AaQA06BrAGsgNvCgAgBFAC-CAAgASAGiDQIQArABcAEMAMgAZYA2QB-AEAAIKARgApYBTwCrwFoAWkA1gBvADqgHyAQ6AioBIgCbAE7AKRAXIAwIBhIDDwGMAMnAZyAzwBnwcACA38dBhAAXABQAFQAMgAcABAAC6AGAAZQA0ADUAHgAPoAhgCKAEwAJ8AVQBWACwAFwAMQAZgA3gBzAD0AH4AQ0AiACJAEsAJgATQAowBSgCxAFvAMIAwwBkADKAGiANkAd4A9oB9gH6AP-Ai4CMAEcgJSAlQBQQCngFXALFAWgBaQC5gF5AMUAbQA3AB1AD0AIbAQ6AiIBFQCLwEggJEASoAmQBNgCdgFDgKaAVYAsUBaEC2ALZAXAAuQBdoC7wF5gMGAYSAw0Bh4DEgGMAMeAZIAycBlQDLAGXAM5AZ8A0SBpAGkgNLAacA1gBt48AIAIoAXwBGQG_jgAYAFwASAGZGQFgAKABDACYAI4AZcA-wD8AIwARwApYBVwCtgG8ATEAmwBaIC2AF5gMCAYeAzkBngDPhUBoACgAQwAmABcAEcAMsAfgBGACOAFLAKvAWgBaQDeAJBATEAmwBTYC2AFyALzAYEAw8BnIDPAGfANyIQNgAFgAUAAyAC4AGIAQwAmABTACqAFwAMQAZgA3gB6AEcALEAYQA74B9gH4AP8AjABHACUgFBAKGAU8Aq8BaAFpALmAYoA2gB1AD0AJBASIAlQBNgCmgFigLRgWwBbQC4AFyALtAYeAxIBk4DOQGeAM-AaIA0kBpYDgCIAIAXwBGSAAEAzJKBsAAgABYAFAAMgAcAA_ADAAMQAeABEACYAFUALgAYgAzABtAENAIgAiQBRgClAFuAMIAaoA2QB3gD8AIwARwAk4BTwCrwFoAWkAxQBuADqAHyAQ6AioBF4CRAE2ALFAWwAu0BeYDDwGTgMsAZyAzwBnwDSAGsANvAcATABAEZAb-SABAAXAMyIgNABWAEMAMgAZYA2QB-AEAAIwAUsAp4BVwDWAHVAPkAh0BIgCbAE7AKRAXIAwIBhIDDwGTgM5AZ8JAAgN_EAAQASFIIgAC4AKAAqABkADgAIIAYABlADQANQAeQBDAEUAJgATwApABVACwAGIAMwAcwA_ACGgEQARIAowBSgCxAFuAMIAZQA0QBqgDZAHfAPsA_QCMAEcAJSAUEAoYBVwCtgFzALyAbQA3AB6AEOgIvASIAk4BNgCdgFDgLFAWwAuABcgC7QF5gMNAYeAxgBkgDJwGXAM5AZ4Az6BpAGkwNYA1kBt5UAEAL4Bv5QAIABcAEgBJwCdg.YAAAAAAAAAAA; _sp_v1_opt=1:login|true:last_id|11:; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKBjLyQAyD2lidGKVUEDOvNCcHyC4BK6iurVXSgSuHSmFXFgsAwY5621cAAAA%3D; _sp_v1_consent=1!1:1:1:0:0:0; cuukie=aFNyQmprTnRNQ1NSeEtxNzZ4ZG1KRHBwb0FWWmRJWkw5dohlCwjNZ4wmzfBOe-5c2u_eam2YiXJcXg2XGXa4Zw%3D%3D; _sp_v1_data=2:411597:1636129427:0:31:0:31:0:0:_:-1',
    }

    data = [
        ('Detailsuche[vorname]', ''),
        ('Detailsuche[name]', ''),
        ('Detailsuche[name_anzeige]', ''),
        ('Detailsuche[passname]', player_name),
        ('Detailsuche[genaue_suche]', '0'),
        ('speichern', 'Submit search'),
        ('Detailsuche[geb_ort]', ''),
        ('Detailsuche[genaue_suche_geburtsort]', '0'),
        ('Detailsuche[land_id]', ''),
        ('Detailsuche[zweites_land_id]', ''),
        ('Detailsuche[geb_land_id]', ''),
        ('Detailsuche[kontinent_id]', ''),
        ('Detailsuche[geburtstag]', 'doesn\'t matter'),
        ('Detailsuche[geburtsmonat]', 'doesn\'t matter'),
        ('Detailsuche[geburtsjahr]', ''),
        ('alter', '0 - 150'),
        ('Detailsuche[age]', '0;150'),
        ('Detailsuche[minAlter]', '0'),
        ('Detailsuche[maxAlter]', '150'),
        ('jahrgang', '1850 - 2006'),
        ('Detailsuche[jahrgang]', '1850;2006'),
        ('Detailsuche[minJahrgang]', '1850'),
        ('Detailsuche[maxJahrgang]', '2006'),
        ('groesse', '0 - 220'),
        ('Detailsuche[groesse]', '0;220'),
        ('Detailsuche[minGroesse]', '0'),
        ('Detailsuche[maxGroesse]', '220'),
        ('Detailsuche[hauptposition_id]', ''),
        ('Detailsuche[nebenposition_id_1]', ''),
        ('Detailsuche[nebenposition_id_2]', ''),
        ('Detailsuche[minMarktwert]', '0'),
        ('Detailsuche[maxMarktwert]', '200.000.000'),
        ('Detailsuche[fuss_id]', ''),
        ('Detailsuche[fuss_id]', ''),
        ('Detailsuche[captain]', ''),
        ('Detailsuche[captain]', ''),
        ('Detailsuche[rn]', ''),
        ('Detailsuche[wettbewerb_id]', ''),
        ('Detailsuche[w_land_id]', ''),
        ('nm_spiele', '0 - 200'),
        ('Detailsuche[nm_spiele]', '0;200'),
        ('Detailsuche[minNmSpiele]', '0'),
        ('Detailsuche[maxNmSpiele]', '200'),
        ('Detailsuche[trans_id]', '0'),
        ('Detailsuche[aktiv]', '0'),
        ('Detailsuche[vereinslos]', '0'),
        ('Detailsuche[leihen]', '0'),
    ]

    return headers, data


async def get_player_id_by_player_name(player_name: str) -> int:
    async with aiohttp.ClientSession() as async_session:

        headers, data = _get_predefined_request(player_name)

        search_player_response = await async_session.request('POST', SEARCH_PLAYER_URL, headers=headers, data=data)

        search_player_response.raise_for_status()

        search_page_soupped = BeautifulSoup(await search_player_response.content.read(), "html.parser")

        result_div = search_page_soupped.select('div#yw0')

        if len(result_div) > 1:
            raise RuntimeError('Should be one div with id yw0, might change in the future')

        result_div = result_div[0]

        # Find the players rows, they are marked in the outer html table with odd or even classes
        players_rows = list(result_div.find_all('tr', class_=['odd', 'even']))

        if len(players_rows) != 1:
            raise RuntimeError(f'Could not find exactly one player for: {player_name}, text: {result_div.text}')

        player_row = players_rows[0]

        for link in player_row.find_all('a'):
            # Working example: /sheran-yeini/profil/spieler/58342
            if 'profil/spieler' in link.attrs['href']:
                return link.attrs['href'].split('/')[-1]

        raise RuntimeError('Could not locate the player href link')
