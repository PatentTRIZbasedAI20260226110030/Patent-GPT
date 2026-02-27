# Patent-GPT UI/UX 작업 핸드오프

> **대상:** Claude 등 AI 어시스턴트 또는 새로 합류하는 팀원  
> **용도:** 이전 작업 맥락을 전달하여 Figma 디자인·프론트엔드 구현을 이어받기 위함

---

## 1. 프로젝트 개요

**Patent-GPT**는 TRIZ(발명문제해결이론) 40가지 원리를 활용한 AI 특허 아이디어 발굴 서비스입니다.

**핵심 사용자 플로우:**
```
키워드 입력 → 특허 아이디어 생성 → 특허로서의 가치 평가 → DOCX 다운로드
```

**백엔드:** FastAPI + LangChain/LangGraph, 4단계 파이프라인 (TRIZ 분류 → 선행특허 검색 → 추론 에이전트 → 초안 생성)

---

## 2. 완료된 작업 (dev/UIUX 브랜치)

| 항목 | 내용 |
| :-- | :-- |
| **브랜치** | `dev/UIUX` |
| **frontend 폴더** | 신규 생성 |
| **화면 정의서** | `frontend/docs/SCREEN_DEFINITION.md` — 6개 화면 정의 |
| **Figma 가이드** | `frontend/docs/FIGMA_GUIDE.md` — 디자인 시스템, 프로토타입 흐름 |
| **README.ko.md** | 프로젝트 구조에 frontend 섹션 추가 |

---

## 3. 화면 목록 및 경로

| ID | 화면명 | 경로(가정) | 설명 |
| :--: | :-- | :-- | :-- |
| S-01 | 랜딩 | `/` | 서비스 소개, CTA |
| S-02 | 문제 입력 | `/generate` | 문제 설명, 기술 분야 입력 |
| S-03 | 결과 로딩 | `/generate` (상태 전환) | 4단계 파이프라인 진행 표시 |
| S-04 | 결과 화면 | `/result/:id` 또는 `/generate` | 특허 초안, TRIZ, 선행특허, DOCX 다운로드 |
| S-05 | 선행특허 검색 | `/search` | 검색 전용 (선택 기능) |
| S-06 | 에러/빈 결과 | 공통 컴포넌트 | API 오류, 유효성 오류, 빈 결과 처리 |

---

## 4. API 엔드포인트

| 메서드 | 경로 | 용도 |
| :-- | :-- | :-- |
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/patent/generate` | 특허 아이디어 생성 (4단계 파이프라인) |
| GET | `/api/v1/patent/{draft_id}/docx` | 특허 초안 DOCX 다운로드 |
| POST | `/api/v1/patent/search` | 선행 특허 검색 단독 |

**생성 요청 예시:**
```json
{
  "problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다",
  "technical_field": "전자기기",
  "max_evasion_attempts": 3
}
```

**생성 응답 주요 필드:** `patent_draft`, `triz_principles`, `similar_patents`, `reasoning_trace`, `docx_download_url`

---

## 5. 다음 단계 (권장)

1. **Figma:** `SCREEN_DEFINITION.md`와 `FIGMA_GUIDE.md`를 참고해 와이어프레임·목업 작성
2. **프로토타입:** S-01 → S-02 → S-03 → S-04 플로우 연결
3. **프론트엔드 구현:** React/Vue 등 프레임워크로 `frontend/` 내 실제 UI 구현
4. **API 연동:** 백엔드 `http://localhost:8000` (uvicorn)와 연동

---

## 6. 관련 파일 경로

```
Patent-GPT/
├── frontend/
│   ├── docs/
│   │   ├── SCREEN_DEFINITION.md   ← 화면별 상세 정의, 데이터 스키마
│   │   ├── FIGMA_GUIDE.md         ← Figma 작업 가이드
│   │   └── HANDOFF.md             ← 본 문서
│   ├── assets/                    ← Figma export용
│   └── README.md
├── app/                           ← 백엔드 (FastAPI)
├── wiki/Architecture.md           ← 백엔드 아키텍처
└── README.ko.md                   ← 프로젝트 전체 설명
```

---

**작성일:** 2026-02-27  
**브랜치:** dev/UIUX
