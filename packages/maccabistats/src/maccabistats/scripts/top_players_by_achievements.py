from collections import Counter, defaultdict

import json
from pathlib import Path
from pprint import pformat
from progressbar import ProgressBar
from typing import Dict, Set

from maccabistats import load_from_maccabipedia_source
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

_DESCRIPTION_WHICH_MEANS_MACCABI_WON_TITLE = ['מקום 1', 'זכיה']

BASE_FOLDER = Path(r"C:\maccabipedia\infographics\titles")


# To check titles with coaches - uncomment line 42
# To check specific competition titles, uncomment line 28
# This query can generate the achievements.json:
# https://www.maccabipedia.co.il/api.php?action=cargoquery&tables=Achievements&format=json&fields=ConnectedCompID,Season,Achievement&limit=1000

def extract_seasons_with_titles() -> Dict[str, int]:
    achievements_file_path = Path(__file__).absolute().parent / 'achievements.json'
    titles_from_cargo = json.loads(achievements_file_path.read_text(encoding='utf8'))
    titles_from_cargo = titles_from_cargo['cargoquery']

    # Season may occur more than one (means maccabi won more than onc title)
    titles = [title_row['title']['Season'] for title_row in titles_from_cargo if
              title_row['title']['Achievement'] in _DESCRIPTION_WHICH_MEANS_MACCABI_WON_TITLE
              # Uncomment to check only specific titles
              #and int(title_row['title']['ConnectedCompID']) == 1
              ]

    titles_count_by_year = defaultdict(int, Counter(titles))
    return titles_count_by_year


def generate_season_to_played_players(maccabi_games: MaccabiGamesStats) -> Dict[str, Set[str]]:
    print(f'Creating the list of played players for all seasons')

    pbar = ProgressBar()
    seasons_to_players = defaultdict(set)

    for game in pbar(maccabi_games):
        seasons_to_players[game.season].update(game.maccabi_team.played_players_with_amount.keys())
        seasons_to_players[game.season].add(game.maccabi_team.coach)

    return seasons_to_players


def find_top_players_by_achievements(maccabi_games: MaccabiGamesStats, titles_by_year: Dict[str, int]) -> Counter:
    season_to_players = generate_season_to_played_players(maccabi_games)

    players_to_titles = defaultdict(int)

    for season, won_players in season_to_players.items():
        if season not in titles_by_year:
            continue

        current_season_titles_amount = titles_by_year[season]
        print(f'Checking season: {season}, {len(won_players)} players won {current_season_titles_amount} titles')
        for player_name in won_players:
            players_to_titles[player_name] += current_season_titles_amount

    return Counter(players_to_titles)


if __name__ == '__main__':
    games = load_from_maccabipedia_source().official_games
    all_titles = extract_seasons_with_titles()

    top_players = find_top_players_by_achievements(games, all_titles)

    # (BASE_FOLDER / "top_players_achievements.json").write_text(json.dumps(top_players))
    (BASE_FOLDER / "top_players_and_coaches_achievements.json").write_text(json.dumps(top_players))

    print(f'\n\nPlayers sorted by titles amount: {pformat(top_players.most_common(50))}')
    a = 6
