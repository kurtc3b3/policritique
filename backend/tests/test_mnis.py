from policritique.parliament.mnis import (
    contacts_from_mnis_address,
    parse_mnis_addresses_payload,
)

SAMPLE_MNIS_PAYLOAD = {
    "Members": {
        "Member": [
            {
                "@Member_Id": "172",
                "DisplayAs": "Ms Diane Abbott",
                "Addresses": {
                    "Address": [
                        {
                            "Type": "Parliamentary office",
                            "IsPreferred": "False",
                            "IsPhysical": "True",
                            "Address1": "House of Commons",
                            "Address5": "London",
                            "Postcode": "SW1A 0AA",
                            "Phone": "020 7219 4426",
                            "Email": "diane.abbott.office@parliament.uk",
                        },
                        {
                            "Type": "X (formerly Twitter)",
                            "IsPreferred": "False",
                            "IsPhysical": "False",
                            "Address1": "https://twitter.com/HackneyAbbott",
                        },
                    ]
                },
            }
        ]
    }
}


def test_parse_mnis_addresses_payload():
    contacts_by_id = parse_mnis_addresses_payload(SAMPLE_MNIS_PAYLOAD)
    assert 172 in contacts_by_id
    contacts = contacts_by_id[172]
    types = {contact.contact_type for contact in contacts}
    assert "email" in types
    assert "phone" in types
    assert "parliamentary_office" in types
    assert "x_formerly_twitter" in types


def test_contacts_from_mnis_address_physical():
    contacts = contacts_from_mnis_address(
        {
            "Type": "Constituency office",
            "IsPreferred": "True",
            "IsPhysical": "True",
            "Address1": "1 High Street",
            "Postcode": "E8 1AA",
            "Email": "mp@example.org",
        }
    )
    assert len(contacts) == 2
    assert contacts[0].contact_type == "email"
    assert contacts[1].contact_type == "constituency_office"
    assert contacts[1].is_primary is True
