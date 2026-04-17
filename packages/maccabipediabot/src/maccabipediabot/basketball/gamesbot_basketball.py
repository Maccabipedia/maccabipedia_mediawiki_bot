import logging
from functools import lru_cache
from pathlib import Path

from pydantic import TypeAdapter

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.common.prettify_games_pages import prettify_game_page_main_template
from maccabipediabot.common.wiki_login import get_site

import tldextract
import pywikibot as pw
from mwparserfromhell.nodes.template import Template

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


@lru_cache(maxsize=1)
def _site() -> pw.Site:
    """Lazy pywikibot site/login. Avoids logging in at module import time."""
    return get_site()

basketball_games_template_name = "משחק כדורסל"
basketball_games_prefix = "כדורסל"

# Legend games templates args consts:s
GAME_DATE = "תאריך המשחק"
GAME_HOUR = "שעת המשחק"
SEASON = "עונה"
COMPETITION = "מפעל"
FIXTURE = "שלב במפעל"
OPPONENT_NAME = "שם יריבה"
HOME_OR_AWAY = "בית חוץ"
ARENA = "אולם"
MACCABI_GAME_SCORE = "תוצאת משחק מכבי"
OPPONENT_GAME_SCORE = "תוצאת משחק יריבה"
MACCABI_COACH = "מאמן מכבי"
OPPONENT_COACH = "מאמן יריבה"
REFEREE = "שופט ראשי"
REFEREE_ASSISTERS = "עוזרי שופט"
CROWD = "כמות קהל"
HIGHLIGHTS_VIDEO = "תקציר וידאו"
HIGHLIGHTS_VIDEO2 = "תקציר וידאו2"
FULL_GAME_VIDEO = "משחק מלא"
FULL_GAME_VIDEO2 = "משחק מלא2"
BROADCAST = "גוף שידור"
GAME_SUMMARY = "סיכום משחק"
IS_OVERTIME = "הארכה"
ARTICLE1 = "כתבה1"
ARTICLE2 = "כתבה2"
MACCABI_PLAYERS = 'שחקנים מכבי'
OPPONENT_PLAYERS = 'שחקנים יריבה'
FIRST_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע1'
SECOND_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע2'
THIRD_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע3'
FOURTH_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע4'
FIRST_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה1'
SECOND_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה2'
THIRD_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה3'
FOURTH_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה4'
FIRST_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע1'
SECOND_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע2'
THIRD_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע3'
FOURTH_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע4'
FIRST_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה1'
SECOND_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה2'
THIRD_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה3'
FOURTH_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה4'
FIRST_HALF_MACCABI_POINTS = 'נקודות מכבי חצי1'
SECOND_HALF_MACCABI_POINTS = 'נקודות מכבי חצי2'
FIRST_HALF_OPPONENT_POINTS = 'נקודות יריבה חצי1'
SECOND_HALF_OPPONENT_POINTS = 'נקודות יריבה חצי2'


SHOULD_SAVE = True


def load_basketball_games(input_path: Path) -> list[BasketballGame]:
    games_text = input_path.read_text(encoding='utf-8')
    games = TypeAdapter(list[BasketballGame]).validate_json(games_text)
    return games


def batch_check_existence(site, page_titles: list[str]) -> set[str]:
    """Return the subset of page_titles that already exist on the wiki.

    Uses pywikibot's PreloadingGenerator to batch the existence check into
    one round-trip (mirrors the TS uploader's getExistencePredicate).
    """
    from pywikibot import pagegenerators
    pages = [pw.Page(site, title) for title in page_titles]
    existing: set[str] = set()
    for page in pagegenerators.PreloadingGenerator(pages):
        if page.exists():
            existing.add(page.title())
    return existing


def generate_page_name_from_game(game: BasketballGame) -> str:
    page_name = "{prefix}:{date} {home_team} נגד {away_team} - {competition}".format(prefix=basketball_games_prefix,
                                                                                     date=game.game_date.strftime(
                                                                                         '%d-%m-%Y'),
                                                                                     home_team=game.home_team_name,
                                                                                     away_team=game.away_team_name,
                                                                                     competition=game.competition)

    return page_name


def get_players_events_for_template(players_summary: list[PlayerSummary]) -> str:
    return ",\n".join(player_summary.__maccabipedia__() for player_summary in players_summary).rstrip()

def format_url(game_url: str) -> str:
    main_domain = tldextract.extract(game_url).domain
    return f"[{game_url} עמוד המשחק באתר {main_domain}]"

