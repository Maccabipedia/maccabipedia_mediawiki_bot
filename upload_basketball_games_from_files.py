import logging
from pathlib import Path

import pywikibot as pw

from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()
BASKETBALL_PREFIX = "כדורסל"
PARENT_FOLDER = Path(rf"D:/maccabipedia_google_drive/מכביפדיה_ראשי/כדורסל/איסוף מידע לאתר/מוכן להעלאה")


def upload_game(game_txt_file: Path) -> None:
    logging.info(f'Uploading game from file: {game_txt_file}')
    page_name = f"{BASKETBALL_PREFIX}:{game_txt_file.stem}"
    game_page = pw.Page(site, page_name)

    if game_page.exists():
        logging.info(f'Game page already exists: {page_name}, skipping upload.')
        return

    game_page.text = game_txt_file.read_text(encoding='utf-8')

    game_page.save(summary="MaccabiBot - Uploading Basketball Games", bot=True)

    logging.info(f'Uploaded game from file: {game_txt_file}')


def upload_games() -> None:
    logging.info(f'Uploading basketball games from files in folder: {PARENT_FOLDER}')
    for game_txt_file in PARENT_FOLDER.rglob("*.txt"):
        try:
            upload_game(game_txt_file)
        except Exception as e:
            logging.error(f'Error uploading game from file: {game_txt_file}')


if __name__ == '__main__':
    upload_games()
