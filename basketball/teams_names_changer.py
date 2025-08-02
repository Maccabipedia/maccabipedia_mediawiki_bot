from collections import namedtuple
import logging

from basketball.basketball_game import BasketballGame

logger = logging.getLogger(__name__)

_name_by_years = namedtuple("NameByYears", ["better_name", "from_year", "to_year"])


class TeamNameChanger:
    _MIN_DEFAULT_YEAR = 1900
    _MAX_DEFAULT_YEAR = 2100

    def __init__(self, old_name):
        """
        :type old_name: str
        """

        self.better_names = []
        self.old_name = old_name

    def add_better_name(self, better_name, from_year=_MIN_DEFAULT_YEAR, to_year=_MAX_DEFAULT_YEAR):
        """
        Adding a better name for this team name, using the years range.
        By default the years range will be "all time range".

        :return: self, To allow using obj.add_better_name(...).add_better_name(...)
        """

        self.better_names.append(_name_by_years(better_name=better_name, from_year=from_year, to_year=to_year))
        return self

    def change_name(self, game: BasketballGame):
        """
        Changing the old_name to a better name (by years range).
        :param game: use the game to get the years.

        :return: team best name (new_name) or ValueError if cant find any.
        """

        for team_name_by_years in self.better_names:
            if team_name_by_years.from_year <= game.game_date.year <= team_name_by_years.to_year:
                return team_name_by_years.better_name

        raise ValueError(
            f"Cant find any better name using the years range: {team_name_by_years.from_year}-{team_name_by_years.to_year},"
            f" game year: {game.date.year}")

    @property
    def current_name(self) -> str:
        if not self.better_names:
            return self.old_name

        return max(self.better_names, key=lambda i: i.from_year).better_name


_teams_names = [
    # Just replace team name (without years range):
    ## In Israel
    TeamNameChanger('מכבי ת"א').add_better_name("מכבי תל אביב"),
    TeamNameChanger('מכבי אלקטרה').add_better_name("מכבי תל אביב"),
    TeamNameChanger('ראשל"צ').add_better_name("מכבי ראשון לציון"),
    TeamNameChanger('ראשון לציון').add_better_name("מכבי ראשון לציון"),
    TeamNameChanger('פנדור ראשל"צ').add_better_name("מכבי ראשון לציון"),
    TeamNameChanger("אופיצי ראשל\"צ").add_better_name("מכבי ראשון לציון"),
    TeamNameChanger('מכבי ר"ג').add_better_name("מכבי רמת גן"),
    TeamNameChanger('מכבי צפון ת"א').add_better_name("מכבי צפון תל אביב"),
    TeamNameChanger('מכבי דרום ת"א').add_better_name("מכבי דרום תל אביב"),
    TeamNameChanger('מכבי פ"ת').add_better_name("מכבי פתח תקווה"),
    TeamNameChanger('מכבי פ``ת').add_better_name("מכבי פתח תקווה"),
    TeamNameChanger('מכבי פתח-תקווה').add_better_name("מכבי פתח תקווה"),
    TeamNameChanger('מכבי בזן חיפה').add_better_name("מכבי חיפה"),
    TeamNameChanger('מ.כ חיפה').add_better_name("מכבי חיפה"),
    TeamNameChanger('מכבי חיפה היט').add_better_name("מכבי חיפה"),
    TeamNameChanger('Hunter חיפה').add_better_name("מכבי חיפה"),
    TeamNameChanger('מגדל י-ם').add_better_name("הפועל ירושלים"),
    TeamNameChanger('הפועל י-ם').add_better_name("הפועל ירושלים"),
    TeamNameChanger('הפועל  י-ם').add_better_name("הפועל ירושלים"),
    TeamNameChanger('יונט חולון').add_better_name("הפועל חולון"),
    TeamNameChanger('UNET חולון').add_better_name("הפועל חולון"),
    TeamNameChanger('הפועל ת"א').add_better_name("הפועל תל אביב"),
    TeamNameChanger('הפועל SP ת"א').add_better_name("הפועל תל אביב"),
    TeamNameChanger('SCE אשדוד').add_better_name("מכבי אשדוד"),
    TeamNameChanger('ביתר י"ם').add_better_name("ביתר ירושלים"),

    ## Not in Israel
    TeamNameChanger('אוניקאחה מלאגה').add_better_name("אוניקאחה מאלגה"),
    TeamNameChanger('פנאתנייקוס').add_better_name("פנאתינאיקוס"),
    TeamNameChanger('פנאתינייקוס').add_better_name("פנאתינאיקוס"),
    TeamNameChanger('Aris BC').add_better_name("אריס סלוניקי"),
    TeamNameChanger('חובנטוד באדלונה').add_better_name("חובנטוד בדאלונה"),
    TeamNameChanger("ז'אלגריס קובנה").add_better_name("ז'לגיריס קובנה"),
    TeamNameChanger("אפס פילזן איסטנבול").add_better_name("אפס פילזן"),

    # Replace teams names by year range:

    TeamNameChanger("מכבי רמת עמידר").add_better_name("מכבי רמת עמידר", 1957, 2005).add_better_name("הכח עמידר רמת גן",
                                                                                                    from_year=2005)
]

# Make that a dictionary:
teams_names_changer = {name_changer.old_name: name_changer for name_changer in _teams_names}