def __get_football_game_template_with_maccabistats_game_value(game: BasketballGame) -> dict[str, str]:
    template_arguments = {
        GAME_DATE: str(game.game_date.strftime("%d-%m-%Y")),
        # We don't want to upload the hour if it's equal to zero (that an unknown time)
        GAME_HOUR: game.game_date.hour if game.game_date.hour != 0 else '',
        SEASON: game.season,
        COMPETITION: game.competition,
        FIXTURE: game.fixture,
        OPPONENT_NAME: game.opponent_name,
        HOME_OR_AWAY: 'בית' if game.is_home_game else 'חוץ',
        ARENA: game.arena,
        FIRST_QUARTER_MACCABI_POINTS: game.first_quarter_maccabi_points,
        SECOND_QUARTER_MACCABI_POINTS: game.second_quarter_maccabi_points,
        THIRD_QUARTER_MACCABI_POINTS: game.third_quarter_maccabi_points,
        FOURTH_QUARTER_MACCABI_POINTS: game.fourth_quarter_maccabi_points,
        FIRST_OVERTIME_MACCABI_POINTS: game.first_overtime_maccabi_points,
        SECOND_OVERTIME_MACCABI_POINTS: game.second_overtime_maccabi_points,
        THIRD_OVERTIME_MACCABI_POINTS: game.third_overtime_maccabi_points,
        FOURTH_OVERTIME_MACCABI_POINTS: game.fourth_overtime_maccabi_points,
        FIRST_QUARTER_OPPONENT_POINTS: game.first_quarter_opponent_points,
        SECOND_QUARTER_OPPONENT_POINTS: game.second_quarter_opponent_points,
        THIRD_QUARTER_OPPONENT_POINTS: game.third_quarter_opponent_points,
        FOURTH_QUARTER_OPPONENT_POINTS: game.fourth_quarter_opponent_points,
        FIRST_OVERTIME_OPPONENT_POINTS: game.first_overtime_opponent_points,
        SECOND_OVERTIME_OPPONENT_POINTS: game.second_overtime_opponent_points,
        THIRD_OVERTIME_OPPONENT_POINTS: game.third_overtime_opponent_points,
        FOURTH_OVERTIME_OPPONENT_POINTS: game.fourth_overtime_opponent_points,
        FIRST_HALF_MACCABI_POINTS: game.first_half_maccabi_points,
        SECOND_HALF_MACCABI_POINTS: game.second_half_maccabi_points,
        FIRST_HALF_OPPONENT_POINTS: game.first_half_opponent_points,
        SECOND_HALF_OPPONENT_POINTS: game.second_half_opponent_points,
        MACCABI_GAME_SCORE: game.maccabi_points,
        OPPONENT_GAME_SCORE: game.opponent_points,
        MACCABI_COACH: game.maccabi_coach,
        OPPONENT_COACH: game.opponent_coach,
        REFEREE: game.referee,
        REFEREE_ASSISTERS: ", ".join(game.referee_assistants),
        CROWD: game.crowd,
        HIGHLIGHTS_VIDEO: "",
        HIGHLIGHTS_VIDEO2: "",
        FULL_GAME_VIDEO: "",
        FULL_GAME_VIDEO2: "",
        BROADCAST: "",
        GAME_SUMMARY: ""
    }

    if game.has_overtime:
        template_arguments[IS_OVERTIME] = "כן"

    if game.game_url:
        template_arguments[ARTICLE1] = format_url(game.game_url[0])
        if len(game.game_url) > 1:
            template_arguments[ARTICLE2] = format_url(game.game_url[1])

    # Players events should be last:
    template_arguments[MACCABI_PLAYERS] = get_players_events_for_template(game.maccabi_players)
    template_arguments[OPPONENT_PLAYERS] = get_players_events_for_template(game.opponent_players)

    return template_arguments


def render_basketball_game_to_wiki(game: BasketballGame) -> str:
    """Build the {{משחק כדורסל ...}} wiki template text from a BasketballGame.

    Pure function: no I/O, no pywikibot. Used by handle_new_page and tested
    in isolation.
    """
    template = Template(basketball_games_template_name)
    for arg_name, arg_value in __get_football_game_template_with_maccabistats_game_value(game).items():
        template.add(arg_name, arg_value)
    return str(template)


def handle_new_page(game_page: pw.page.Page, game: BasketballGame):
    game_page.text = render_basketball_game_to_wiki(game)


def handle_game(game: BasketballGame, site, skip_existing: bool, existing_titles: set[str]) -> None:
    page_name = generate_page_name_from_game(game)
    if skip_existing and page_name in existing_titles:
        logging.info("SKIP exists: %s", page_name)
        return

    game_page = pw.Page(site, page_name)
    if game_page.exists() and not skip_existing:
        logging.info("OVERWRITE existing page: %s", page_name)

    handle_new_page(game_page, game)

    if not SHOULD_SAVE:
        logging.info("Not saving %s, just showing diff", game_page.title())
        return

    logging.info("Saving %s", game_page.title())
    game_page.save(summary="MaccabiBot - Uploading basketball games")

    logging.info("Prettifying %s", game_page.title())
    prettify_game_page_main_template(game_page)


def upload_basketball_games_to_maccabipedia(games: list[BasketballGame], skip_existing: bool) -> None:
    site = _site()
    page_names = [generate_page_name_from_game(g) for g in games]
    existing = batch_check_existence(site, page_names) if skip_existing else set()
    for game in games:
        handle_game(game, site=site, skip_existing=skip_existing, existing_titles=existing)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload basketball games from a JSON file to MaccabiPedia.",
    )
    parser.add_argument("--input", type=Path, required=True,
                        help="Path to a JSON file produced by crawl_basket_co_il / crawl_euroleague.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip games whose wiki page already exists. Default: overwrite.")
    args = parser.parse_args()

    logging.info("Loading games from %s (skip_existing=%s)", args.input, args.skip_existing)
    games = load_basketball_games(args.input)
    logging.info("Uploading %d games", len(games))
    upload_basketball_games_to_maccabipedia(games, skip_existing=args.skip_existing)
    logging.info("Finished uploading basketball games")


if __name__ == "__main__":
    main()
