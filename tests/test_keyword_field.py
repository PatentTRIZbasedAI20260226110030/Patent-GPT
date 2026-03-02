import pytest
from pydantic import ValidationError

from app.api.schemas.request import PatentGenerateRequest


def test_keyword_only_request_valid():
    req = PatentGenerateRequest(keyword="방열 구조체")
    assert req.keyword == "방열 구조체"
    assert req.problem_description == ""


def test_description_only_request_valid():
    req = PatentGenerateRequest(problem_description="발열을 줄이고 싶다")
    assert req.problem_description == "발열을 줄이고 싶다"
    assert req.keyword is None


def test_both_provided_valid():
    req = PatentGenerateRequest(
        problem_description="발열 문제",
        keyword="방열 구조체",
    )
    assert req.problem_description == "발열 문제"
    assert req.keyword == "방열 구조체"


def test_neither_provided_invalid():
    with pytest.raises(ValidationError, match="keyword 또는 problem_description"):
        PatentGenerateRequest()


def test_empty_strings_invalid():
    with pytest.raises(ValidationError, match="keyword 또는 problem_description"):
        PatentGenerateRequest(problem_description="  ", keyword=None)


def test_keyword_with_technical_field():
    req = PatentGenerateRequest(
        keyword="열방출 구조",
        technical_field="전자기기",
        max_evasion_attempts=2,
    )
    assert req.keyword == "열방출 구조"
    assert req.technical_field == "전자기기"
    assert req.max_evasion_attempts == 2
