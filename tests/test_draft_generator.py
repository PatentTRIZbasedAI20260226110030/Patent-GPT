from pathlib import Path


def test_docx_exporter_creates_file(tmp_path):
    from app.models.patent_draft import PatentDraft
    from app.utils.docx_exporter import export_to_docx

    draft = PatentDraft(
        title="테스트 발명",
        abstract="이것은 테스트 요약입니다.",
        background="배경 기술 설명",
        problem_statement="해결 과제",
        solution="해결 수단",
        claims=["청구항 1: 테스트", "청구항 2: 테스트"],
        effects="발명의 효과",
    )
    output_path = tmp_path / "test_patent.docx"
    result = export_to_docx(draft, str(output_path))
    assert Path(result).exists()
    assert result.endswith(".docx")
