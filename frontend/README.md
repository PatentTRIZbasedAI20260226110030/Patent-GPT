# Patent-GPT Frontend

TRIZ 기반 특허 아이디어 생성 서비스의 프론트엔드(웹앱) 영역입니다.

## 폴더 구조

```
frontend/
├── docs/
│   ├── SCREEN_DEFINITION.md   # 화면 정의서 (피그마 디자인 참조 문서)
│   └── FIGMA_GUIDE.md         # Figma 활용 가이드
├── assets/                    # 디자인 에셋 (Figma export 등)
└── README.md
```

## 디자인 작업 흐름

1. **화면 정의서** (`docs/SCREEN_DEFINITION.md`)를 읽고 화면 구성·기능을 파악합니다.
2. **Figma**에서 외형 디자인(와이어프레임, 목업)을 작성합니다.
3. 디자인이 확정되면 본 폴더 또는 별도 저장소에서 실제 UI 구현을 진행합니다.

## 관련 문서

- [화면 정의서](docs/SCREEN_DEFINITION.md) — 각 화면의 목적, UI 요소, 데이터 정의
- [Figma 활용 가이드](docs/FIGMA_GUIDE.md) — Figma에서 디자인·협업 시 참고사항

## API 연동

프론트엔드 구현 시 백엔드 API는 아래를 참고하세요.

| 엔드포인트 | 용도 |
| :-- | :-- |
| `GET /api/v1/health` | 헬스체크 |
| `POST /api/v1/patent/generate` | 특허 아이디어 생성 (4단계 파이프라인) |
| `GET /api/v1/patent/{draft_id}/docx` | 특허 초안 DOCX 다운로드 |
| `POST /api/v1/patent/search` | 선행 특허 검색 단독 실행 |

상세 API 스펙은 프로젝트 루트의 `README.ko.md`를 참조하세요.
