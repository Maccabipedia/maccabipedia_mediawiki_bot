import logging
from pathlib import Path

from pywikibot_boilerplate import run_boilerplate

run_boilerplate()

import pywikibot as pw

site = pw.Site()
site.login()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
START_YEAR = 1953  # First season will be 1953/54
END_YEAR = 2024    # Last season will be 2024/25
NAMESPACE = "כדורסל"  # Basketball namespace
DRY_RUN = False     # Set to True to preview without creating pages


def generate_season_name(year: int) -> str:
    """
    Generate season name in format YYYY/YY
    For example: 2012 -> 2012/13, 1999 -> 1999/00
    Handles edge case around year 2000 properly
    """
    next_year = year + 1
    next_year_short = str(next_year)[-2:].zfill(2)  # Get last 2 digits and zero-pad
    return f"{year}/{next_year_short}"


def create_redirect_page(short_name: str, full_name: str) -> None:
    """
    Create a redirect page from short_name to full_name
    
    :param short_name: The redirect page name (e.g., "כדורסל:2012/13")
    :param full_name: The target page name (e.g., "כדורסל:עונת 2012/13")
    """
    redirect_page = pw.Page(site, short_name)
    
    if redirect_page.exists():
        logger.info(f"Page already exists, skipping: {short_name}")
        return
    
    # MediaWiki redirect syntax
    redirect_text = f"#הפניה [[{full_name}]]"
    
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would create redirect: {short_name} -> {full_name}")
        logger.info(f"[DRY RUN] Content: {redirect_text}")
    else:
        redirect_page.text = redirect_text
        redirect_page.save(summary="MaccabiBot - Create season redirect")
        logger.info(f"Created redirect: {short_name} -> {full_name}")


def create_all_season_redirects() -> None:
    """
    Create redirect pages for all basketball seasons in the configured range
    """
    logger.info(f"Starting to create season redirects from {START_YEAR}/{START_YEAR+1-2000} to {END_YEAR}/{END_YEAR+1-2000}")
    logger.info(f"Dry run mode: {DRY_RUN}")
    
    created_count = 0
    skipped_count = 0
    
    for year in range(START_YEAR, END_YEAR + 1):
        season_name = generate_season_name(year)
        short_name = f"{NAMESPACE}:{season_name}"
        full_name = f"{NAMESPACE}:עונת {season_name}"
        
        try:
            if pw.Page(site, short_name).exists():
                logger.info(f"Page already exists, skipping: {short_name}")
                skipped_count += 1
            else:
                create_redirect_page(short_name, full_name)
                created_count += 1
        except Exception as e:
            logger.error(f"Error creating redirect for {short_name}: {e}")
    
    logger.info(f"\nFinished! Created: {created_count}, Skipped: {skipped_count}")


if __name__ == '__main__':
    create_all_season_redirects()
