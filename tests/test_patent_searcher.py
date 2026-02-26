def test_patent_searcher_combines_results():
    """Searcher should merge BM25 + vector results and return SimilarPatent objects."""
    from app.models.patent_draft import SimilarPatent
    from app.services.patent_searcher import merge_and_score_results
    from langchain_core.documents import Document

    docs = [
        Document(
            page_content="방열 구조체에 관한 발명",
            metadata={"title": "방열 구조체", "application_number": "10-2024-001"},
        ),
        Document(
            page_content="열전도 필름 기술",
            metadata={"title": "열전도 필름", "application_number": "10-2024-002"},
        ),
    ]
    # Simulate reranking scores (higher = more similar)
    scores = [0.92, 0.75]

    results = merge_and_score_results(docs, scores)
    assert len(results) == 2
    assert isinstance(results[0], SimilarPatent)
    assert results[0].similarity_score == 0.92
    assert results[0].title == "방열 구조체"


def test_merge_handles_empty_input():
    from app.services.patent_searcher import merge_and_score_results

    results = merge_and_score_results([], [])
    assert results == []
