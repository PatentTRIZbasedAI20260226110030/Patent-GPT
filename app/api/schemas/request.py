from pydantic import BaseModel, Field


class PatentGenerateRequest(BaseModel):
    problem_description: str = Field(
        min_length=1, description="기술적 모순 또는 해결하고 싶은 문제"
    )
    technical_field: str | None = Field(
        default=None, description="기술 분야 (예: 전자기기, 의료기기)"
    )
    max_evasion_attempts: int = Field(
        default=3, ge=1, le=5, description="최대 회피 설계 시도 횟수"
    )


class PatentSearchRequest(BaseModel):
    query: str = Field(min_length=1, description="검색 쿼리")
    top_k: int = Field(default=5, ge=1, le=50)


class PatentEvaluateRequest(BaseModel):
    user_problem: str = Field(min_length=1, description="원래 문제 설명")
    generated_idea: str = Field(min_length=1, description="생성된 발명 아이디어")
    retrieved_contexts: list[str] = Field(
        default_factory=list, description="검색된 선행특허 요약 목록"
    )
    reference: str = Field(
        default="", description="참조 정답 (비어있으면 generated_idea 사용)"
    )
