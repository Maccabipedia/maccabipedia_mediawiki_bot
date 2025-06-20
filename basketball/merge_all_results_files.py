import datetime
import json
import logging
from collections import defaultdict
from pathlib import Path
from pydantic import TypeAdapter

from basketball.basketball_game import BasketballGame
from basketball.teams_names_changer import teams_names_changer

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

BASKETBALL_BASE_FOLDER = Path("C:\\") / "maccabi" / "basketball"
ALL_JSONS_FOLDER = BASKETBALL_BASE_FOLDER / 'all_results'


def _fix_team_names(basketball_game: BasketballGame) -> None:
    if basketball_game.home_team_name in teams_names_changer:
        new_home_team_name = teams_names_changer[basketball_game.home_team_name].change_name(basketball_game)
        if basketball_game.home_team_name != new_home_team_name:
            logging.info(f"Changed home team name from {basketball_game.home_team_name} -> {new_home_team_name} "
                         f"in game date: {basketball_game.game_date}")
            basketball_game.home_team_name = new_home_team_name

    if basketball_game.away_team_name in teams_names_changer:
        new_away_team_name = teams_names_changer[basketball_game.away_team_name].change_name(basketball_game)
        if basketball_game.away_team_name != new_away_team_name:
            logging.info(f"Changed away team name from {basketball_game.away_team_name} -> {new_away_team_name} "
                         f"in game date: {basketball_game.game_date}")
            basketball_game.away_team_name = new_away_team_name


def general_fixes_for_game(basketball_game: BasketballGame) -> None:
    _fix_team_names(basketball_game)


def get_all_games() -> list[BasketballGame]:
    all_games = []
    for result_file in ALL_JSONS_FOLDER.glob("*.json"):
        if changed the name: 'maccabi_euroleague_' in result_file.name:
            games_json = json.loads(result_file.read_text(encoding="utf8"))
            current_source_games = [BasketballGame.from_raw(raw_game) for raw_game in games_json]
        else:
            current_source_games = TypeAdapter(list[BasketballGame]).validate_json(
                result_file.read_text(encoding="utf8"))

        logging.info(f"Added {len(current_source_games)} games from file: {result_file}")
        all_games.extend(current_source_games)

    return all_games


def merge_results_files() -> None:
    games_from_all_sources = get_all_games()

    games_by_date: dict[datetime.datetime, list[BasketballGame]] = defaultdict(list)
    for game in games_from_all_sources:
        general_fixes_for_game(game)
        games_by_date[game.game_date].append(game)

    b = {d: games for d, games in games_by_date.items() if len(games) == 2}

    team_names = {g.home_team_name for g in games_from_all_sources} | {g.away_team_name for g in games_from_all_sources}

    for d, games in b.items():
        first_game, second_game = games[0], games[1]
        if (first_game.home_team_score != second_game.home_team_score) or (first_game.away_team_score != second_game.away_team_score):
            logging.warn(f"Bad scoring! games: {games}")
    a=6


if __name__ == '__main__':
    logging.info("Starting merge results files")
    merge_results_files()
    logging.info("Finished merge results files")
