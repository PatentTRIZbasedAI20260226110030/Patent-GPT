from pydantic import BaseModel

from app.models.patent_draft import PatentDraft, SimilarPatent
from app.models.triz import TRIZPrinciple


class PatentGenerateResponse(BaseModel):
    patent_draft: PatentDraft
    triz_principles: list[TRIZPrinciple]
    similar_patents: list[SimilarPatent]
    reasoning_trace: list[str]
    docx_download_url: str | None = None


class PatentSearchResponse(BaseModel):
    results: list[SimilarPatent]
