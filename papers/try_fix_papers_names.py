import logging
from pathlib import Path

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

_PAPER_NAME = "למרחב"
BASE_PAPER_FOLDER_PATH = Path(
    r"C:\code\maccabipedia_mediawikibot\games_papers_to_upload\from_drive\למרחב\למרחב 70-71")


def rename_file(old_file: Path, new_file: Path, reason: str = "") -> Path:
    if new_file.is_file() and old_file.samefile(new_file):
        return new_file

    logging.info(f"Renaming {reason} {old_file.name} ---> {new_file.name}")
    old_file.rename(new_file)

    return new_file


def handle_paper_image_file(paper: Path) -> Path:
    new_paper = paper

    # Remove duplicate spaces:
    new_paper_stem = new_paper.stem.replace("  ", " ")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{new_paper.suffix}'), "dup spaces")

    # Sometimes we got the names with "עיתון דבר" when "דבר" is the paper name,
    # we should remove it and have the paper name at start only
    new_paper_stem = new_paper.stem.replace(f"עיתון {_PAPER_NAME}", "")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{new_paper.suffix}'), "paper long name")

    if new_paper.stem.startswith(_PAPER_NAME):
        logging.warning(f"{new_paper} already starts with {_PAPER_NAME}")
    else:
        # Move Paper name to the start
        new_paper_stem = f"{_PAPER_NAME} {new_paper.stem.replace(_PAPER_NAME, '')}"
        new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "paper name prefix")

    # Remove duplicate spaces:
    new_paper_stem = new_paper.stem.replace("  ", " ")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "dup spaces")

    # Remove spaces near brackets:
    new_paper_stem = new_paper.stem.replace("( ", "(").replace(" )", ")")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "spaces brackets")

    # If not end with bracket, we need a space after it
    if ")" in new_paper.stem and ") " not in new_paper.stem and not new_paper.stem.endswith(")"):
        new_paper_stem = new_paper.stem.replace(")", ") ")
        new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "space bracket end2")

    # Remove spaces after bracket when stem ends (may be caused from older fixes):
    if new_paper.stem.endswith(") "):
        new_paper_stem = new_paper.stem.replace(") ", ")")
        new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "space bracket end")

    # Remove MTA against:
    new_paper_stem = new_paper.stem.replace("מכבי תל אביב נגד ", "").replace("נגד ", "")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "against maccabi")

    # Remove MTA against:
    new_paper_stem = new_paper.stem.replace("מ ", "מכבי ")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "shorten maccabi")

    # Remove makaf before paper:
    new_paper_stem = new_paper.stem.replace(" - עיתון", " עיתון").replace("- עיתון", " עיתון")
    new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'), "paper with makaf")

    for paper_num in range(1, 10):
        # Move "עיתון X" to be at the end of the stem
        if f' עיתון {paper_num}' in str(new_paper_stem):
            new_paper_stem = new_paper.stem.replace(f" עיתון {paper_num}", "")
            new_paper_stem = f'{new_paper_stem} עיתון{paper_num}'
            new_paper = rename_file(new_paper, new_paper.with_name(f'{new_paper_stem}{paper.suffix}'))

    return new_paper


def show_papers_names(base_folder: Path) -> None:
    for item in base_folder.iterdir():
        print(item.stem)


if __name__ == '__main__':
    folder = BASE_PAPER_FOLDER_PATH

    for current_paper in folder.iterdir():
        if not current_paper.is_file():
            continue

        logging.info(f"Handle: {current_paper}")

        # if _PAPER_NAME not in current_paper.stem:
        #     logging.error(f"No {_PAPER_NAME} in {current_paper}, skipping")
        #     continue

        if current_paper.suffix not in ['.jpg', '.jpeg']:
            current_paper = rename_file(current_paper, current_paper.with_name(f'{current_paper.name}.jpg'),
                                        "add jpg suffix")

        # Remove duplicate jpgs:
        if str(current_paper).count('.jpg') > 1:
            new_paper_name = current_paper.name.replace(".jpg", "", 1)
            current_paper = rename_file(current_paper, current_paper.with_name(new_paper_name), "dup jpgs")

        if "(" in current_paper.stem and ")" not in current_paper.stem:
            logging.error(f"Only one bracket in {current_paper}")
            continue

        if ")" in current_paper.stem and "(" not in current_paper.stem:
            logging.error(f"Only one bracket in {current_paper}")
            continue

        try:
            new_name = handle_paper_image_file(current_paper)
            if str(new_name) != str(current_paper):
                logging.info(f'שם הקובץ שונה: {current_paper.stem}-->{new_name.stem}')
        except FileExistsError:
            logging.warning('Trying to set עיתון2 to this file and re-handle')
            current_paper = rename_file(current_paper,
                                        current_paper.with_name(f'{current_paper.stem} עיתון2{current_paper.suffix}'))

    show_papers_names(folder)
