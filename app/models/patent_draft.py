from pydantic import BaseModel, Field


class PatentDraft(BaseModel):
    title: str = Field(description="발명의 명칭")
    abstract: str = Field(description="요약")
    background: str = Field(description="발명의 배경 (기술 분야 + 선행 기술)")
    problem_statement: str = Field(description="해결하려는 과제")
    solution: str = Field(description="과제의 해결 수단")
    claims: list[str] = Field(description="청구항 목록")
    effects: str = Field(description="발명의 효과")


class SimilarPatent(BaseModel):
    title: str
    abstract: str
    application_number: str = ""
    similarity_score: float = Field(ge=0.0, le=1.0)
