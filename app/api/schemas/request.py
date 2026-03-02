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
    session_id: str | None = Field(
        default=None, description="세션 ID (대화 맥락 유지용)"
    )


class PatentSearchRequest(BaseModel):
    query: str = Field(min_length=1, description="검색 쿼리")
    top_k: int = Field(default=5, ge=1, le=50)
