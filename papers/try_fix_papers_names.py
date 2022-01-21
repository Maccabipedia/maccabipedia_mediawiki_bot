import logging
from pathlib import Path

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

_PAPER_NAME = "חדשות הספורט"


def rename_file(old_file: Path, new_file: Path) -> Path:
    if str(old_file) == str(new_file):
        return new_file

    logging.info(f"Renaming {old_file.name} ---> {new_file.name}")
    old_file.rename(new_file)

    return new_file


def handle_paper_image_file(paper: Path) -> None:
    new_paper = paper

    if paper.stem.startswith(_PAPER_NAME):
        logging.warning(f"{paper} starts with {_PAPER_NAME}, skipping")
    else:
        # Move Paper name to the start
        new_paper_stem = f"{_PAPER_NAME}{new_paper.stem.replace(_PAPER_NAME, '')}"
        new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Remove duplicate spaces:
    new_paper_stem = new_paper.stem.replace("  ", " ")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Remove spaces near brackets:
    new_paper_stem = new_paper.stem.replace("( ", "(").replace(" )", ")")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Remove MTA against:
    new_paper_stem = new_paper.stem.replace("מכבי תל אביב נגד ", "").replace("נגד ", "")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Remove MTA against:
    new_paper_stem = new_paper.stem.replace("מ ", "מכבי ")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Remove makaf before paper:
    new_paper_stem = new_paper.stem.replace(" - עיתון", " עיתון").replace("- עיתון", " עיתון")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    # Move "עיתון 2" to be at the end of the stem
    if ' עיתון 2' in str(new_paper_stem):
        new_paper_stem = new_paper.stem.replace(" עיתון 2", "")
        new_paper_stem = f'{new_paper_stem} עיתון2'
        new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))


if __name__ == '__main__':
    folder = Path(
        r"/games_papers_to_upload/from_drive/חדשות הספורט/נגלה_אחרונה")

    for current_paper in folder.iterdir():
        if not current_paper.is_file():
            continue

        logging.info(f"Handle: {current_paper}")

        if _PAPER_NAME not in current_paper.stem:
            logging.error(f"No {_PAPER_NAME} in {current_paper}, skipping")
            continue

        if "(" in current_paper.stem and ")" not in current_paper.stem:
            logging.error(f"Only one bracket in {current_paper}")
            continue

        if ")" in current_paper.stem and "(" not in current_paper.stem:
            logging.error(f"Only one bracket in {current_paper}")
            continue

        try:
            handle_paper_image_file(current_paper)
        except FileExistsError:
            logging.warning('Trying to set עיתון2 to this file and re-handle')
            current_paper = rename_file(current_paper,
                                        current_paper.with_name(f'{current_paper.stem} עיתון2{current_paper.suffix}'))
