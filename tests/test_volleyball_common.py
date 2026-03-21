from volleyball_common import TEAM_NAMES_REPLACER, STADIUMS_NAMES


def test_team_names_replacer_is_not_empty():
    assert len(TEAM_NAMES_REPLACER) > 0


def test_team_names_replacer_maccabi_yedaim():
    assert TEAM_NAMES_REPLACER["מכבי יעדים תל אביב"] == "מכבי תל אביב"


def test_team_names_replacer_hapoel_galil():
    assert TEAM_NAMES_REPLACER['הפועל "גליל" מטה אשר עכו'] == 'הפועל מטה אשר/עכו'


def test_team_names_replacer_values_have_no_sponsor_names():
    """Canonical names must not contain sponsorship prefixes like SVA or יעדים."""
    for canonical in TEAM_NAMES_REPLACER.values():
        assert "SVA" not in canonical
        assert "יעדים" not in canonical


def test_stadiums_names_is_not_empty():
    assert len(STADIUMS_NAMES) > 0


def test_stadiums_names_hadar_yosef():
    assert STADIUMS_NAMES["מרכז הרב ספורט ת-א"] == "הדר יוסף"
