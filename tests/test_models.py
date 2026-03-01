def test_patent_draft_model():
    from app.models.patent_draft import PatentDraft

    draft = PatentDraft(
        title="접이식 방열 구조를 가진 전자 장치",
        abstract="본 발명은...",
        background="종래의 전자 장치는...",
        problem_statement="발열과 두께의 모순을 해결하는 과제",
        solution="분할 원리를 적용하여...",
        claims=["독립항 1: ...", "종속항 2: ..."],
        effects="발열 감소와 두께 유지를 동시에 달성",
    )
    assert draft.title == "접이식 방열 구조를 가진 전자 장치"
    assert len(draft.claims) == 2


def test_similar_patent_model():
    from app.models.patent_draft import SimilarPatent

    patent = SimilarPatent(
        title="방열 구조체",
        abstract="방열 구조체에 관한 것으로...",
        application_number="10-2024-0001234",
        similarity_score=0.85,
    )
    assert patent.similarity_score == 0.85


def test_agent_state_keys():
    from app.models.state import AgentState

    state: AgentState = {
        "user_problem": "test",
        "technical_field": "",
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "novelty_score": 0.0,
        "novelty_reasoning": "",
        "context_sufficient": False,
        "evasion_count": 0,
        "final_idea": "",
        "reasoning_trace": [],
        "current_step": "",
    }
    assert state["context_sufficient"] is False
    assert state["evasion_count"] == 0
    assert state["novelty_score"] == 0.0
