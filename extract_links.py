from openpyxl import load_workbook
from itertools import product
from collections import defaultdict
import json

import logging

logger = logging.getLogger(__name__)


# Both should be in each cell that contains full game link
full_game_text = "משחק מלא"
hyper_link_text = 'HYPERLINK'

SHOULD_BE_IN_FULL_GAME_LINK_CELL = [full_game_text, hyper_link_text]


def potential_sheets():
    current = 2019
    seasons = [f"{current - num - 1}{str(current - num)[-2:]}" for num in range(50)]
    seasons.append("שונות")

    return seasons


def cells_that_may_contain_full_games_links():
    cells = ['E', 'F', 'G']

    # Starting from the third row, the first two rows are headers
    return ["".join(map(str, cell)) for cell in product(cells, range(3, 50))]


def extract_full_game_link_from_cell_text(text):
    # That so bad (but work), all of this

    if "http" in text:
        return eval(text.replace("=HYPERLINK", ""))[0]

    raise RuntimeError("cannot find http in the link")


def extract(file_name):
    workbook = load_workbook(file_name)

    # dict of "sheet_name" to (round number) to link
    links = defaultdict(dict)

    for sheet_name in potential_sheets():
        if sheet_name in workbook:
            logger.info("Extracting from {sheet_name} sheet")
            current_sheet = workbook[sheet_name]

            for cell in cells_that_may_contain_full_games_links():
                if current_sheet[cell].value and all(text in str(current_sheet[cell].value) for text in SHOULD_BE_IN_FULL_GAME_LINK_CELL):
                    try:
                        full_game_link = extract_full_game_link_from_cell_text(current_sheet[cell].value)
                        # Save the game link at "sheet_name" at round_number
                        links[sheet_name][int(cell[1:]) - 2] = full_game_link
                        logger.info(f"Found full game link: {full_game_link}\n in cell {cell}, sheet: {sheet_name}")
                    except Exception:
                        logger.exception(f"Could not parse full game text: {current_sheet[cell].value}")
                elif current_sheet[cell].value:
                    logger.warning(f"Could not find all the required text inside this cell value: {current_sheet[cell].value}")

    with open(r"C:\maccabipedia\videos\full_games.json", 'w') as p:
        json.dump(links, p)


if __name__ == "__main__":
    extract(r"F:\Maccabi-videos\csv\maccabi.xlsx")
