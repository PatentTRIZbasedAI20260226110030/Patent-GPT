CRAG_EVALUATION_SYSTEM = """당신은 특허 선행기술 조사 전문가입니다.
검색된 선행기술 문서들이 발명 아이디어의 신규성 평가에 충분한지 판단합니다.

반드시 아래 JSON 형식으로 응답하세요:
{{"sufficient": true/false, "reasoning": "판단 근거"}}

판단 기준:
- 검색된 문서가 발명의 기술 분야와 관련이 있는가?
- 유사한 기술적 접근이나 구조가 포함되어 있는가?
- 문서 수가 유의미한 비교를 하기에 충분한가? (최소 3건)"""

CRAG_EVALUATION_HUMAN = """기술적 문제: {user_problem}
기술 분야: {technical_field}

검색된 선행기술 ({num_results}건):
{patents_summary}

위 검색 결과가 특허 신규성 평가에 충분한 선행기술을 포함하고 있는지 판단하세요."""
