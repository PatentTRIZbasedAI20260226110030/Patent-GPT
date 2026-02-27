# Patent-GPT: AI 기반 TRIZ 발명 파일럿

**새로운 아이디어를 얻기 위한 트리즈(TRIZ) 활용 인공지능 엔진 서비스**

> 5조 · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026 · 발표일: 2026-03-04

[English README](README.md)

---

> **비즈니스 가치:** TRIZ 기반 AI 특허 생성과 변리사 매칭을 통해 특허 진입 장벽을 낮춥니다 —
> 전문 지식 없이도 개인 발명가와 예비 창업자가 특허 아이디어를 발굴, 평가, 초안 작성까지 완료할 수 있습니다.

---

## 차례

1. [기획의도](#1-기획의도)
2. [AS-IS: 시장/경쟁사 분석](#2-as-is-시장경쟁사-분석)
3. [사용자 분석](#3-사용자-분석)
4. [TO-BE: 제안하는 AI 기능 컨셉](#4-to-be-제안하는-ai-기능-컨셉)
5. [서비스 상세: 아키텍처 및 Flow Chart](#5-서비스-상세-아키텍처-및-flow-chart)
6. [기대 효과](#6-기대-효과)
7. [구현된 화면 기능](#7-구현된-화면-기능)
8. [빠른 시작](#빠른-시작)
9. [프로젝트 구조](#프로젝트-구조)
10. [API](#api)
11. [로드맵](#로드맵)

---

## 1. 기획의도

**TRIZ**(Theory of Solving Inventive Problem)는 구 소련 겐리히 알츠슐러(Genrich Altshuller)에 의해 제창된 **발명문제 해결을 위한 체계적 방법론**입니다.

일상생활을 하며 한두 가지 불편한 점을 느낀 경험은 누구나 있습니다. 하지만 막상 이런 불편한 점들을 해결하려고 하면 적당한 방법을 찾지 못하는 경우가 일반적입니다.

본 서비스는 **TRIZ 40가지 발명원리**를 활용한 인공지능 엔진을 통해, 막연한 문제 인식을 **구체적인 특허 아이디어**와 **실행 가능한 인사이트**로 전환하는 것을 목표로 합니다.

**핵심 가치:**

```
키워드 입력 → 특허 아이디어 생성 → 특허로서의 가치 평가
```

---

## 2. AS-IS: 시장/경쟁사 분석

현재 특허 분야 AI 서비스들은 주로 아이디어에서 머무르지 않고 **명세서 작성**까지를 서비스합니다.

| 서비스 | 설명 |
| :-- | :-- |
| **젠아이피 (GenIP)** | 변리사의 특허 명세서 작성 업무를 돕기 위한 생성형 AI 기반 명세서 서비스 'Gen-D'를 변리사들에게 제공 |
| **패튼에프티 (PatentFT)** | 키워드를 입력하면 이를 분석해 특허 명세서 초안을 작성해 주는 'PatenDraft' 프로그램 |
| **특허청 (KIPO)** | AI 학습에 활용 가능한 지식재산 데이터 7종을 특허정보활용서비스(KIPRISplus)를 통해 무료 개방 |

> **기존 서비스의 한계:** 이미 아이디어가 있는 상태에서 명세서 작성을 돕는 데 집중합니다.
> Patent-GPT는 그보다 앞선 단계 — **아이디어 자체를 발굴하고 가치를 평가**하는 것부터 시작합니다.

---

## 3. 사용자 분석

### 타겟 페르소나: 개인 발명가 / 예비 창업자

| 항목 | 내용 |
| :-- | :-- |
| **이름** | 정민아 (31세) |
| **직업** | 예비 창업자 |
| **상황** | 막연히 특허 하나는 있어야 하지 않을까라는 생각을 하고 있으나 구체적 기술은 없음 |
| **목표** | 상업적 가치 있는 특허 아이디어 발굴, 정부 지원 프로그램 신청 |

### 페인 포인트

- 무엇을 만들어야 할지 모름
- 특허를 검색해도 인사이트 도출이 어려움
- 기술 트렌드 이해 부족

### 니즈 (핵심 사용자 플로우)

```
키워드 입력 → 특허 아이디어 생성 → 특허로서의 가치 평가
```

### 사용자 여정 맵

| 단계 | 인식 | 탐색 | 사용 | 평가 |
| :-- | :-- | :-- | :-- | :-- |
| **행동** | 불편함 인식 | 키워드 검색 시작 | TRIZ 기반 아이디어 생성 | 특허 가치/신규성 확인 |
| **감정** | 막연한 답답함 | 기대감 | 구체화되는 느낌 | 실현 가능성 판단 |
| **접점** | 일상 경험 | Patent-GPT 접속 | 결과 검토 | 평가 리포트 |

---

## 4. TO-BE: 제안하는 AI 기능 컨셉

### 기존 서비스 대비 차별점

| 차원 | 기존 서비스 (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **중점** | 명세서 작성 보조 | **아이디어 발굴 + 가치 평가** |
| **방법론** | 일반 LLM 지식 | TRIZ 40원리 Few-Shot 프롬프팅 |
| **검색 방식** | 단순 키워드 매칭 | 시맨틱 + 키워드 + 리랭킹(하이브리드) |
| **상호작용** | 1회성 무상태 Q&A | 조건부 재설계 루프(에이전틱) |
| **출력** | 비구조화 텍스트 | Pydantic 검증 JSON → DOCX |

### 기술 스택

#### 백엔드

| 분류 | 기술 |
| :-- | :-- |
| 언어 | Python 3.11+ |
| 프레임워크 | FastAPI, Uvicorn |
| LLM 오케스트레이션 | LangChain, LangGraph |
| LLM | OpenAI GPT-4o (생성), GPT-4o-mini (분류) |
| 임베딩 | OpenAI text-embedding-3-small |
| 벡터 DB | ChromaDB (로컬, 인-프로세스) |
| 검색 | BM25 (rank-bm25) + Cross-Encoder (sentence-transformers) |
| 특허 데이터 | KIPRISplus Open API |
| 출력 | Pydantic Structured Output + python-docx |
| 테스트 | pytest, pytest-asyncio |
| 린팅 | Ruff |

#### 프론트엔드

| 분류 | 기술 |
| :-- | :-- |
| 프레임워크 | Next.js 14 (App Router) |
| 언어 | TypeScript |
| 스타일링 | Tailwind CSS (커스텀 Indigo 디자인 시스템) |
| UI 컴포넌트 | 자체 컴포넌트 라이브러리 (Button, Input, Select, Textarea) |
| 상태 관리 | React `useState` / `useRef` / `useCallback` |
| API 클라이언트 | `fetch` + 타입 지정 `PatentGenerateRequest` / `PatentGenerateResponse` |
| 린팅 | ESLint + Prettier |

---

## 5. 서비스 상세: 아키텍처 및 Flow Chart

**서비스 레이어 + LangGraph 코어**
FastAPI 라우트 → 서비스 레이어 → LangGraph(회피 설계 루프에만 적용).
각 파이프라인 단계는 독립적으로 테스트 가능한 서비스입니다.

```text
┌───────────────────────────────────────────────────┐
│                  FastAPI 서버                      │
├───────────────────────────────────────────────────┤
│  POST /api/v1/patent/generate                     │
│                    │                              │
│                    ▼                              │
│  ┌────────────────────────────────────────────┐   │
│  │      PatentService (오케스트레이터)          │   │
│  │                                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │  1단계   │→ │  2단계   │→ │  3단계   │ │   │
│  │  │   TRIZ   │  │  선행   │  │ 추론 에   │ │   │
│  │  │ 분류기   │  │ 특허    │  │이전트     │ │   │
│  │  │          │  │ 검색기  │  │(LangGraph)│ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │  유사도>80%? ─YES─→ 회피 루프      │        │   │
│  │       │         (최대 3회)         │        │   │
│  │       NO         ◄────────────────┘        │   │
│  │       │                                    │   │
│  │       ▼                                    │   │
│  │  ┌──────────┐                              │   │
│  │  │  4단계   │ → JSON + DOCX               │   │
│  │  │  초안    │                              │   │
│  │  │ 생성기   │                              │   │
│  │  └──────────┘                              │   │
│  └────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  ┌──────────┐        ┌───────────┐
  │ ChromaDB │        │ KIPRISplus│
  │(벡터 DB) │        │  Open API │
  └──────────┘        └───────────┘
```

### 4단계 파이프라인

| 단계 | 서비스 | 설명 | 기술 |
| :--: | :-- | :-- | :-- |
| 1 | **TRIZ 분류기** | Few-Shot LLM 라우팅으로 문제를 TRIZ 원리에 매핑 | GPT-4o-mini, Few-Shot 프롬프팅 |
| 2 | **선행특허 검색기** | KIPRISplus 데이터 하이브리드 검색 + 정밀 리랭킹 | BM25 + ChromaDB + Cross-Encoder |
| 3 | **추론 에이전트** | 유사도가 임계값을 초과할 때 자율적 재설계(회피 설계) | LangGraph 회피 루프 |
| 4 | **초안 생성기** | KIPO 형식 JSON + DOCX 특허 초안 생성 | Pydantic `with_structured_output` + python-docx |

---

## 6. 기대 효과

| 관점 | 기대 효과 |
| :-- | :-- |
| **개인 발명가** | 전문 지식 없이도 TRIZ 방법론을 활용한 체계적 아이디어 발굴 가능 |
| **예비 창업자** | 상업적 가치 있는 특허 아이디어를 빠르게 발굴하고 가치 사전 검증 |
| **R&D 엔지니어** | 기존 특허 대비 차별화된 설계 대안 자동 탐색 |
| **특허 산업** | 진입 장벽 낮춰 개인/중소기업 발명가의 시장 참여 확대 |

---

## 7. 구현된 화면 기능

프론트엔드는 문제 입력부터 다운로드 가능한 특허 초안까지 완전한 5개 화면 사용자 여정을 구현합니다.

### 화면 1 — 랜딩 페이지 (`/`)

서비스 진입점. 핵심 가치 제안을 전달하고 두 가지 주요 액션으로 사용자를 안내합니다.

- 서비스 제목과 태그라인이 담긴 히어로 섹션
- 두 가지 CTA: **특허 생성하기**, **선행특허 검색**
- TRIZ 기반 AI 차별점을 한눈에 강조

### 화면 2 — 입력 화면 (`/generate`)

사용자가 문제를 설명하고 생성 파이프라인을 설정하는 화면입니다.

- **문제 설명** — 자유 입력 텍스트 영역 (필수), 최소 1자
- **기술 분야** — 드롭다운 선택기 (전자기기 / 소재 / 기계 / 화학 / 바이오 / 기타)
- **고급 설정** — `max_evasion_attempts` 노출하는 접이식 토글 (정수, 1–10, 기본값 3)
- 접근성 오류 메시지 포함 클라이언트 측 유효성 검사
- `PatentGenerateRequest`에 직접 매핑 — 모든 필드가 `POST /api/v1/patent/generate`로 전달

### 화면 3 — 로딩 화면 (`/generate` 내)

API 호출 중 표시됩니다. 단계별 애니메이션 진행 피드백을 제공합니다.

| 단계 | 레이블 |
| :--: | :-- |
| 1 | TRIZ 원리 분류 중... |
| 2 | 선행특허 검색 중... |
| 3 | 회피 설계 검토 중... |
| 4 | 특허 초안 생성 중... |

1.5초 타이머로 단계가 진행되며 API 응답 시 완료됩니다. 인터벌은 ref로 추적되어 언마운트 시 정리됩니다.

### 화면 4 — 결과 화면 (`/generate` 내)

탭 레이아웃으로 전체 `PatentGenerateResponse`를 표시합니다.

**특허 초안 탭** — 7개 `PatentDraft` 필드 전체 렌더링:

| 필드 | 한국어 레이블 |
| :-- | :-- |
| `title` | 페이지 `<h1>`로 표시 |
| `abstract` | 요약 |
| `background` | 기술적 배경 |
| `problem_statement` | 해결 과제 |
| `solution` | 해결 수단 |
| `claims` | 청구항 (순서 목록) |
| `effects` | 발명의 효과 |

**TRIZ 원리 탭** — 반환된 원리별 `TrizCard` 컴포넌트 그리드.

**선행특허 탭** — 유사도 점수 배지가 포함된 `PatentCard` 컴포넌트 목록.

**DOCX 다운로드** — `DownloadButton`이 `docx_download_url`에서 `draft_id`를 추출하여 `GET /api/v1/patent/{draft_id}/docx` 호출 후 Blob URL로 브라우저 다운로드를 트리거합니다.

### 화면 5 — 검색 화면 (`/search`)

생성 파이프라인과 독립된 선행특허 단독 검색 화면입니다.

- `POST /api/v1/patent/search`에 매핑된 키워드 입력
- 유사도 점수가 포함된 `PatentCard` 목록으로 결과 표시
- 전체 생성 전 빠른 신규성 확인에 유용

---

## 빠른 시작

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- OpenAI API 키
- KIPRISplus API 키 ([공공데이터포털](https://www.data.go.kr/)에서 발급)

### 백엔드 설치

```bash
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env
# .env를 편집하여 API 키를 입력하세요
```

### 프론트엔드 설치

```bash
cd frontend
npm install
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000 설정
```

### 환경 변수

```env
OPENAI_API_KEY=sk-...
KIPRIS_API_KEY=...
LLM_MODEL=gpt-4o
LLM_MODEL_MINI=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.8
MAX_EVASION_ATTEMPTS=3
RETRIEVAL_TOP_K=20
RERANK_TOP_K=5
CHROMA_PERSIST_DIR=./data/chromadb
```

### 특허 데이터 적재

```bash
python scripts/ingest_patents.py
```

### 실행

```bash
# 백엔드
uvicorn app.main:app --reload

# 프론트엔드 (별도 터미널)
cd frontend && npm run dev
```

### 테스트

```bash
# 백엔드
pytest

# 프론트엔드 타입 체크
cd frontend && npx tsc --noEmit
```

---

## 프로젝트 구조

```text
Patent-GPT/
├── frontend/                         # Next.js 14 프론트엔드
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # 화면 1: 랜딩
│   │   │   ├── generate/page.tsx     # 화면 2–4: 입력 / 로딩 / 결과
│   │   │   └── search/page.tsx       # 화면 5: 선행특허 검색
│   │   ├── components/
│   │   │   ├── PatentForm.tsx        # 고급 설정 토글 포함 입력 폼
│   │   │   ├── LoadingSteps.tsx      # 4단계 애니메이션 진행 표시기
│   │   │   ├── ResultPanel.tsx       # 탭형 결과 뷰 (초안/TRIZ/특허)
│   │   │   ├── DownloadButton.tsx    # Blob URL 처리 포함 DOCX 다운로드
│   │   │   ├── PatentCard.tsx        # 유사도 배지 포함 선행특허 카드
│   │   │   ├── TrizCard.tsx          # TRIZ 원리 카드
│   │   │   └── ui/                   # 기본 컴포넌트: Button, Input, Select, Textarea
│   │   ├── lib/
│   │   │   ├── api.ts                # 타입 지정 API 클라이언트
│   │   │   └── utils.ts              # cn() Tailwind 클래스 유틸리티
│   │   └── types/
│   │       └── patent.ts             # 요청/응답 타입 정의
│   └── docs/
│       ├── SCREEN_DEFINITION.md      # 화면 정의 스펙
│       └── FIGMA_GUIDE.md            # Figma 사용 가이드
├── app/                              # FastAPI 백엔드
├── data/
├── scripts/
├── tests/
├── wiki/
├── .env.example
├── pyproject.toml
└── LICENSE
```

---

## API

> **API 계약 출처:** [`tests/test_patent_route.py`](tests/test_patent_route.py)의 테스트 우선 계약.

### `GET /api/v1/health`

```json
{ "status": "healthy", "version": "0.1.0" }
```

### `POST /api/v1/patent/generate`

**요청:**

```json
{
  "problem_description": "기기를 얇게 유지하면서 발열을 줄여야 한다",
  "technical_field": "전자기기",
  "max_evasion_attempts": 3
}
```

**응답:**

```json
{
  "patent_draft": {
    "title": "...",
    "abstract": "...",
    "background": "...",
    "problem_statement": "...",
    "solution": "...",
    "claims": ["...", "..."],
    "effects": "..."
  },
  "triz_principles": [...],
  "similar_patents": [...],
  "reasoning_trace": ["[아이디어 생성] ...", "[완료] ..."],
  "docx_download_url": "data/drafts/patent_draft_ab12cd34.docx"
}
```

### `GET /api/v1/patent/{draft_id}/docx`

생성된 특허 초안을 DOCX 파일로 다운로드합니다.

### `POST /api/v1/patent/search`

```json
{ "query": "방열 구조" }
```

### `POST /api/v1/admin/ingest`

KIPRISplus에서 ChromaDB로 특허 데이터 적재를 트리거합니다.

---

## 로드맵

| 마일스톤 | 범위 | 상태 |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | 프로젝트 스캐폴딩, 설정, 핵심 데이터 모델, FastAPI 스켈레톤, API 스키마 | ✅ 완료 |
| **v0.2.0 · Core Services** | TRIZ 분류기, KIPRISplus 클라이언트, 적재 스크립트, 하이브리드 특허 검색기, 프롬프트 라이브러리 | ✅ 완료 |
| **v0.3.0 · Agent & Output** | LangGraph 추론 에이전트, 초안 생성기(Pydantic + DOCX), PatentService 오케스트레이터 | ✅ 완료 |
| **v0.4.0 · Ship** | 라우트 연결, Ruff 린팅, 전체 테스트 스위트, 스모크 테스트 | ✅ 완료 |
| **v0.4.1 · Frontend** | Next.js 14 UI — 5개 화면, 전체 API 통합, DOCX 다운로드, 고급 설정 | ✅ 완료 |
| **v0.5.0 · Intelligence** | RAGAS 평가, TRIZ 모순 행렬, 대화 메모리(맥락 기억) | 📋 예정 |

### MVP 범위 제한 사항

- **RAGAS 평가** — 충실도(Faithfulness), 문맥 재현율(Context Recall)
- **TRIZ 모순 행렬** — 개선/악화 파라미터 매핑을 통한 정밀 원리 선택
- **맥락 기억** — 멀티턴 대화 세션 상태 유지
- **Tool Calling** — TavilySearch / PythonREPL 도구 호출
- **HWP 출력** — 현재 DOCX만 지원
- **변리사 매칭** — 아이디어 도메인 기반 변리사 연결 (v1.0 목표)

---

## 라이선스

[MIT](LICENSE)

---

## 팀

**5조** · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026
발표일: 2026-03-04
