# Patent-GPT Backend MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a backend-first MVP of the Patent-GPT Agentic RAG pipeline — a FastAPI server that takes a user's technical problem, classifies it via TRIZ principles, searches prior art with hybrid retrieval, runs an evasion loop if similarity is too high, and outputs a structured patent draft with DOCX export.

**Architecture:** Service Layer + LangGraph Core. FastAPI routes delegate to a `PatentService` orchestrator, which calls four independent services in sequence: `TRIZClassifier` (LLM routing), `PatentSearcher` (hybrid RAG), `ReasoningAgent` (LangGraph evasion loop), and `DraftGenerator` (Pydantic + DOCX). Each service is independently testable.

**Tech Stack:** Python 3.11+, FastAPI, LangChain, LangGraph, ChromaDB, OpenAI (GPT-4o, text-embedding-3-small), rank-bm25, sentence-transformers, python-docx, httpx, pydantic-settings, ruff, pytest

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.python-version`
- Modify: `.gitignore`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "patent-gpt"
version = "0.1.0"
description = "Agentic RAG-based invention copilot combining TRIZ methodology with LLMs"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "langgraph>=0.2.0",
    "chromadb>=0.5.0",
    "rank-bm25>=0.2.2",
    "sentence-transformers>=3.0.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-docx>=1.1.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.6.0",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Step 2: Create .env.example**

```env
# LLM
OPENAI_API_KEY=sk-...

# KIPRISplus
KIPRIS_API_KEY=...

# Model settings
LLM_MODEL=gpt-4o
LLM_MODEL_MINI=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Search settings
SIMILARITY_THRESHOLD=0.8
MAX_EVASION_ATTEMPTS=3
RETRIEVAL_TOP_K=20
RERANK_TOP_K=5

# ChromaDB
CHROMA_PERSIST_DIR=./data/chromadb
```

**Step 3: Create .python-version**

```
3.11
```

**Step 4: Update .gitignore**

Append the following to the existing `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# Environment
.env

# Data
data/chromadb/
*.docx

# IDE
.vscode/
.idea/

# Docs (planning materials - not for public repo)
docs (have to gitignore this!)/

# Firebase
firebase-debug.log
```

**Step 5: Create directory skeleton**

```bash
mkdir -p app/api/routes app/api/schemas app/services app/models app/prompts app/utils
mkdir -p data scripts tests
touch app/__init__.py app/api/__init__.py app/api/routes/__init__.py app/api/schemas/__init__.py
touch app/services/__init__.py app/models/__init__.py app/prompts/__init__.py app/utils/__init__.py
touch tests/__init__.py
```

**Step 6: Install dependencies**

```bash
pip install -e ".[dev]"
```

**Step 7: Verify installation**

```bash
python -c "import fastapi, langchain, langgraph, chromadb; print('All imports OK')"
```
Expected: `All imports OK`

**Step 8: Commit**

```bash
git add pyproject.toml .env.example .python-version .gitignore app/ data/ scripts/ tests/
git commit -m "chore: scaffold project structure and dependencies"
```

---

## Task 2: Configuration & Settings

**Files:**
- Create: `app/config.py`
- Test: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import os

def test_settings_loads_defaults():
    """Settings should have sensible defaults even without .env file."""
    from app.config import Settings

    settings = Settings(
        OPENAI_API_KEY="test-key",
        KIPRIS_API_KEY="test-kipris",
    )
    assert settings.LLM_MODEL == "gpt-4o"
    assert settings.LLM_MODEL_MINI == "gpt-4o-mini"
    assert settings.EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.SIMILARITY_THRESHOLD == 0.8
    assert settings.MAX_EVASION_ATTEMPTS == 3
    assert settings.RETRIEVAL_TOP_K == 20
    assert settings.RERANK_TOP_K == 5

def test_settings_requires_api_keys():
    """Settings should fail without required API keys."""
    import pytest
    from pydantic import ValidationError
    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.config'`

