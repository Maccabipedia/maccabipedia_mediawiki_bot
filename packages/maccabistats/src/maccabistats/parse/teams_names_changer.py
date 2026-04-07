from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

_name_by_years = namedtuple("NameByYears", ["better_name", "from_year", "to_year"])


class TeamNameChanger(object):
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

    def change_name(self, game):
        """
        Changing the old_name to a better name (by years range).
        :param game: use the game to get the years.

        :return: team best name (new_name) or ValueError if cant find any.
        """

        for team_name_by_years in self.better_names:
            if team_name_by_years.from_year <= game.date.year <= team_name_by_years.to_year:
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

    TeamNameChanger("עירוני קש").add_better_name("עירוני קריית שמונה"),
    TeamNameChanger("עירוני קרית שמונה").add_better_name("עירוני קריית שמונה"),
    TeamNameChanger("הפועל כפס").add_better_name("הפועל כפר סבא"),
    TeamNameChanger("הפועל תא").add_better_name("הפועל תל אביב"),
    TeamNameChanger("הפועל פת").add_better_name("הפועל פתח תקווה"),
    TeamNameChanger("מ.ס אשדוד").add_better_name("מ.ס. אשדוד"),
    TeamNameChanger("הפועל בש").add_better_name("הפועל באר שבע"),
    TeamNameChanger("הכח עמידר רג").add_better_name("הכח מכבי עמידר רמת גן"),
    TeamNameChanger("מכבי פת").add_better_name("מכבי פתח תקווה"),
    TeamNameChanger("אחי נצרת").add_better_name("מכבי אחי נצרת"),
    TeamNameChanger("עירוני רמהש").add_better_name("הפועל ניר רמת השרון"),
    TeamNameChanger("הפועל רמת השרון").add_better_name("הפועל ניר רמת השרון"),
    TeamNameChanger("ביתר נתניה").add_better_name('בית"ר נתניה'),
    TeamNameChanger("'גראסהופרס'").add_better_name("גראסהופרס ציריך"),
    TeamNameChanger("בני לוד").add_better_name("הפועל בני לוד"),
    TeamNameChanger("זלגיריס וילנה").add_better_name("ז'לגיריס וילנה"),
    TeamNameChanger("ז'לז'ניצאר").add_better_name("ז'לייזניצ'אר סרייבו"),
    TeamNameChanger("מאלמו").add_better_name("מאלמה"),
    TeamNameChanger("מאריבור").add_better_name("מריבור"),
    TeamNameChanger("טרנצ'ין").add_better_name("אס טרנצ'ין"),
    TeamNameChanger("בשיקטאש").add_better_name("בשיקטש"),
    TeamNameChanger("פנדורי").add_better_name("פאנדורי"),
    TeamNameChanger("מיסורה הודו").add_better_name("מיסורה"),
    TeamNameChanger("ואלטה").add_better_name("ולטה"),
    TeamNameChanger("יאנג צ'י ד.קוריאה").add_better_name("יאנגצ'יי"),
    TeamNameChanger("קלאב ברוז").add_better_name("קלאב ברוז"),
    TeamNameChanger("דיוסגיורי").add_better_name("דיושגיור"),
    TeamNameChanger("מוגרן").add_better_name("מוגרן בודווה"),
    TeamNameChanger("דואיסבורג").add_better_name("דיסבורג"),
    TeamNameChanger("פאנאתינאיקוס").add_better_name("פנאתינייקוס"),
    TeamNameChanger("פנג'אב הודו").add_better_name("משטרת פנג'אב"),
    TeamNameChanger("קאיירט אלמטי").add_better_name("קאיראט אלמטי"),
    TeamNameChanger("באזל").add_better_name("פ.צ. באזל"),
    TeamNameChanger("ה.י.ק הלסינקי").add_better_name("ה.י.ק. הלסינקי"),
    TeamNameChanger("לבאדיה טאלין").add_better_name("לבדיה טאלין"),
    TeamNameChanger("פרנקפורט").add_better_name("איינטרכט פרנקפורט"),
    TeamNameChanger("דפורטיבה מניירה").add_better_name("דפורטיבו מינרה"),
    TeamNameChanger("טיראנה").add_better_name("קיי אף טירנה"),
    TeamNameChanger("פ.צ ציריך").add_better_name("פ.צ. ציריך"),
    TeamNameChanger("דונדלק").add_better_name("דאנדלק"),
    TeamNameChanger("קראסנודר").add_better_name("קרסנודאר"),
    TeamNameChanger("מ.ס.ק זילינה").add_better_name("מ.ש.ק. ז'ילינה"),
    TeamNameChanger("ווינר ניושטאדט").add_better_name("וינר נוישטאדט"),
    TeamNameChanger("הפועל קרית אונו").add_better_name("הפועל קריית אונו"),
    TeamNameChanger("הפועל קרית חיים").add_better_name("הפועל קריית חיים"),
    TeamNameChanger("ק.ב קופנהאגן").add_better_name("קייבי"),
    TeamNameChanger("פ.ב.ק קובנה").add_better_name("פ.ב.ק. קובנה"),
    TeamNameChanger("דונייסטה סטראדה").add_better_name("דונאיסקה סטרדה"),
    TeamNameChanger("ק.ר רייקיאוויק").add_better_name("קיי.אר. רייקיאוויק"),
    TeamNameChanger("פוליס קלאב בגדד").add_better_name("אל שורטה"),
    TeamNameChanger("פריס סן ז'רמן").add_better_name("פריז סן ז'רמן"),
    TeamNameChanger("היברניאנס").add_better_name("פאולה היברניאנס"),
    TeamNameChanger("זניט סט. פטרסבורג").add_better_name("זניט סנקט פטרבורג"),
    TeamNameChanger("הפועל טובא").add_better_name("הפועל בני טובא"),
    TeamNameChanger("פראק מלזיה").add_better_name("פראק"),
    TeamNameChanger("חאזאר לנקאראן").add_better_name("חזאר לנקראן"),
    TeamNameChanger("הפועל אום אל פאחם").add_better_name("הפועל אום אל פחם"),

    # Replace teams names by year range:

    TeamNameChanger("מכבי רמת עמידר").add_better_name("מכבי רמת עמידר", 1957, 2005).add_better_name("הכח עמידר רמת גן",
                                                                                                    from_year=2005),
    TeamNameChanger("מכבי קרית גת").add_better_name("מכבי קריית גת", 1900, 2013).add_better_name("מכבי עירוני קריית גת",
                                                                                                 from_year=2013),
    TeamNameChanger('בית"ר שמשון תל אביב').add_better_name('בית"ר שמשון תל אביב', 2000, 2011).add_better_name(
        "שמשון תל אביב", from_year=2011),
    TeamNameChanger("שמשון תא").add_better_name("שמשון תל אביב", 1949, 2000).add_better_name('בית"ר שמשון תל אביב',
                                                                                             2000, 2011)
        .add_better_name("שמשון תל אביב", from_year=2011),
    TeamNameChanger("שמשון תל אביב").add_better_name("שמשון תל אביב", 1949, 2000).add_better_name('בית"ר שמשון תל אביב',
                                                                                                  2000, 2011)
        .add_better_name("שמשון תל אביב", from_year=2011),
    TeamNameChanger("צפרירים חולון").add_better_name("הפועל חולון", 1940, 1985).add_better_name("הפועל צפרירים חולון",
                                                                                                from_year=1985),
    TeamNameChanger("עירוני ראשלצ").add_better_name("הפועל ראשון לציון", 1928, 1992).add_better_name(
        "הפועל עירוני ראשון לציון", 1992, 2008).add_better_name("הפועל ראשון לציון", from_year=2008),
    TeamNameChanger("עירוני ראשון לציון").add_better_name("הפועל ראשון לציון", 1928, 1992).add_better_name(
        "הפועל עירוני ראשון לציון", 1992, 2008).add_better_name("הפועל ראשון לציון", from_year=2008),
    TeamNameChanger("הפועל ראשון לציון").add_better_name("הפועל ראשון לציון", 1928, 1992).add_better_name(
        "הפועל עירוני ראשון לציון", 1992, 2008).add_better_name("הפועל ראשון לציון", from_year=2008),
    TeamNameChanger("הפועל עירוני ראשון לציון").add_better_name("הפועל עירוני ראשון לציון", 1992, 2008)
        .add_better_name("הפועל ראשון לציון", from_year=2008),
    TeamNameChanger("הפועל רג").add_better_name("הפועל רמת גן", 1927, 1956).add_better_name("הפועל רמת גן גבעתיים",
                                                                                            from_year=1956),
    TeamNameChanger("הפועל רמת גן").add_better_name("הפועל רמת גן", 1927, 1956).add_better_name("הפועל רמת גן גבעתיים",
                                                                                                from_year=1956),
    TeamNameChanger("ביתר ירושלים").add_better_name('בית"ר ירושלים', 1936, 1947).add_better_name("נורדיה ירושלים", 1946,
                                                                                                 1947)
        .add_better_name('בית"ר ירושלים', from_year=1948),
    TeamNameChanger("הפועל חולון").add_better_name("הפועל חולון", 1940, 1985).add_better_name("הפועל צפרירים חולון",
                                                                                              from_year=1985),
    TeamNameChanger("מכבי חיפה").add_better_name("מכבי הגיבור חיפה", 1900, 1940).add_better_name("מכבי חיפה",
                                                                                                 from_year=1940),
    TeamNameChanger("הפועל אשדוד").add_better_name("הפועל אשדוד", 1957, 1999).add_better_name("מ.ס. אשדוד",
                                                                                              from_year=2000),
    TeamNameChanger("הכח רג").add_better_name("הכח תל אביב", 1934, 1959).add_better_name("הכח מכבי רמת גן", 1959, 2005)
        .add_better_name("הכח עמידר רמת גן", from_year=2005),
    TeamNameChanger("הכח עמידר רג").add_better_name("הכח תל אביב", 1934, 1959).add_better_name("הכח מכבי רמת גן", 1959,
                                                                                               2005)
        .add_better_name("הכח עמידר רמת גן", from_year=2005),
    TeamNameChanger("הכח מכבי עמידר רמת גן").add_better_name("הכח תל אביב", 1934, 1959).add_better_name(
        "הכח מכבי רמת גן", 1959, 2005)
        .add_better_name("הכח עמידר רמת גן", from_year=2005),
    TeamNameChanger("הכח רג").add_better_name("הכח תל אביב", 1934, 1959).add_better_name("הכח מכבי רמת גן", 1959, 2005)
        .add_better_name("הכח עמידר רמת גן", from_year=2005),
    TeamNameChanger("הפועל ירוחם").add_better_name("הפועל ירוחם", to_year=2017).add_better_name("מ.ס. הפועל ירוחם",
                                                                                                from_year=2017),
    TeamNameChanger("מכבי רמת גן").add_better_name("מכבי רמת גן", to_year=1959).add_better_name("הכח מכבי רמת גן", 1959,
                                                                                                2005)
        .add_better_name("הכח עמידר רמת גן", from_year=2005),
    TeamNameChanger("עירוני אשדוד").add_better_name("מכבי עירוני אשדוד", 1961, 2000).add_better_name("מ.ס. אשדוד",
                                                                                                     from_year=2000),
    TeamNameChanger('בית"ר תל אביב/רמלה').add_better_name('בית"ר תל אביב', 1924, 2011).add_better_name(
        'בית"ר תל אביב רמלה', from_year=2011),
    TeamNameChanger('ביתר תא').add_better_name('בית"ר תל אביב', 1924, 2011).add_better_name('בית"ר תל אביב רמלה',
                                                                                            from_year=2011),
    TeamNameChanger("הכח תל אביב").add_better_name("הכח תל אביב", 1934, 1959).add_better_name("הכח עמידר רמת גן",
                                                                                              from_year=2005),
]

# Make that a dictionary:
teams_names_changer = {name_changer.old_name: name_changer for name_changer in _teams_names}
