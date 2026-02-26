def test_kipris_client_parses_response():
    """Client should parse KIPRISplus XML/JSON response into patent dicts."""
    from app.utils.kipris_client import parse_kipris_patents

    mock_data = {
        "response": {
            "body": {
                "items": {
                    "item": [
                        {
                            "inventionTitle": "방열 구조체",
                            "astrtCont": "본 발명은 방열 구조에 관한 것이다.",
                            "applicationNumber": "10-2024-0001234",
                        },
                        {
                            "inventionTitle": "열전도 필름",
                            "astrtCont": "열전도 필름에 관한 발명이다.",
                            "applicationNumber": "10-2024-0005678",
                        },
                    ]
                }
            }
        }
    }
    patents = parse_kipris_patents(mock_data)
    assert len(patents) == 2
    assert patents[0]["title"] == "방열 구조체"
    assert patents[0]["abstract"] == "본 발명은 방열 구조에 관한 것이다."
    assert patents[0]["application_number"] == "10-2024-0001234"


def test_kipris_client_handles_empty_response():
    from app.utils.kipris_client import parse_kipris_patents

    empty_data = {"response": {"body": {"items": {"item": []}}}}
    patents = parse_kipris_patents(empty_data)
    assert patents == []
