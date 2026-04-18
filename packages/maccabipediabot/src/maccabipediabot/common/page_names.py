from datetime import date


def build_game_page_name(prefix: str, game_date: date, home_team: str,
                         away_team: str, competition: str) -> str:
    formatted_date = game_date.strftime('%d-%m-%Y')
    return f'{prefix}:{formatted_date} {home_team} נגד {away_team} - {competition}'
