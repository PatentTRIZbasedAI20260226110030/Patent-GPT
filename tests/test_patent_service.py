def test_patent_service_has_required_methods():
    """PatentService should expose a generate() method."""
    import inspect
    from app.services.patent_service import PatentService

    assert hasattr(PatentService, "generate")
    sig = inspect.signature(PatentService.generate)
    params = list(sig.parameters.keys())
    assert "problem_description" in params
