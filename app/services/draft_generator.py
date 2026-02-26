import logging
import uuid
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.models.patent_draft import PatentDraft
from app.utils.docx_exporter import export_to_docx

logger = logging.getLogger(__name__)

DRAFT_SYSTEM = """당신은 한국 특허청(KIPO) 특허 명세서 작성 전문가입니다.
주어진 발명 아이디어를 바탕으로 특허 명세서의 각 섹션을 전문적으로 작성합니다.
반드시 아래 JSON 스키마를 준수하여 응답하세요."""

DRAFT_HUMAN = """발명 아이디어:
{idea}

기술적 문제:
{problem_description}

적용된 TRIZ 원리:
{triz_principles}

위 내용을 바탕으로 특허 명세서를 JSON 형식으로 작성하세요.

필수 필드:
- title: 발명의 명칭 (한국어)
- abstract: 요약 (200자 내외)
- background: 발명의 배경 (기술 분야 및 선행 기술 문제점)
- problem_statement: 해결하려는 과제
- solution: 과제의 해결 수단 (구체적인 기술 구현)
- claims: 청구항 배열 (독립항 1개 + 종속항 2개 이상)
- effects: 발명의 효과"""


class DraftGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
        ).with_structured_output(PatentDraft)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", DRAFT_SYSTEM),
            ("human", DRAFT_HUMAN),
        ])
        self.output_dir = Path("data/drafts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        idea: str,
        problem_description: str,
        triz_principles_text: str,
    ) -> tuple[PatentDraft, str | None]:
        chain = self.prompt | self.llm
        draft = await chain.ainvoke({
            "idea": idea,
            "problem_description": problem_description,
            "triz_principles": triz_principles_text,
        })

        # Export to DOCX
        docx_path = None
        try:
            filename = f"patent_draft_{uuid.uuid4().hex[:8]}.docx"
            docx_path = str(self.output_dir / filename)
            export_to_docx(draft, docx_path)
            logger.info(f"DOCX exported to {docx_path}")
        except Exception as e:
            logger.error(f"Failed to export DOCX: {e}")

        return draft, docx_path
