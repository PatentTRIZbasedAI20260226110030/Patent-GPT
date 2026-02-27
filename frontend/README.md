# Patent-GPT Frontend

TRIZ 기반 특허 아이디어 생성 서비스의 프론트엔드(웹앱) 영역입니다.

## 실행 방법

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:3000)
npm run dev
```

> **중요:** 프론트엔드를 사용하기 전에 **백엔드(uvicorn)를 먼저 실행**해야 합니다.  
> 프로젝트 루트에서 `uvicorn app.main:app --reload`로 API 서버를 띄운 후 프론트엔드를 실행하세요.

## 환경 변수

| 변수 | 설명 | 기본값 |
| :-- | :-- | :-- |
| `NEXT_PUBLIC_API_URL` | 백엔드 API URL | `http://localhost:8000` |

`.env.example`을 복사해 `.env.local`을 만들고 필요한 값을 설정하세요.

```bash
cp .env.example .env.local
```

## 폴더 구조

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # S-01 랜딩
│   │   ├── generate/page.tsx   # S-02~04 생성 (입력/로딩/결과)
│   │   └── search/page.tsx     # S-05 선행특허 검색
│   ├── components/
│   │   ├── ui/                 # 버튼, 입력 필드 등
│   │   ├── PatentForm.tsx
│   │   ├── LoadingSteps.tsx
│   │   ├── ResultPanel.tsx
│   │   ├── TrizCard.tsx
│   │   ├── PatentCard.tsx
│   │   └── DownloadButton.tsx
│   ├── lib/
│   │   ├── api.ts              # API 클라이언트
│   │   └── utils.ts
│   └── types/
│       └── patent.ts           # TypeScript 타입
├── docs/
├── public/
└── package.json
```

## 빌드

```bash
npm run build
npm start
```

## 관련 문서

- [화면 정의서](docs/SCREEN_DEFINITION.md) — 각 화면의 목적, UI 요소, 데이터 정의
- [Figma 활용 가이드](docs/FIGMA_GUIDE.md) — Figma에서 디자인·협업 시 참고사항
- [핸드오프 문서](docs/HANDOFF.md) — Claude 등에 맥락 전달용 요약

## API 엔드포인트

| 메서드 | 경로 | 용도 |
| :-- | :-- | :-- |
| GET | `/api/v1/health` | 헬스체크 |
| POST | `/api/v1/patent/generate` | 특허 아이디어 생성 |
| GET | `/api/v1/patent/{draft_id}/docx` | DOCX 다운로드 |
| POST | `/api/v1/patent/search` | 선행 특허 검색 |
