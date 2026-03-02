from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    faithfulness: float = Field(description="생성된 아이디어가 검색된 근거에 기반하는 정도")
    answer_relevancy: float = Field(description="응답이 원래 문제를 다루는 정도")
    context_recall: float = Field(description="핵심 선행특허가 검색에서 누락되지 않은 정도")
    passed: bool = Field(description="신뢰도 임계값 통과 여부")
