"""Tests for TRIZ Contradiction Matrix models and lookup."""

from app.models.triz import (
    ContradictionMatrix,
    EngineeringParameter,
    load_contradiction_matrix,
    load_triz_principles,
)
from app.services.triz_classifier import _build_matrix_context, parse_principles_response


class TestContradictionMatrixModel:
    """Test ContradictionMatrix Pydantic model behavior."""

    def _make_matrix(self) -> ContradictionMatrix:
        return ContradictionMatrix(
            parameters=[
                EngineeringParameter(
                    id=1, name_en="Weight of moving object",
                    name_ko="이동 물체의 무게",
                ),
                EngineeringParameter(
                    id=2, name_en="Weight of stationary object",
                    name_ko="고정 물체의 무게",
                ),
            ],
            matrix={"1": {"2": [15, 8, 29, 34]}},
        )

    def test_lookup_existing_cell(self):
        m = self._make_matrix()
        assert m.lookup(1, 2) == [15, 8, 29, 34]

    def test_lookup_empty_cell(self):
        m = self._make_matrix()
        assert m.lookup(2, 1) == []

    def test_lookup_invalid_params(self):
        m = self._make_matrix()
        assert m.lookup(99, 99) == []

    def test_get_parameter_names(self):
        m = self._make_matrix()
        names = m.get_parameter_names()
        assert len(names) == 2
        assert names[0] == "1. 이동 물체의 무게 (Weight of moving object)"
        assert names[1] == "2. 고정 물체의 무게 (Weight of stationary object)"


class TestLoadContradictionMatrix:
    """Test loading the full matrix JSON file."""

    def test_load_has_39_parameters(self):
        matrix = load_contradiction_matrix()
        assert len(matrix.parameters) == 39

    def test_parameter_ids_are_sequential(self):
        matrix = load_contradiction_matrix()
        ids = [p.id for p in matrix.parameters]
        assert ids == list(range(1, 40))

    def test_known_cell_lookup(self):
        """Verify a well-known standard TRIZ matrix cell."""
        matrix = load_contradiction_matrix()
        # Improving: 1 (Weight of moving object), Worsening: 2 (Weight of stationary object)
        result = matrix.lookup(1, 2)
        assert result == [15, 8, 29, 34]

    def test_matrix_values_in_range(self):
        """All recommended principle numbers should be 1-40."""
        matrix = load_contradiction_matrix()
        for improving_key, row in matrix.matrix.items():
            for worsening_key, principles in row.items():
                for p in principles:
                    assert 1 <= p <= 40, (
                        f"Invalid principle {p} at [{improving_key}][{worsening_key}]"
                    )


class TestBuildMatrixContext:
    """Test _build_matrix_context helper."""

    def test_returns_empty_when_params_none(self):
        matrix = ContradictionMatrix(parameters=[], matrix={})
        result = _build_matrix_context(matrix, None, None, [])
        assert result == ""

    def test_returns_empty_when_improving_none(self):
        matrix = ContradictionMatrix(parameters=[], matrix={})
        result = _build_matrix_context(matrix, None, 2, [])
        assert result == ""

    def test_returns_empty_when_no_recommendations(self):
        matrix = ContradictionMatrix(parameters=[], matrix={"1": {"2": []}})
        result = _build_matrix_context(matrix, 1, 3, [])
        assert result == ""

    def test_returns_context_with_known_principles(self):
        matrix = ContradictionMatrix(
            parameters=[],
            matrix={"1": {"2": [15, 8]}},
        )
        principles = load_triz_principles()
        result = _build_matrix_context(matrix, 1, 2, principles)
        assert "파라미터 1" in result
        assert "파라미터 2" in result
        assert "#15" in result
        assert "#8" in result
        assert "우선적으로 고려하세요" in result

    def test_handles_unknown_principle_number(self):
        matrix = ContradictionMatrix(
            parameters=[],
            matrix={"1": {"2": [99]}},
        )
        result = _build_matrix_context(matrix, 1, 2, [])
        assert "#99" in result


class TestParsePrinciplesResponse:
    """Test parse_principles_response edge cases."""

    def test_valid_json(self):
        content = (
            '[{"number": 1, "name_en": "Segmentation",'
            ' "name_ko": "분할", "description": "test",'
            ' "matching_score": 0.9}]'
        )
        result = parse_principles_response(content)
        assert len(result) == 1
        assert result[0].number == 1

    def test_invalid_json(self):
        result = parse_principles_response("not json")
        assert result == []

    def test_empty_array(self):
        result = parse_principles_response("[]")
        assert result == []
