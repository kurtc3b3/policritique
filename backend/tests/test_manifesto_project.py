from policritique.manifesto.party_pdfs import build_party_manifesto_sources
from policritique.manifesto.project import (
    extract_corpus_text,
    parse_core_csv,
    published_at_from_yyyymm,
)

SAMPLE_CORE_CSV = """\
country,party,partyname,date,title
51,51320,Labour,201706,For the Many Not the Few
51,51620,Conservative,201706,Forward Together
52,52110,Democratic Unionist Party,201706,DUP Manifesto
"""


def test_parse_core_csv_filters_uk_rows():
    records = parse_core_csv(SAMPLE_CORE_CSV)
    assert len(records) == 3
    assert records[0].query_key == "51320_201706"
    assert records[0].party_name == "Labour"
    assert records[2].party_id == 52110


def test_extract_corpus_text():
    text = extract_corpus_text({"text": "Invest in the NHS.\nBuild more homes."})
    assert text == "Invest in the NHS.\nBuild more homes."


def test_published_at_from_yyyymm():
    assert published_at_from_yyyymm(201706) == "2017-06-01"


def test_build_party_manifesto_sources():
    sources = build_party_manifesto_sources()
    assert len(sources) == 30
    labour_2024 = next(
        source
        for source in sources
        if source.election_date == "2024-07-04" and source.party_name == "Labour"
    )
    assert "labour.org.uk" in labour_2024.source_url
