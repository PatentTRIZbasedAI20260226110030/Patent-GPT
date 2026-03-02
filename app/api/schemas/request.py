from pydantic import BaseModel, Field, model_validator


class PatentGenerateRequest(BaseModel):
    problem_description: str = Field(
        default="", description="기술적 모순 또는 해결하고 싶은 문제"
    )
    keyword: str | None = Field(
        default=None, description="검색 키워드 (예: 방열 구조체)"
    )
    technical_field: str | None = Field(
        default=None, description="기술 분야 (예: 전자기기, 의료기기)"
    )
    max_evasion_attempts: int = Field(
        default=3, ge=1, le=5, description="최대 회피 설계 시도 횟수"
    )

    @model_validator(mode="after")
    def at_least_one_input(self) -> "PatentGenerateRequest":
        if not self.problem_description.strip() and not self.keyword:
            raise ValueError(
                "keyword 또는 problem_description 중 하나는 반드시 입력해야 합니다."
            )
        return self


class PatentSearchRequest(BaseModel):
    query: str = Field(min_length=1, description="검색 쿼리")
    top_k: int = Field(default=5, ge=1, le=50)