**Step 3: Write minimal implementation**

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    KIPRIS_API_KEY: str = ""

    # Model settings
    LLM_MODEL: str = "gpt-4o"
    LLM_MODEL_MINI: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Search settings
    SIMILARITY_THRESHOLD: float = 0.8
    MAX_EVASION_ATTEMPTS: int = 3
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"

    model_config = {"env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```
Expected: 2 passed

**Step 5: Commit**

```bash
git add app/config.py tests/test_config.py
git commit -m "feat: add Settings config with env loading and defaults"
```

---

## Task 3: TRIZ Principles Data Model

**Files:**
- Create: `app/models/triz.py`
- Create: `data/triz_principles.json`
- Test: `tests/test_models_triz.py`

**Step 1: Write the failing test**

```python
# tests/test_models_triz.py
def test_triz_principle_model():
    from app.models.triz import TRIZPrinciple

    p = TRIZPrinciple(
        number=1,
        name_en="Segmentation",
        name_ko="분할",
        description="Divide an object into independent parts.",
    )
    assert p.number == 1
    assert p.name_ko == "분할"

def test_load_triz_principles():
    from app.models.triz import load_triz_principles

    principles = load_triz_principles()
    assert len(principles) == 40
    assert principles[0].number == 1
    assert principles[0].name_en == "Segmentation"
    assert principles[39].number == 40
    assert principles[39].name_en == "Composite Materials"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models_triz.py -v
```
Expected: FAIL

**Step 3: Create triz_principles.json**

Create `data/triz_principles.json` with all 40 TRIZ principles. Each entry:

```json
[
  {"number": 1, "name_en": "Segmentation", "name_ko": "분할", "description": "Divide an object into independent parts. Make an object easy to disassemble. Increase the degree of fragmentation or segmentation."},
  {"number": 2, "name_en": "Taking Out", "name_ko": "추출", "description": "Separate an interfering part or property from an object. Extract only the necessary part or property from an object."},
  {"number": 3, "name_en": "Local Quality", "name_ko": "국소적 품질", "description": "Change an object's structure from uniform to non-uniform. Make each part of an object function in conditions most suitable for its operation."},
  {"number": 4, "name_en": "Asymmetry", "name_ko": "비대칭", "description": "Change the shape of an object from symmetrical to asymmetrical. If an object is asymmetrical, increase its degree of asymmetry."},
  {"number": 5, "name_en": "Merging", "name_ko": "합치기/통합", "description": "Bring closer together identical or similar objects. Assemble identical or similar parts to perform parallel operations."},
  {"number": 6, "name_en": "Universality", "name_ko": "다용도", "description": "Make an object perform multiple functions, eliminating the need for other objects."},
  {"number": 7, "name_en": "Nesting", "name_ko": "포개기", "description": "Place one object inside another. Pass one object through a cavity in another."},
  {"number": 8, "name_en": "Anti-weight", "name_ko": "선행 반대조치(1로 보전)", "description": "Compensate for the weight of an object by merging with other objects that provide lift. Compensate by interaction with the environment."},
  {"number": 9, "name_en": "Preliminary Counteraction", "name_ko": "선행조치", "description": "If it is necessary to perform an action with both useful and harmful effects, it should be replaced with anti-actions to control harmful effects."},
  {"number": 10, "name_en": "Preliminary Action", "name_ko": "사전예방", "description": "Perform the required change of an object completely or partially in advance. Pre-arrange objects so they can come into action without time loss."},
  {"number": 11, "name_en": "Beforehand Cushioning", "name_ko": "사전예방", "description": "Prepare emergency means beforehand to compensate for the relatively low reliability of an object."},
  {"number": 12, "name_en": "Equipotentiality", "name_ko": "높이 맞추기", "description": "In a potential field, limit position changes so there is no need to raise or lower an object."},
  {"number": 13, "name_en": "The Other Way Round", "name_ko": "반대로 하기", "description": "Invert the action used to solve the problem. Make movable parts fixed and fixed parts movable. Turn the object upside down."},
  {"number": 14, "name_en": "Spheroidality/Curvature", "name_ko": "둥글게 바꾸기/구형화", "description": "Move from flat surfaces to spherical ones and from linear to curvilinear parts. Use rollers, balls, spirals."},
  {"number": 15, "name_en": "Dynamics", "name_ko": "역동성", "description": "Allow characteristics of an object or environment to change to be optimal at each stage. Divide an object into parts capable of movement relative to each other."},
  {"number": 16, "name_en": "Partial or Excessive Action", "name_ko": "부족하거나 넘치게 하기", "description": "If 100 percent of an objective is hard to achieve, do more or less to simplify the problem."},
  {"number": 17, "name_en": "Another Dimension", "name_ko": "일제로 만들기/차원변경", "description": "Move an object in two- or three-dimensional space. Use a multi-story arrangement instead of single-story. Tilt or re-orient the object."},
  {"number": 18, "name_en": "Mechanical Vibration", "name_ko": "빌리게 하기/진동", "description": "Cause an object to oscillate or vibrate. Increase its frequency. Use resonance frequency."},
  {"number": 19, "name_en": "Periodic Action", "name_ko": "주기적 작용", "description": "Instead of continuous action, use periodic or pulsating actions. If an action is already periodic, change the frequency."},
  {"number": 20, "name_en": "Continuity of Useful Action", "name_ko": "유익한 작용의 연속", "description": "Carry on work continuously. Make all parts of an object work at full capacity all the time. Eliminate idle and intermediate actions."},
  {"number": 21, "name_en": "Skipping/Rushing Through", "name_ko": "고속처리", "description": "Conduct a process or certain stages at high speed to avoid harmful side effects."},
  {"number": 22, "name_en": "Blessing in Disguise", "name_ko": "해를 이롭게", "description": "Use harmful factors to achieve a positive effect. Eliminate the primary harmful action by combining it with another harmful action."},
  {"number": 23, "name_en": "Feedback", "name_ko": "환류, 피드백", "description": "Introduce feedback to improve a process or action. If feedback already exists, change its magnitude or influence."},
  {"number": 24, "name_en": "Intermediary", "name_ko": "임시기능 수행/매개체", "description": "Use an intermediary carrier article or intermediary process. Merge one object temporarily with another that can be easily removed."},
  {"number": 25, "name_en": "Self-service", "name_ko": "셀프서비스", "description": "Make an object serve itself by performing auxiliary helpful functions. Use waste resources, energy, or substances."},
  {"number": 26, "name_en": "Copying", "name_ko": "복제", "description": "Instead of an unavailable, expensive, or fragile object, use simpler and cheaper copies. Replace an object with optical copies."},
  {"number": 27, "name_en": "Cheap Short-living Objects", "name_ko": "일회용 제품", "description": "Replace an expensive object with a multitude of inexpensive objects, sacrificing certain qualities such as service life."},
  {"number": 28, "name_en": "Mechanics Substitution", "name_ko": "다감각 활용하기/기계시스템 대체", "description": "Replace a mechanical means with a sensory means. Use electric, magnetic, and electromagnetic fields."},
  {"number": 29, "name_en": "Pneumatics and Hydraulics", "name_ko": "공기나 물로토류 활용", "description": "Use gas and liquid parts of an object instead of solid parts. Inflatable and filled structures, air cushion, hydrostatic and hydroreactive."},
  {"number": 30, "name_en": "Flexible Shells and Thin Films", "name_ko": "얇은 막으로 보호하기", "description": "Use flexible shells and thin films instead of three-dimensional structures. Isolate the object from the external environment using flexible shells."},
  {"number": 31, "name_en": "Porous Materials", "name_ko": "다공질 재료", "description": "Make an object porous or add porous elements. If an object is already porous, use the pores to introduce a useful substance or function."},
  {"number": 32, "name_en": "Color Changes", "name_ko": "색깔 변경", "description": "Change the color of an object or its external environment. Change the transparency of an object or its environment."},
  {"number": 33, "name_en": "Homogeneity", "name_ko": "동질성", "description": "Make objects interact with a given object of the same material or close to it in behavior."},
  {"number": 34, "name_en": "Discarding and Recovering", "name_ko": "폐기 혹은 재생", "description": "Make portions of an object that have fulfilled their functions go away or modify during operation. Restore consumable parts during operation."},
  {"number": 35, "name_en": "Parameter Changes", "name_ko": "성질 바꾸기/속성 변환", "description": "Change an object's physical state, concentration or consistency, degree of flexibility, temperature."},
  {"number": 36, "name_en": "Phase Transitions", "name_ko": "상태전이", "description": "Use phenomena occurring during phase transitions, such as volume changes, loss or absorption of heat."},
  {"number": 37, "name_en": "Thermal Expansion", "name_ko": "열팽창", "description": "Use thermal expansion or contraction of materials. If thermal expansion is being used, use multiple materials with different coefficients."},
  {"number": 38, "name_en": "Strong Oxidants", "name_ko": "활성화", "description": "Replace common air with oxygen-enriched air. Replace oxygen-enriched air with pure oxygen. Use ionized oxygen. Use ozonized oxygen."},
  {"number": 39, "name_en": "Inert Atmosphere", "name_ko": "비활성화", "description": "Replace a normal environment with an inert one. Add neutral parts or inert additives to an object."},
  {"number": 40, "name_en": "Composite Materials", "name_ko": "복합재료", "description": "Change from uniform to composite or multi-layered materials."}
]
```

**Step 4: Write minimal implementation**

```python
# app/models/triz.py
import json
from pathlib import Path

from pydantic import BaseModel


class TRIZPrinciple(BaseModel):
    number: int
    name_en: str
    name_ko: str
    description: str


def load_triz_principles() -> list[TRIZPrinciple]:
    data_path = Path(__file__).parent.parent.parent / "data" / "triz_principles.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    return [TRIZPrinciple(**item) for item in data]
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_models_triz.py -v
```
Expected: 2 passed

**Step 6: Commit**

```bash
git add app/models/triz.py data/triz_principles.json tests/test_models_triz.py
git commit -m "feat: add TRIZ principles data model and 40 principles JSON"
```

---

## Task 4: PatentDraft & State Models

**Files:**
- Create: `app/models/patent_draft.py`
- Create: `app/models/state.py`
- Test: `tests/test_models.py`

**Step 1: Write the failing test**

```python
# tests/test_models.py
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
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "evasion_count": 0,
        "should_evade": False,
        "final_idea": "",
        "reasoning_trace": [],
    }
    assert state["should_evade"] is False
    assert state["evasion_count"] == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/models/patent_draft.py
from pydantic import BaseModel, Field


class PatentDraft(BaseModel):
    title: str = Field(description="발명의 명칭")
    abstract: str = Field(description="요약")
    background: str = Field(description="발명의 배경 (기술 분야 + 선행 기술)")
    problem_statement: str = Field(description="해결하려는 과제")
    solution: str = Field(description="과제의 해결 수단")
    claims: list[str] = Field(description="청구항 목록")
    effects: str = Field(description="발명의 효과")


class SimilarPatent(BaseModel):
    title: str
    abstract: str
    application_number: str = ""
    similarity_score: float = Field(ge=0.0, le=1.0)
```

```python
# app/models/state.py
from typing import TypedDict

from app.models.patent_draft import SimilarPatent
from app.models.triz import TRIZPrinciple


class AgentState(TypedDict):
    user_problem: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    evasion_count: int
    should_evade: bool
    final_idea: str
    reasoning_trace: list[str]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```
Expected: 3 passed

**Step 5: Commit**

```bash
git add app/models/patent_draft.py app/models/state.py tests/test_models.py
git commit -m "feat: add PatentDraft, SimilarPatent, and AgentState models"
```

---

## Task 5: FastAPI App Skeleton & Health Endpoint

**Files:**
- Create: `app/main.py`
- Create: `app/api/routes/health.py`
- Test: `tests/test_health.py`

**Step 1: Write the failing test**

```python
# tests/test_health.py
from fastapi.testclient import TestClient


def test_health_endpoint():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_health.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
```

```python
# app/main.py
from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Patent-GPT",
    description="Agentic RAG-based invention copilot combining TRIZ methodology with LLMs",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_health.py -v
```
Expected: 1 passed

**Step 5: Verify Swagger UI works**

```bash
uvicorn app.main:app --reload &
# Open http://localhost:8000/docs in browser
# Kill the server after verifying
kill %1
```

**Step 6: Commit**

```bash
git add app/main.py app/api/routes/health.py tests/test_health.py
git commit -m "feat: add FastAPI app skeleton with health endpoint"
```

---

## Task 6: Request/Response Schemas & Patent Route Stub

**Files:**
- Create: `app/api/schemas/request.py`
- Create: `app/api/schemas/response.py`
- Create: `app/api/routes/patent.py`
- Modify: `app/main.py`
- Test: `tests/test_patent_route.py`

**Step 1: Write the failing test**

```python
# tests/test_patent_route.py
from fastapi.testclient import TestClient


def test_generate_endpoint_accepts_valid_request():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/patent/generate",
        json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
    )
    # Stub returns 501 Not Implemented for now
    assert response.status_code == 501


def test_generate_endpoint_rejects_empty_description():
    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/v1/patent/generate",
        json={"problem_description": ""},
    )
    assert response.status_code == 422
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_patent_route.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/api/schemas/request.py
from pydantic import BaseModel, Field


class PatentGenerateRequest(BaseModel):
    problem_description: str = Field(min_length=1, description="기술적 모순 또는 해결하고 싶은 문제")
    technical_field: str | None = Field(default=None, description="기술 분야 (예: 전자기기, 의료기기)")
    max_evasion_attempts: int = Field(default=3, ge=1, le=10, description="최대 회피 설계 시도 횟수")


class PatentSearchRequest(BaseModel):
    query: str = Field(min_length=1, description="검색 쿼리")
    top_k: int = Field(default=5, ge=1, le=50)
```

```python
# app/api/schemas/response.py
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
```

```python
# app/api/routes/patent.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest

router = APIRouter(prefix="/patent")


@router.post("/generate", status_code=501)
async def generate_patent(request: PatentGenerateRequest):
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet"},
    )


@router.post("/search", status_code=501)
async def search_patents(request: PatentSearchRequest):
    return JSONResponse(
        status_code=501,
        content={"detail": "Not implemented yet"},
    )
```

Modify `app/main.py` — add the patent router:

```python
# app/main.py
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.patent import router as patent_router

app = FastAPI(
    title="Patent-GPT",
    description="Agentic RAG-based invention copilot combining TRIZ methodology with LLMs",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(patent_router, prefix="/api/v1")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_patent_route.py -v
```
Expected: 2 passed

**Step 5: Commit**

```bash
git add app/api/schemas/ app/api/routes/patent.py app/main.py tests/test_patent_route.py
git commit -m "feat: add patent route stubs and request/response schemas"
```

---

## Task 7: TRIZ Classifier Service

**Files:**
- Create: `app/prompts/classifier.py`
- Create: `app/services/triz_classifier.py`
- Test: `tests/test_triz_classifier.py`

**Step 1: Write the failing test**

```python
# tests/test_triz_classifier.py
import pytest


def test_triz_classifier_returns_principles():
    """Classifier should return a list of TRIZPrinciple objects."""
    from unittest.mock import AsyncMock, patch

    from app.models.triz import TRIZPrinciple
    from app.services.triz_classifier import TRIZClassifier

    # Mock the LLM to return a known response
    mock_response = '[{"number": 1, "name_en": "Segmentation", "name_ko": "분할", "description": "Divide an object into independent parts."}, {"number": 7, "name_en": "Nesting", "name_ko": "포개기", "description": "Place one object inside another."}]'

    classifier = TRIZClassifier.__new__(TRIZClassifier)
    classifier.llm = AsyncMock()
    classifier.llm.ainvoke = AsyncMock(return_value=AsyncMock(content=mock_response))
    classifier.principles = [
        TRIZPrinciple(number=i, name_en=f"P{i}", name_ko=f"원리{i}", description=f"Desc {i}")
        for i in range(1, 41)
    ]
    classifier.prompt = None  # Will be overridden by mock

    # We test the parsing logic separately
    from app.services.triz_classifier import parse_principles_response
    result = parse_principles_response(mock_response)
    assert len(result) == 2
    assert result[0].number == 1
    assert result[1].number == 7


def test_parse_principles_handles_invalid_json():
    from app.services.triz_classifier import parse_principles_response
    result = parse_principles_response("not valid json")
    assert result == []
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_triz_classifier.py -v
```
Expected: FAIL

**Step 3: Write the classifier prompt**

```python
# app/prompts/classifier.py
TRIZ_CLASSIFIER_SYSTEM = """You are a TRIZ (Theory of Inventive Problem Solving) expert.
Given a user's technical problem or contradiction, identify the top 3 most applicable TRIZ inventive principles from the 40 principles.

You must respond ONLY with a JSON array. Each element must have these fields:
- "number": the TRIZ principle number (1-40)
- "name_en": English name
- "name_ko": Korean name
- "description": Brief explanation of why this principle applies to the given problem

Example response:
[
  {{"number": 1, "name_en": "Segmentation", "name_ko": "분할", "description": "The problem involves a monolithic structure that could benefit from being divided into independent parts."}},
  {{"number": 7, "name_en": "Nesting", "name_ko": "포개기", "description": "Space constraints suggest placing components inside each other."}}
]

Available TRIZ principles for reference:
{principles_list}
"""

TRIZ_CLASSIFIER_HUMAN = """기술적 문제: {problem_description}
{field_context}

위 문제에 가장 적합한 TRIZ 발명 원리 3개를 JSON 배열로 응답하세요."""
```

**Step 4: Write the classifier service**

```python
# app/services/triz_classifier.py
import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.config import Settings
from app.models.triz import TRIZPrinciple, load_triz_principles
from app.prompts.classifier import TRIZ_CLASSIFIER_SYSTEM, TRIZ_CLASSIFIER_HUMAN

logger = logging.getLogger(__name__)


def parse_principles_response(content: str) -> list[TRIZPrinciple]:
    try:
        data = json.loads(content)
        return [TRIZPrinciple(**item) for item in data]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse TRIZ classifier response: {e}")
        return []


class TRIZClassifier:
    def __init__(self, settings: Settings):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_MINI,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        )
        self.principles = load_triz_principles()
        principles_text = "\n".join(
            f"#{p.number} {p.name_en} ({p.name_ko}): {p.description}"
            for p in self.principles
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", TRIZ_CLASSIFIER_SYSTEM),
            ("human", TRIZ_CLASSIFIER_HUMAN),
        ]).partial(principles_list=principles_text)

    async def classify(
        self, problem_description: str, technical_field: str | None = None
    ) -> list[TRIZPrinciple]:
        field_context = f"기술 분야: {technical_field}" if technical_field else ""
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "problem_description": problem_description,
            "field_context": field_context,
        })
        return parse_principles_response(response.content)
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_triz_classifier.py -v
```
Expected: 2 passed

**Step 6: Commit**

```bash
git add app/prompts/classifier.py app/services/triz_classifier.py tests/test_triz_classifier.py
git commit -m "feat: add TRIZ classifier service with LLM-based routing"
```

---

## Task 8: KIPRISplus API Client

**Files:**
- Create: `app/utils/kipris_client.py`
- Test: `tests/test_kipris_client.py`

**Step 1: Write the failing test**

```python
# tests/test_kipris_client.py
import pytest


def test_kipris_client_parses_response():
    """Client should parse KIPRISplus XML/JSON response into patent dicts."""
    from app.utils.kipris_client import parse_kipris_patents

    # Mock a typical KIPRISplus API response structure
    mock_data = {
        "response": {
            "body": {
                "items": {
                    "item": [
                        {
                            "inventionTitle": "방열 구조체",
                            "astrtCont": "본 발명은 방열 구조에 관한 것이다.",
                            "applicationNumber": "10-2024-0001234",
                        },
                        {
                            "inventionTitle": "열전도 필름",
                            "astrtCont": "열전도 필름에 관한 발명이다.",
                            "applicationNumber": "10-2024-0005678",
                        },
                    ]
                }
            }
        }
    }
    patents = parse_kipris_patents(mock_data)
    assert len(patents) == 2
    assert patents[0]["title"] == "방열 구조체"
    assert patents[0]["abstract"] == "본 발명은 방열 구조에 관한 것이다."
    assert patents[0]["application_number"] == "10-2024-0001234"


def test_kipris_client_handles_empty_response():
    from app.utils.kipris_client import parse_kipris_patents

    empty_data = {"response": {"body": {"items": {"item": []}}}}
    patents = parse_kipris_patents(empty_data)
    assert patents == []
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_kipris_client.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/utils/kipris_client.py
import logging
from typing import Any

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

KIPRIS_BASE_URL = "http://plus.kipris.or.kr/openapi/rest/v1/published"


def parse_kipris_patents(data: dict[str, Any]) -> list[dict[str, str]]:
    try:
        items = data["response"]["body"]["items"]["item"]
        if not items:
            return []
        if isinstance(items, dict):
            items = [items]
        return [
            {
                "title": item.get("inventionTitle", ""),
                "abstract": item.get("astrtCont", ""),
                "application_number": item.get("applicationNumber", ""),
            }
            for item in items
        ]
    except (KeyError, TypeError) as e:
        logger.warning(f"Failed to parse KIPRISplus response: {e}")
        return []


class KIPRISClient:
    def __init__(self, settings: Settings):
        self.api_key = settings.KIPRIS_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_patents(
        self, keyword: str, num_of_rows: int = 50, page_no: int = 1
    ) -> list[dict[str, str]]:
        params = {
            "word": keyword,
            "numOfRows": num_of_rows,
            "pageNo": page_no,
            "ServiceKey": self.api_key,
        }
        try:
            response = await self.client.get(KIPRIS_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return parse_kipris_patents(data)
        except httpx.HTTPError as e:
            logger.error(f"KIPRISplus API request failed: {e}")
            return []

    async def close(self):
        await self.client.aclose()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_kipris_client.py -v
```
Expected: 2 passed

**Step 5: Commit**

```bash
git add app/utils/kipris_client.py tests/test_kipris_client.py
git commit -m "feat: add KIPRISplus API client with response parsing"
```

---

## Task 9: Patent Ingestion Script

**Files:**
- Create: `scripts/ingest_patents.py`

This script fetches patents from KIPRISplus and stores them in ChromaDB. It's a batch operation run separately from the API server.

**Step 1: Write the ingestion script**

```python
# scripts/ingest_patents.py
"""Fetch patents from KIPRISplus and ingest into ChromaDB."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.config import get_settings
from app.utils.kipris_client import KIPRISClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest(keyword: str, max_patents: int = 100):
    settings = get_settings()
    client = KIPRISClient(settings)
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )

    logger.info(f"Fetching patents for keyword: {keyword}")
    patents = await client.search_patents(keyword, num_of_rows=max_patents)
    await client.close()

    if not patents:
        logger.warning("No patents found. Check your KIPRIS_API_KEY and keyword.")
        return 0

    documents = [
        Document(
            page_content=f"{p['title']}\n\n{p['abstract']}",
            metadata={
                "title": p["title"],
                "application_number": p["application_number"],
                "source": "kipris",
            },
        )
        for p in patents
        if p["title"] and p["abstract"]
    ]

    logger.info(f"Embedding and storing {len(documents)} patents into ChromaDB...")
    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        collection_name="patents",
    )

    logger.info(f"Successfully ingested {len(documents)} patents.")
    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Ingest patents from KIPRISplus into ChromaDB")
    parser.add_argument("keyword", help="Search keyword (e.g., '방열 구조')")
    parser.add_argument("--max", type=int, default=100, help="Max patents to fetch")
    args = parser.parse_args()
    asyncio.run(ingest(args.keyword, args.max))


if __name__ == "__main__":
    main()
```

**Step 2: Commit** (no test for script — it's a CLI tool tested via integration)

```bash
git add scripts/ingest_patents.py
git commit -m "feat: add patent ingestion script for KIPRISplus → ChromaDB"
```

---

## Task 10: Patent Searcher Service (Hybrid Search + Reranking)

**Files:**
- Create: `app/services/patent_searcher.py`
- Test: `tests/test_patent_searcher.py`

**Step 1: Write the failing test**

```python
# tests/test_patent_searcher.py
import pytest


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_patent_searcher.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/services/patent_searcher.py
import logging

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from app.config import Settings
from app.models.patent_draft import SimilarPatent

logger = logging.getLogger(__name__)


def merge_and_score_results(
    docs: list[Document], scores: list[float]
) -> list[SimilarPatent]:
    if not docs:
        return []
    results = []
    for doc, score in zip(docs, scores):
        results.append(
            SimilarPatent(
                title=doc.metadata.get("title", ""),
                abstract=doc.page_content,
                application_number=doc.metadata.get("application_number", ""),
                similarity_score=round(score, 4),
            )
        )
    return results


class PatentSearcher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def _get_vectorstore(self) -> Chroma:
        return Chroma(
            persist_directory=self.settings.CHROMA_PERSIST_DIR,
            embedding_function=self.embeddings,
            collection_name="patents",
        )

    async def search(self, query: str, top_k: int | None = None) -> list[SimilarPatent]:
        top_k = top_k or self.settings.RERANK_TOP_K
        retrieval_k = self.settings.RETRIEVAL_TOP_K

        vectorstore = self._get_vectorstore()
        collection = vectorstore._collection
        if collection.count() == 0:
            logger.warning("ChromaDB is empty. Run the ingestion script first.")
            return []

        # Dense retriever (vector search)
        dense_retriever = vectorstore.as_retriever(
            search_kwargs={"k": retrieval_k}
        )

        # Sparse retriever (BM25)
        all_docs = vectorstore.get()
        if not all_docs["documents"]:
            return []

        bm25_docs = [
            Document(
                page_content=doc,
                metadata=meta,
            )
            for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])
        ]
        sparse_retriever = BM25Retriever.from_documents(bm25_docs, k=retrieval_k)

        # Ensemble (hybrid) retriever
        ensemble = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[0.5, 0.5],
        )

        # Retrieve candidates
        candidates = await ensemble.ainvoke(query)

        if not candidates:
            return []

        # Deduplicate by content
        seen = set()
        unique_candidates = []
        for doc in candidates:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_candidates.append(doc)

        # Cross-Encoder reranking
        pairs = [[query, doc.page_content] for doc in unique_candidates]
        scores = self.reranker.predict(pairs).tolist()

        # Sort by score descending, take top_k
        scored = sorted(zip(unique_candidates, scores), key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in scored[:top_k]]
        top_scores = [score for _, score in scored[:top_k]]

        # Normalize scores to 0-1 range
        max_score = max(top_scores) if top_scores else 1.0
        min_score = min(top_scores) if top_scores else 0.0
        score_range = max_score - min_score if max_score != min_score else 1.0
        normalized_scores = [(s - min_score) / score_range for s in top_scores]

        return merge_and_score_results(top_docs, normalized_scores)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_patent_searcher.py -v
```
Expected: 2 passed

**Step 5: Commit**

```bash
git add app/services/patent_searcher.py tests/test_patent_searcher.py
git commit -m "feat: add patent searcher with hybrid retrieval and cross-encoder reranking"
```

---

## Task 11: Evasion Design Prompt

**Files:**
- Create: `app/prompts/triz_expert.py`
- Create: `app/prompts/evasion.py`

**Step 1: Write prompts**

```python
# app/prompts/triz_expert.py
TRIZ_EXPERT_SYSTEM = """당신은 세계 최고 수준의 TRIZ(창의적 문제 해결 이론) 전문가이자 변리사입니다.
40가지 발명 원리와 모순 행렬을 완벽히 숙지하고 있으며, 사용자의 기술적 모순을 분석하여
독창적이고 특허 가능한 해결안을 제시합니다.

응답 시 다음을 준수하세요:
1. 적용된 TRIZ 원리를 명시하고, 왜 이 원리가 적합한지 설명
2. 기존 특허와 차별화되는 핵심 포인트를 명확히 기술
3. 특허 명세서에 사용할 수 있는 수준의 기술적 구체성 유지
4. 한국어로 응답"""

TRIZ_IDEA_GENERATION_HUMAN = """기술적 문제: {problem_description}
적용할 TRIZ 원리: {triz_principles}

위 TRIZ 원리를 적용하여 이 문제를 해결하는 독창적인 발명 아이디어를 제안하세요.
아이디어는 구체적이고 기술적으로 실현 가능해야 합니다."""
```

```python
# app/prompts/evasion.py
EVASION_SYSTEM = """당신은 특허 회피 설계 전문가입니다.
유사한 선행 특허가 발견되었을 때, TRIZ 원리를 활용하여 기존 특허의 청구항을 우회하는
새로운 해결안을 설계합니다.

회피 설계 시 다음을 준수하세요:
1. 기존 특허의 핵심 청구항과 명확히 다른 기술적 접근
2. 다른 TRIZ 원리를 적용하거나 같은 원리를 다른 방식으로 적용
3. 기존 아이디어의 장점은 유지하면서 구현 방식을 변경"""

EVASION_HUMAN = """원래 문제: {problem_description}
기존 아이디어: {current_idea}

유사 선행 특허:
{similar_patents_text}

최대 유사도: {max_similarity_score:.1%}

위 선행 특허와 차별화되는 새로운 해결안을 TRIZ 원리를 활용하여 제안하세요.
기존 아이디어의 핵심 목적은 유지하되, 구현 방식을 근본적으로 변경하세요."""
```

**Step 2: Commit**

```bash
git add app/prompts/triz_expert.py app/prompts/evasion.py
git commit -m "feat: add TRIZ expert, idea generation, and evasion design prompts"
```

---

## Task 12: Reasoning Agent (LangGraph Evasion Loop)

**Files:**
- Create: `app/services/reasoning_agent.py`
- Test: `tests/test_reasoning_agent.py`

**Step 1: Write the failing test**

```python
# tests/test_reasoning_agent.py
import pytest


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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_reasoning_agent.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/services/reasoning_agent.py
import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from app.config import Settings
from app.models.state import AgentState
from app.models.patent_draft import SimilarPatent
from app.prompts.triz_expert import TRIZ_EXPERT_SYSTEM, TRIZ_IDEA_GENERATION_HUMAN
from app.prompts.evasion import EVASION_SYSTEM, EVASION_HUMAN
from app.services.patent_searcher import PatentSearcher

logger = logging.getLogger(__name__)


def should_evade(state: dict[str, Any], threshold: float, max_attempts: int) -> bool:
    return (
        state["max_similarity_score"] > threshold
        and state["evasion_count"] < max_attempts
    )


class ReasoningAgent:
    def __init__(self, settings: Settings, patent_searcher: PatentSearcher):
        self.settings = settings
        self.patent_searcher = patent_searcher
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
        self.idea_prompt = ChatPromptTemplate.from_messages([
            ("system", TRIZ_EXPERT_SYSTEM),
            ("human", TRIZ_IDEA_GENERATION_HUMAN),
        ])
        self.evasion_prompt = ChatPromptTemplate.from_messages([
            ("system", EVASION_SYSTEM),
            ("human", EVASION_HUMAN),
        ])
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("generate_idea", self._generate_idea_node)
        graph.add_node("search_prior_art", self._search_prior_art_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("evade", self._evade_node)
        graph.add_node("finalize", self._finalize_node)

        graph.set_entry_point("generate_idea")
        graph.add_edge("generate_idea", "search_prior_art")
        graph.add_edge("search_prior_art", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            self._route_after_evaluate,
            {"evade": "evade", "finalize": "finalize"},
        )
        graph.add_edge("evade", "search_prior_art")
        graph.add_edge("finalize", END)

        return graph.compile()

    def _route_after_evaluate(self, state: AgentState) -> str:
        if should_evade(
            state,
            threshold=self.settings.SIMILARITY_THRESHOLD,
            max_attempts=self.settings.MAX_EVASION_ATTEMPTS,
        ):
            return "evade"
        return "finalize"

    async def _generate_idea_node(self, state: AgentState) -> dict:
        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})" for p in state["triz_principles"]
        )
        chain = self.idea_prompt | self.llm
        response = await chain.ainvoke({
            "problem_description": state["user_problem"],
            "triz_principles": triz_text,
        })
        return {
            "current_idea": response.content,
            "reasoning_trace": state["reasoning_trace"]
                + [f"[아이디어 생성] TRIZ 원리 {triz_text} 적용"],
        }

    async def _search_prior_art_node(self, state: AgentState) -> dict:
        query = f"{state['user_problem']} {state['current_idea'][:200]}"
        results = await self.patent_searcher.search(query)
        max_score = max((p.similarity_score for p in results), default=0.0)
        return {
            "similar_patents": results,
            "max_similarity_score": max_score,
            "reasoning_trace": state["reasoning_trace"]
                + [f"[선행기술 조사] {len(results)}건 검색, 최대 유사도: {max_score:.1%}"],
        }

    async def _evaluate_node(self, state: AgentState) -> dict:
        threshold = self.settings.SIMILARITY_THRESHOLD
        if state["max_similarity_score"] > threshold:
            msg = f"[평가] 유사도 {state['max_similarity_score']:.1%} > {threshold:.0%} → 회피 설계 필요"
        else:
            msg = f"[평가] 유사도 {state['max_similarity_score']:.1%} ≤ {threshold:.0%} → 독창성 확보"
        return {
            "reasoning_trace": state["reasoning_trace"] + [msg],
        }

    async def _evade_node(self, state: AgentState) -> dict:
        patents_text = "\n".join(
            f"- {p.title} (유사도: {p.similarity_score:.1%}): {p.abstract[:100]}..."
            for p in state["similar_patents"][:3]
        )
        chain = self.evasion_prompt | self.llm
        response = await chain.ainvoke({
            "problem_description": state["user_problem"],
            "current_idea": state["current_idea"],
            "similar_patents_text": patents_text,
            "max_similarity_score": state["max_similarity_score"],
        })
        new_count = state["evasion_count"] + 1
        return {
            "current_idea": response.content,
            "evasion_count": new_count,
            "reasoning_trace": state["reasoning_trace"]
                + [f"[회피 설계 #{new_count}] 새로운 아이디어 생성"],
        }

    async def _finalize_node(self, state: AgentState) -> dict:
        return {
            "final_idea": state["current_idea"],
            "reasoning_trace": state["reasoning_trace"] + ["[완료] 최종 아이디어 확정"],
        }

    async def run(self, initial_state: AgentState) -> AgentState:
        result = await self.graph.ainvoke(initial_state)
        return result
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_reasoning_agent.py -v
```
Expected: 3 passed

**Step 5: Commit**

```bash
git add app/services/reasoning_agent.py tests/test_reasoning_agent.py
git commit -m "feat: add LangGraph reasoning agent with evasion loop"
```

---

## Task 13: Draft Generator Service

**Files:**
- Create: `app/services/draft_generator.py`
- Create: `app/utils/docx_exporter.py`
- Test: `tests/test_draft_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_draft_generator.py
import pytest
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_draft_generator.py -v
```
Expected: FAIL

**Step 3: Write DOCX exporter**

```python
# app/utils/docx_exporter.py
from docx import Document as DocxDocument
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.models.patent_draft import PatentDraft


def export_to_docx(draft: PatentDraft, output_path: str) -> str:
    doc = DocxDocument()

    # Title
    title_para = doc.add_heading(level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run(f"[발명의 명칭] {draft.title}")
    run.font.size = Pt(16)

    # Abstract
    doc.add_heading("요약", level=1)
    doc.add_paragraph(draft.abstract)

    # Background
    doc.add_heading("발명의 배경", level=1)
    doc.add_paragraph(draft.background)

    # Problem Statement
    doc.add_heading("해결하려는 과제", level=1)
    doc.add_paragraph(draft.problem_statement)

    # Solution
    doc.add_heading("과제의 해결 수단", level=1)
    doc.add_paragraph(draft.solution)

    # Claims
    doc.add_heading("청구항", level=1)
    for i, claim in enumerate(draft.claims, 1):
        doc.add_paragraph(f"[항 {i}] {claim}")

    # Effects
    doc.add_heading("발명의 효과", level=1)
    doc.add_paragraph(draft.effects)

    doc.save(output_path)
    return output_path
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_draft_generator.py -v
```
Expected: 1 passed

**Step 5: Write draft generator service**

```python
# app/services/draft_generator.py
import logging
import uuid
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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
```

**Step 6: Commit**

```bash
git add app/services/draft_generator.py app/utils/docx_exporter.py tests/test_draft_generator.py
git commit -m "feat: add draft generator with Pydantic structured output and DOCX export"
```

---

## Task 14: Patent Service Orchestrator

**Files:**
- Create: `app/services/patent_service.py`
- Test: `tests/test_patent_service.py`

**Step 1: Write the failing test**

```python
# tests/test_patent_service.py
def test_patent_service_has_required_methods():
    """PatentService should expose a generate() method."""
    import inspect
    from app.services.patent_service import PatentService

    assert hasattr(PatentService, "generate")
    sig = inspect.signature(PatentService.generate)
    params = list(sig.parameters.keys())
    assert "problem_description" in params
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_patent_service.py -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# app/services/patent_service.py
import logging

from app.config import Settings
from app.models.state import AgentState
from app.services.triz_classifier import TRIZClassifier
from app.services.patent_searcher import PatentSearcher
from app.services.reasoning_agent import ReasoningAgent
from app.services.draft_generator import DraftGenerator
from app.api.schemas.response import PatentGenerateResponse

logger = logging.getLogger(__name__)


class PatentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.triz_classifier = TRIZClassifier(settings)
        self.patent_searcher = PatentSearcher(settings)
        self.reasoning_agent = ReasoningAgent(settings, self.patent_searcher)
        self.draft_generator = DraftGenerator(settings)

    async def generate(
        self,
        problem_description: str,
        technical_field: str | None = None,
        max_evasion_attempts: int = 3,
    ) -> PatentGenerateResponse:
        # Stage 1: TRIZ Classification
        logger.info("Stage 1: Classifying problem with TRIZ principles...")
        triz_principles = await self.triz_classifier.classify(
            problem_description, technical_field
        )
        if not triz_principles:
            raise ValueError("TRIZ classification failed to return any principles.")

        # Stage 2 & 3: Reasoning Agent (includes search + evasion loop)
        logger.info("Stage 2-3: Running reasoning agent with evasion loop...")
        initial_state: AgentState = {
            "user_problem": problem_description,
            "triz_principles": triz_principles,
            "current_idea": "",
            "similar_patents": [],
            "max_similarity_score": 0.0,
            "evasion_count": 0,
            "should_evade": False,
            "final_idea": "",
            "reasoning_trace": [],
        }
        # Override max evasion attempts if specified
        original_max = self.settings.MAX_EVASION_ATTEMPTS
        self.settings.MAX_EVASION_ATTEMPTS = max_evasion_attempts
        try:
            final_state = await self.reasoning_agent.run(initial_state)
        finally:
            self.settings.MAX_EVASION_ATTEMPTS = original_max

        # Stage 4: Draft Generation
        logger.info("Stage 4: Generating structured patent draft...")
        triz_text = ", ".join(
            f"#{p.number} {p.name_ko}({p.name_en})" for p in triz_principles
        )
        draft, docx_path = await self.draft_generator.generate(
            idea=final_state["final_idea"],
            problem_description=problem_description,
            triz_principles_text=triz_text,
        )

        return PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=triz_principles,
            similar_patents=final_state["similar_patents"],
            reasoning_trace=final_state["reasoning_trace"],
            docx_download_url=docx_path,
        )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_patent_service.py -v
```
Expected: 1 passed

**Step 5: Commit**

```bash
git add app/services/patent_service.py tests/test_patent_service.py
git commit -m "feat: add PatentService orchestrator wiring all 4 pipeline stages"
```

---

## Task 15: Wire Routes to Services

**Files:**
- Modify: `app/api/routes/patent.py`
- Modify: `app/main.py`

**Step 1: Update patent routes to use PatentService**

Replace the contents of `app/api/routes/patent.py`:

```python
# app/api/routes/patent.py
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest
from app.api.schemas.response import PatentGenerateResponse, PatentSearchResponse
from app.config import Settings, get_settings
from app.services.patent_service import PatentService
from app.services.patent_searcher import PatentSearcher

router = APIRouter(prefix="/patent")


def get_patent_service(settings: Settings = Depends(get_settings)) -> PatentService:
    return PatentService(settings)


def get_patent_searcher(settings: Settings = Depends(get_settings)) -> PatentSearcher:
    return PatentSearcher(settings)


@router.post("/generate", response_model=PatentGenerateResponse)
async def generate_patent(
    request: PatentGenerateRequest,
    service: PatentService = Depends(get_patent_service),
):
    try:
        return await service.generate(
            problem_description=request.problem_description,
            technical_field=request.technical_field,
            max_evasion_attempts=request.max_evasion_attempts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=PatentSearchResponse)
async def search_patents(
    request: PatentSearchRequest,
    searcher: PatentSearcher = Depends(get_patent_searcher),
):
    try:
        results = await searcher.search(request.query, top_k=request.top_k)
        return PatentSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{draft_id}/docx")
async def download_docx(draft_id: str):
    docx_path = Path(f"data/drafts/{draft_id}.docx")
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found")
    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"patent_draft_{draft_id}.docx",
    )
```

**Step 2: Add admin ingest route**

```python
# app/api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings, get_settings

router = APIRouter(prefix="/admin")


class IngestRequest(BaseModel):
    keyword: str = Field(min_length=1, description="검색 키워드")
    max_patents: int = Field(default=100, ge=1, le=500)


class IngestResponse(BaseModel):
    ingested_count: int
    status: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_patents(
    request: IngestRequest,
    settings: Settings = Depends(get_settings),
):
    try:
        from scripts.ingest_patents import ingest
        count = await ingest(request.keyword, request.max_patents)
        return IngestResponse(ingested_count=count, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: Update main.py with all routers**

```python
# app/main.py
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.patent import router as patent_router
from app.api.routes.admin import router as admin_router

app = FastAPI(
    title="Patent-GPT",
    description="Agentic RAG-based invention copilot combining TRIZ methodology with LLMs",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(patent_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
```

**Step 4: Run all tests**

```bash
pytest tests/ -v
```
Expected: All tests pass

**Step 5: Commit**

```bash
git add app/api/routes/patent.py app/api/routes/admin.py app/main.py
git commit -m "feat: wire routes to services and add admin ingest endpoint"
```

---

## Task 16: Final Verification & Cleanup

**Step 1: Run linter**

```bash
ruff check app/ tests/ scripts/ --fix
ruff format app/ tests/ scripts/
```

**Step 2: Run full test suite**

```bash
pytest tests/ -v
```
Expected: All tests pass

**Step 3: Test the server starts**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Expected: Server starts, Swagger docs available at `http://localhost:8000/docs`

**Step 4: Commit any linting fixes**

```bash
git add -A
git commit -m "chore: apply ruff formatting and linting fixes"
```

**Step 5: Final commit with updated README**

Update `README.md` with quickstart instructions, then:

```bash
git add README.md
git commit -m "docs: update README with setup and usage instructions"
```
