import logging
from pywikibot import pagegenerators, Category
from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()


def refresh_category(category: str, hard_refresh: bool = False) -> None:
    logging.info(f'Refresh every page in category: {category}')

    category_iterator = pagegenerators.CategorizedPageGenerator(Category(site, category),
                                                                recurse=True)
    for page in category_iterator:
        logging.info(f'Refreshing page: {page.title()}')

        if hard_refresh:
            page.purge()
        else:
            page.touch(botflag=True)


if __name__ == '__main__':
    refresh_category(category="משחקי כדורעף")
