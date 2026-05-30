from policritique.parliament.members_api import parse_member_summary


def test_parse_member_summary():
    summary = parse_member_summary(
        {
            "id": 172,
            "nameListAs": "Abbott, Ms Diane",
            "nameDisplayAs": "Ms Diane Abbott",
            "nameFullTitle": "Rt Hon Diane Abbott MP",
            "gender": "F",
            "latestParty": {"name": "Independent", "abbreviation": "Ind"},
            "latestHouseMembership": {
                "membershipFrom": "Hackney North and Stoke Newington",
                "membershipStartDate": "1987-06-11T00:00:00",
                "membershipEndDate": None,
                "membershipStatus": {"statusIsActive": True},
            },
        }
    )

    assert summary is not None
    assert summary.parliament_member_id == 172
    assert summary.party_name == "Independent"
    assert summary.constituency_name == "Hackney North and Stoke Newington"
    assert summary.membership_start_date == "1987-06-11"
    assert summary.is_current is True
