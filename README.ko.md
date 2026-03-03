# Patent-GPT

**새로운 아이디어를 얻기 위한 트리즈(TRIZ) 활용 인공지능 엔진 서비스**

> 5조 · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026 · 발표일: 2026-03-04

[English README](README.md)

---

## 차례

1. [기획의도](#1-기획의도)
2. [AS-IS: 시장/경쟁사 분석](#2-as-is-시장경쟁사-분석)
3. [사용자 분석](#3-사용자-분석)
4. [TO-BE: 제안하는 AI 기능 컨셉](#4-to-be-제안하는-ai-기능-컨셉)
5. [아키텍처](#5-아키텍처)
6. [기대 효과](#6-기대-효과)
7. [빠른 시작](#7-빠른-시작)
8. [API](#8-api)
9. [로드맵](#9-로드맵)

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

현재 특허 분야 AI 서비스들은 주로 아이디어가 이미 있는 상태에서 **명세서 작성**을 돕는 데 집중합니다.

| 서비스 | 설명 |
| :-- | :-- |
| **젠아이피 (GenIP)** | 변리사의 특허 명세서 작성을 돕는 생성형 AI 서비스 'Gen-D' |
| **패튼에프티 (PatentFT)** | 키워드를 분석해 특허 명세서 초안을 작성하는 'PatenDraft' |
| **특허청 (KIPO)** | AI 학습용 지식재산 데이터 7종을 KIPRISplus를 통해 무료 개방 |

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
| **목표** | 사업화 가능한 특허 아이디어 발굴, 정부지원사업 지원 |

### Pain Point

- 무엇을 만들어야 할지 모름
- 특허 검색은 하지만 인사이트 도출이 어려움
- 기술 트렌드 이해가 부족함

### User Journey

| 단계 | 인지 | 탐색 | 사용 | 평가 |
| :-- | :-- | :-- | :-- | :-- |
| **행동** | 불편함을 인식 | 키워드로 검색 시작 | TRIZ 기반 아이디어 생성 | 특허 가치/신규성 확인 |
| **감정** | 막연함 | 기대감 | 구체화되는 느낌 | 실행 가능성 판단 |

---

## 4. TO-BE: 제안하는 AI 기능 컨셉

### 기존 서비스와의 핵심 차별성

| 구분 | 기존 서비스 (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **초점** | 명세서 작성 보조 | **아이디어 발굴 + 가치 평가** |
| **방법론** | 일반 LLM 지식 | TRIZ 40 원리 + 모순 행렬 |
| **검색 방식** | 단순 키워드 매칭 | 하이브리드 검색 (의미 + BM25 + 리랭킹) |
| **작동 방식** | 1회성 문답 (Stateless) | 에이전틱 재설계 루프 |
| **결과물** | 비정형 텍스트 | 검증된 JSON → DOCX 특허 초안 |

### 적용 기술

| 구분 | 기술 |
| :-- | :-- |
| 언어 | Python 3.11+, TypeScript 5 |
| 백엔드 | FastAPI, LangChain, LangGraph |
| 프론트엔드 | Next.js 16, React 18, Tailwind CSS, Shadcn UI |
| LLM | OpenAI GPT-4o-mini |
| 임베딩 | OpenAI text-embedding-3-small |
| 벡터 DB | ChromaDB |
| 검색 | BM25 + Cross-Encoder 리랭킹 |
| 특허 데이터 | KIPRISplus Open API |
| 디자인 | Figma ([와이어프레임](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)) |

---

## 5. 아키텍처

```text
┌───────────────────────────────────────────────────┐
│                  FastAPI Server                    │
├───────────────────────────────────────────────────┤
│  POST /api/v1/patent/generate                     │
│                    │                              │
│                    ▼                              │
│  ┌────────────────────────────────────────────┐   │
│  │         PatentService (Orchestrator)        │   │
│  │                                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Stage 1  │→ │ Stage 2  │→ │ Stage 3  │ │   │
│  │  │   TRIZ   │  │  선행특허 │  │  추론    │ │   │
│  │  │  분류기  │  │  검색기  │  │ 에이전트 │ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │                   ┌───────────────┘        │   │
│  │                   ▼                        │   │
│  │  유사도>80%? ─YES─→ 회피 설계 루프          │   │
│  │       │             (최대 3회 시도)         │   │
│  │       NO                    │              │   │
│  │       │         ◄───────────┘              │   │
│  │       ▼                                    │   │
│  │  ┌──────────┐                              │   │
│  │  │ Stage 4  │ → JSON + DOCX               │   │
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

| 단계 | 서비스 | 설명 |
| :--: | :-- | :-- |
| 1 | **TRIZ 분류기** | 모순 행렬 + LLM으로 문제를 TRIZ 원리에 매핑 |
| 2 | **선행특허 검색기** | 하이브리드 검색 (BM25 + 밀집 벡터) + Cross-Encoder 리랭킹 |
| 3 | **추론 에이전트** | LangGraph 회피 루프 — 유사도 초과 시 자율 재설계 |
| 4 | **초안 생성기** | KIPO 형식 특허 초안 출력 (JSON + DOCX) |

---

## 6. 기대 효과

| 관점 | 기대 효과 |
| :-- | :-- |
| **개인 발명가** | TRIZ 전문 지식 없이도 체계적 발명 방법론 활용 가능 |
| **예비 창업자** | 사업화 가능한 특허 아이디어를 빠르게 발굴하고 가치 사전 검증 |
| **R&D 엔지니어** | 기존 특허 대비 차별화된 설계 대안을 자동으로 탐색 |
| **특허 산업** | 아이디어 진입 장벽을 낮춰 개인/중소 발명자의 참여 확대 |

---

## 7-1. 빠른 시작

### 사전 준비

- Python 3.11+
- OpenAI API 키 (필수)
- Node.js 18+ (프론트엔드용)

### 설치

```bash
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT

# 백엔드
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # ← OPENAI_API_KEY 입력

# 프론트엔드
cd frontend && npm install
```

### 실행

```bash
# 터미널 1 — 백엔드 (localhost:8000)
uvicorn app.main:app --reload
```

```bash
# 터미널 2 — 프론트엔드 (localhost:3000)
cd frontend && npm run dev
```

### 테스트

```bash
pytest                         # 88개 테스트
cd frontend && npm run build   # 프로덕션 빌드 확인
```

## 7-2. Windows 초보자용 설치 (npm 설치부터, PowerShell 기준)

> 아래는 **Windows 11 + PowerShell** 기준입니다.

1. **Node.js 설치 (npm 포함)**
   - [Node.js 공식 사이트](https://nodejs.org)에서 **LTS 버전(권장: Node 20+)** 설치
   - 설치 후 PowerShell에서 확인:

```powershell
node -v
npm -v
```

2. **Git 설치**
   - [Git for Windows](https://git-scm.com/download/win) 설치
   - 확인:

```powershell
git --version
```

3. **Python 설치**
   - [Python for Windows](https://www.python.org/downloads/windows/)에서 Python 3.11 설치
   - 설치 시 **Add Python to PATH** 체크
   - 확인:

```powershell
py --version
pip --version
```

4. **프로젝트 다운로드**

```powershell
cd $HOME
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT
```

5. **백엔드 가상환경 생성/활성화**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

실행 정책 오류가 나면 1회 실행:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

다시 활성화:

```powershell
.\.venv\Scripts\Activate.ps1
```

6. **백엔드 의존성 설치**

```powershell
pip install -e ".[dev]"
```

7. **백엔드 환경 변수 설정**

```powershell
Copy-Item .env.example .env
notepad .env
```

`.env`에서 `OPENAI_API_KEY=...` 값을 입력하고 저장하세요.

8. **프론트 환경 변수 설정**

```powershell
cd frontend
Copy-Item .env.example .env.local
notepad .env.local
```

기본값(`NEXT_PUBLIC_API_URL=http://localhost:8000`)을 그대로 사용해도 됩니다.

9. **프론트 의존성 설치**

```powershell
npm install
```

10. **실행 (터미널 2개)**

터미널 A (프로젝트 루트):

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

터미널 B (`frontend` 폴더):

```powershell
cd frontend
npm run dev
```

11. **접속 확인**
   - 프론트엔드: `http://localhost:3000`
   - 백엔드 헬스체크: `http://localhost:8000/api/v1/health`

---

## 8. API

| 메서드 | 엔드포인트 | 설명 |
| :-- | :-- | :-- |
| `GET` | `/api/v1/health` | 헬스체크 |
| `POST` | `/api/v1/patent/generate` | 전체 4단계 파이프라인 (블로킹) |
| `POST` | `/api/v1/patent/generate/stream` | 전체 파이프라인 (SSE 스트리밍) |
| `POST` | `/api/v1/patent/search` | 선행특허 검색만 단독 수행 |
| `GET` | `/api/v1/patent/{draft_id}/docx` | DOCX 초안 다운로드 |
| `POST` | `/api/v1/admin/ingest` | KIPRISplus → ChromaDB 적재 트리거 |

**사용 예시 — 특허 아이디어 생성:**

```bash
curl -X POST http://localhost:8000/api/v1/patent/generate \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"}'
```

---

## 9. 로드맵

| 마일스톤 | 상태 |
| :-- | :--: |
| **Foundation** — 프로젝트 스캐폴딩, 설정, 핵심 데이터 모델, FastAPI 스켈레톤 | ✅ |
| **Core Services** — TRIZ 분류기, KIPRISplus 클라이언트, 하이브리드 특허 검색기 | ✅ |
| **Agent & Output** — LangGraph 추론 에이전트, 초안 생성기 (Pydantic + DOCX) | ✅ |
| **Ship** — 라우트 연결, 린팅, 전체 테스트 스위트 | ✅ |
| **UI/UX** — Figma 9화면 와이어프레임, Next.js 프론트엔드, 컴포넌트 라이브러리 | ✅ |
| **Integration** — SSE 스트리밍, CORS, 에러 처리, E2E 테스트 | ✅ |
| **Intelligence** — RAGAS 평가, TRIZ 모순 행렬, 대화 메모리, ML 분류기 | ✅ |
| **Simplification** — LLM 프로바이더 통일 (OpenAI), 캐싱, 병렬 검색, 보안 강화 | ✅ |

### 디자인

- [Figma 와이어프레임](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)
- [프로토타입 (CodeSandbox)](https://codesandbox.io/p/sandbox/mlc68g)

---

## 라이선스

[MIT](LICENSE)

---

## 팀

**5조** · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026
