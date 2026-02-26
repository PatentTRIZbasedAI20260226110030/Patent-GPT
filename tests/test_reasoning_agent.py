def test_should_evade_returns_true_when_similarity_high():
    from app.services.reasoning_agent import should_evade

    state = {
        "max_similarity_score": 0.85,
        "evasion_count": 0,
    }
    assert should_evade(state, threshold=0.8, max_attempts=3) is True


def test_should_evade_returns_false_when_similarity_low():
    from app.services.reasoning_agent import should_evade

    state = {
        "max_similarity_score": 0.6,
        "evasion_count": 0,
    }
    assert should_evade(state, threshold=0.8, max_attempts=3) is False


def test_should_evade_returns_false_when_max_attempts_reached():
    from app.services.reasoning_agent import should_evade

    state = {
        "max_similarity_score": 0.9,
        "evasion_count": 3,
    }
    assert should_evade(state, threshold=0.8, max_attempts=3) is False
