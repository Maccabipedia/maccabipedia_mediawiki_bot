import argparse
import logging
from pathlib import Path

import pywikibot as pw
import tldextract
from mwparserfromhell.nodes.template import Template
from pydantic import TypeAdapter

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.common.page_names import build_basketball_game_page_name
from maccabipediabot.common.prettify_games_pages import prettify_game_page_main_template
from maccabipediabot.common.wiki_login import get_site

# === Page metadata ===
BASKETBALL_GAMES_TEMPLATE_NAME = "משחק כדורסל"
BASKETBALL_GAMES_PAGE_PREFIX = "כדורסל"
SHOULD_SAVE = True  # safety global; --dry-run is the public per-run override

# === Source URL → Hebrew label for the כתבה1 reference field ===
_SOURCE_LABELS = {
    "basket.co.il": "מנהלת ליגת העל בכדורסל",
    "euroleaguebasketball.net": "היורוליג",
}

# === Wiki template parameter names (HE) ===
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
MACCABI_PLAYERS = "שחקנים מכבי"
OPPONENT_PLAYERS = "שחקנים יריבה"
FIRST_QUARTER_MACCABI_POINTS = "נקודות מכבי רבע1"
SECOND_QUARTER_MACCABI_POINTS = "נקודות מכבי רבע2"
THIRD_QUARTER_MACCABI_POINTS = "נקודות מכבי רבע3"
FOURTH_QUARTER_MACCABI_POINTS = "נקודות מכבי רבע4"
FIRST_OVERTIME_MACCABI_POINTS = "נקודות מכבי הארכה1"
SECOND_OVERTIME_MACCABI_POINTS = "נקודות מכבי הארכה2"
THIRD_OVERTIME_MACCABI_POINTS = "נקודות מכבי הארכה3"
FOURTH_OVERTIME_MACCABI_POINTS = "נקודות מכבי הארכה4"
FIRST_QUARTER_OPPONENT_POINTS = "נקודות יריבה רבע1"
SECOND_QUARTER_OPPONENT_POINTS = "נקודות יריבה רבע2"
THIRD_QUARTER_OPPONENT_POINTS = "נקודות יריבה רבע3"
FOURTH_QUARTER_OPPONENT_POINTS = "נקודות יריבה רבע4"
FIRST_OVERTIME_OPPONENT_POINTS = "נקודות יריבה הארכה1"
SECOND_OVERTIME_OPPONENT_POINTS = "נקודות יריבה הארכה2"
THIRD_OVERTIME_OPPONENT_POINTS = "נקודות יריבה הארכה3"
FOURTH_OVERTIME_OPPONENT_POINTS = "נקודות יריבה הארכה4"
FIRST_HALF_MACCABI_POINTS = "נקודות מכבי חצי1"
SECOND_HALF_MACCABI_POINTS = "נקודות מכבי חצי2"
FIRST_HALF_OPPONENT_POINTS = "נקודות יריבה חצי1"
SECOND_HALF_OPPONENT_POINTS = "נקודות יריבה חצי2"

# Optional period scores: skip if None so unused OT / half slots don't litter
# the page source with empty placeholders.
_OPTIONAL_PERIOD_KEYS = frozenset([
    FIRST_OVERTIME_MACCABI_POINTS, SECOND_OVERTIME_MACCABI_POINTS,
    THIRD_OVERTIME_MACCABI_POINTS, FOURTH_OVERTIME_MACCABI_POINTS,
    FIRST_OVERTIME_OPPONENT_POINTS, SECOND_OVERTIME_OPPONENT_POINTS,
    THIRD_OVERTIME_OPPONENT_POINTS, FOURTH_OVERTIME_OPPONENT_POINTS,
    FIRST_HALF_MACCABI_POINTS, SECOND_HALF_MACCABI_POINTS,
    FIRST_HALF_OPPONENT_POINTS, SECOND_HALF_OPPONENT_POINTS,
])


