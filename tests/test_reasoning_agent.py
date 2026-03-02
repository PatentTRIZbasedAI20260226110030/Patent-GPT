def test_route_after_evaluate_novelty_novel():
    """Should route to draft_patent when idea is novel."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.8, "evasion_count": 0, "max_evasion_attempts": 3}
    result = route_after_evaluate_novelty(state, threshold=0.5)
    assert result == "draft_patent"


def test_route_after_evaluate_novelty_not_novel():
    """Should route to evade when idea is not novel and attempts remain."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.3, "evasion_count": 0, "max_evasion_attempts": 3}
    result = route_after_evaluate_novelty(state, threshold=0.5)
    assert result == "evade"


def test_route_after_evaluate_novelty_max_attempts():
    """Should route to draft_patent when max attempts reached even if not novel."""
    from app.services.reasoning_agent import route_after_evaluate_novelty

    state = {"novelty_score": 0.3, "evasion_count": 3, "max_evasion_attempts": 3}
    result = route_after_evaluate_novelty(state, threshold=0.5)
    assert result == "draft_patent"


def test_route_after_evaluate_context_sufficient():
    """Should route to generate_idea when context is sufficient."""
    from app.services.reasoning_agent import route_after_evaluate_context

    state = {"context_sufficient": True}
    assert route_after_evaluate_context(state) == "generate_idea"


def test_route_after_evaluate_context_insufficient():
    """Should route to search_kipris when context is insufficient."""
    from app.services.reasoning_agent import route_after_evaluate_context

    state = {"context_sufficient": False}
    assert route_after_evaluate_context(state) == "search_kipris"
