import json
import logging
from pathlib import Path
from typing import List

from pywikibot import pagegenerators, Category
from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

CACHE_FILE = Path("C://") / "maccabipedia" / "volleyball_code" / "cache.json"


def refresh_category(category: str, hard_refresh: bool = False) -> None:
    if not CACHE_FILE.is_file():
        CACHE_FILE.touch(exist_ok=True)
        CACHE_FILE.write_text(json.dumps([]))

    logging.info(f'Refresh every page in category: {category}')

    category_iterator = pagegenerators.CategorizedPageGenerator(Category(site, category),
                                                                recurse=True)
    cache: List[str] = json.loads(CACHE_FILE.read_text())
    for page in category_iterator:
        if page.title() in cache:
            logging.info(f'Page in cache: {page.title()}')
            continue

        logging.info(f'Refreshing page: {page.title()}')

        if hard_refresh:
            page.purge()
        else:
            page.touch(botflag=True)
        cache.append(page.title())
        CACHE_FILE.write_text(json.dumps(cache))


if __name__ == '__main__':
    refresh_category(category="עונות כדורעף")