def load_basketball_games(input_path: Path) -> list[BasketballGame]:
    return TypeAdapter(list[BasketballGame]).validate_json(
        input_path.read_text(encoding="utf-8")
    )


def generate_page_name_from_game(game: BasketballGame) -> str:
    return build_basketball_game_page_name(
        game_date=game.game_date,
        home_team=game.home_team_name,
        away_team=game.away_team_name,
        competition=game.competition,
    )


def get_players_events_for_template(players_summary: list[PlayerSummary]) -> str:
    return ",\n".join(player.__maccabipedia__() for player in players_summary).rstrip()


def format_url(game_url: str) -> str:
    extracted = tldextract.extract(game_url)
    label = _SOURCE_LABELS.get(extracted.top_domain_under_public_suffix, extracted.domain)
    return f"[{game_url} עמוד המשחק באתר {label}]"


def _get_basketball_template_arguments(game: BasketballGame) -> dict[str, str]:
    template_arguments = {
        GAME_DATE: str(game.game_date.strftime("%d-%m-%Y")),
        # Emit full HH:MM. Skip the field for midnight (unknown game time).
        GAME_HOUR: game.game_date.strftime("%H:%M") if (game.game_date.hour or game.game_date.minute) else "",
        SEASON: game.season,
        COMPETITION: game.competition,
        FIXTURE: game.fixture,
        OPPONENT_NAME: game.opponent_name,
        HOME_OR_AWAY: "בית" if game.is_home_game else "חוץ",
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
        GAME_SUMMARY: "",
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


def render_basketball_game_to_wikitext(game: BasketballGame) -> str:
    """Build the {{משחק כדורסל ...}} wiki template text from a BasketballGame.
    Pure function: no I/O, no pywikibot."""
    template = Template(BASKETBALL_GAMES_TEMPLATE_NAME)
    for arg_name, arg_value in _get_basketball_template_arguments(game).items():
        if arg_name in _OPTIONAL_PERIOD_KEYS and arg_value in (None, ""):
            continue
        template.add(arg_name, arg_value)
    return str(template)


def upload_game_to_page(page, game: BasketballGame, *, dry_run: bool) -> None:
    """Render the game wikitext into `page` and save (unless dry_run / SHOULD_SAVE off)."""
    page.text = render_basketball_game_to_wikitext(game)

    if dry_run or not SHOULD_SAVE:
        logging.info("DRY-RUN: not saving %s", page.title())
        return

    logging.info("Saving %s", page.title())
    page.save(summary="MaccabiBot - Uploading basketball games")

    logging.info("Prettifying %s", page.title())
    prettify_game_page_main_template(page)


def upload_basketball_games_to_maccabipedia(games: list[BasketballGame], *,
                                            skip_existing: bool, dry_run: bool) -> None:
    site = get_site()
    if not dry_run:
        logging.warning("LIVE MODE: pages will be written to MaccabiPedia")
    for game in games:
        page_name = generate_page_name_from_game(game)
        page = pw.Page(site, page_name)
        if page.exists():
            if skip_existing:
                logging.info("SKIP exists: %s", page_name)
                continue
            logging.info("OVERWRITE existing page: %s", page_name)
        upload_game_to_page(page, game, dry_run=dry_run)


def main() -> None:
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Upload basketball games from a JSON file to MaccabiPedia.",
    )
    parser.add_argument("--input", type=Path, required=True,
                        help="Path to a JSON file produced by crawl_basket_co_il / crawl_euroleague.")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip games whose wiki page already exists. Default: overwrite.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build wiki text but don't save to MaccabiPedia.")
    args = parser.parse_args()

    logging.info("Loading games from %s (skip_existing=%s, dry_run=%s)",
                 args.input, args.skip_existing, args.dry_run)
    games = load_basketball_games(args.input)
    logging.info("Uploading %d games", len(games))
    upload_basketball_games_to_maccabipedia(
        games, skip_existing=args.skip_existing, dry_run=args.dry_run,
    )
    logging.info("Finished uploading basketball games")


if __name__ == "__main__":
    main()
