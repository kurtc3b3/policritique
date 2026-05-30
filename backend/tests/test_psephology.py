from policritique.parliament.psephology import (
    candidate_full_name,
    parse_candidacies_csv,
    winning_candidate_keys,
)

SAMPLE_CSV = """\
ONS ID,Constituency name,Country name,Party name,Party abbreviation,\
Electoral Commission party ID,Candidate first name,Candidate surname,Votes,Share
E14001063,Example East,England,Labour,Lab,PP53,Jane,Smith,18000,0.45
E14001063,Example East,England,Conservative,Con,PP52,John,Doe,15000,0.375
E14001064,Example West,England,Conservative,Con,PP52,Alice,Jones,12000,0.50
E14001064,Example West,England,Labour,Lab,PP53,Bob,Brown,11000,0.458
"""


def test_parse_candidacies_csv():
    rows = parse_candidacies_csv(SAMPLE_CSV)
    assert len(rows) == 4
    assert rows[0].constituency_name == "Example East"
    assert rows[0].ec_party_id == "PP53"
    assert rows[0].votes == 18000
    assert rows[0].vote_share == 0.45


def test_winning_candidate_keys():
    rows = parse_candidacies_csv(SAMPLE_CSV)
    winners = winning_candidate_keys(rows)
    assert ("E14001063", "Example East", "Jane Smith") in winners
    assert ("E14001064", "Example West", "Alice Jones") in winners
    assert len(winners) == 2


def test_candidate_full_name():
    assert candidate_full_name("Jane", "Smith") == "Jane Smith"


HEADERLESS_CSV = """\
W07000049,W92000004,Aberavon,West Glamorgan,Wales,Wales,County,Labour,Lab,PP53,15,,\
Hywel,Francis,Male,Yes,Yes,1382,16073,0.519187,-0.081
W07000049,W92000004,Aberavon,West Glamorgan,Wales,Wales,County,Conservative,Con,PP52,4,,\
Caroline,Jones,Female,No,No,,4411,0.142483,0.041
"""


def test_parse_headerless_candidacies_csv():
    rows = parse_candidacies_csv(HEADERLESS_CSV)
    assert len(rows) == 2
    assert rows[0].constituency_name == "Aberavon"
    assert rows[0].candidate_first_name == "Hywel"
    assert rows[0].votes == 16073
