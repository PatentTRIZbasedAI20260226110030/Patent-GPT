def test_triz_classifier_returns_principles():
    """Classifier should return a list of TRIZPrinciple objects."""
    from app.services.triz_classifier import parse_principles_response

    mock_response = (
        '[{"number": 1, "name_en": "Segmentation", "name_ko": "분할",'
        ' "description": "Divide an object into independent parts.",'
        ' "matching_score": 0.92},'
        ' {"number": 7, "name_en": "Nesting", "name_ko": "포개기",'
        ' "description": "Place one object inside another.",'
        ' "matching_score": 0.78}]'
    )

    result = parse_principles_response(mock_response)
    assert len(result) == 2
    assert result[0].number == 1
    assert result[0].matching_score == 0.92
    assert result[1].number == 7
    assert result[1].matching_score == 0.78


def test_parse_principles_handles_invalid_json():
    from app.services.triz_classifier import parse_principles_response

    result = parse_principles_response("not valid json")
    assert result == []
