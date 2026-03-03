def test_kipris_client_parses_response():
    """Client should parse KIPRISplus XML/JSON response into patent dicts."""
    from app.utils.kipris_client import parse_kipris_patents

    mock_data = {
        "response": {
            "header": {
                "successYN": "Y",
                "resultCode": "00",
                "resultMsg": "정상",
            },
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
            },
        }
    }
    patents = parse_kipris_patents(mock_data)
    assert len(patents) == 2
    assert patents[0]["title"] == "방열 구조체"
    assert patents[0]["abstract"] == "본 발명은 방열 구조에 관한 것이다."
    assert patents[0]["application_number"] == "10-2024-0001234"


def test_kipris_client_handles_empty_response():
    from app.utils.kipris_client import parse_kipris_patents

    empty_data = {
        "response": {
            "header": {"successYN": "Y", "resultCode": "00", "resultMsg": "정상"},
            "body": {"items": {"item": []}},
        }
    }
    patents = parse_kipris_patents(empty_data)
    assert patents == []


def test_kipris_client_handles_error_response():
    """Client should return empty list when API returns an error (e.g., expired key)."""
    from app.utils.kipris_client import parse_kipris_patents

    error_data = {
        "response": {
            "header": {
                "successYN": "N",
                "resultCode": "10",
                "resultMsg": "상품의 사용기한이 만료되었습니다.",
            }
        }
    }
    patents = parse_kipris_patents(error_data)
    assert patents == []
