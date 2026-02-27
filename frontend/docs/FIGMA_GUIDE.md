# Figma 활용 가이드

Patent-GPT 웹앱의 외형 디자인과 화면 정의를 Figma로 작업할 때 참고할 가이드입니다.

---

## 1. 작업 전 준비

### 참조 문서

| 문서 | 용도 |
| :-- | :-- |
| [화면 정의서](SCREEN_DEFINITION.md) | 화면 목록, UI 요소, 데이터 스키마 |
| [Architecture](../../wiki/Architecture.md) | 백엔드 4단계 파이프라인 이해 |

### Figma 파일 구조 제안

```
Patent-GPT Design
├── 📄 Cover                    # 커버 페이지 (프로젝트 개요)
├── 📄 Design System            # 색상, 타이포, 컴포넌트
├── 📄 S-01 Landing
├── 📄 S-02 Problem Input
├── 📄 S-03 Loading
├── 📄 S-04 Result
├── 📄 S-05 Search
├── 📄 S-06 Error/Empty States
└── 📄 Prototype                # 프로토타입 링크 연결
```

---

## 2. 디자인 시스템 권장 사항

### 색상

| 용도 | 권장 | 비고 |
| :-- | :-- | :-- |
| Primary | 브랜드 컬러 1종 | CTA, 강조 |
| Secondary | 보조 컬러 | 버튼(보조), 링크 |
| Background | #FFFFFF, #F5F5F5 | 라이트 모드 |
| Text | #1a1a1a, #666666 | 본문, 보조 텍스트 |
| Error | #dc3545 또는 유사 | 에러 메시지, 경고 |

### 타이포그래피

- **제목(H1):** 24~32px, Bold
- **소제목(H2):** 18~20px, Semibold
- **본문:** 14~16px, Regular
- **캡션:** 12px, Regular
- **폰트:** 시스템 폰트 (Pretendard, Noto Sans KR 등) 또는 웹폰트

### 간격

- 8px 그리드 권장 (8, 16, 24, 32, 48)
- 카드 패딩: 16~24px
- 섹션 간격: 24~48px

---

## 3. 화면별 Figma 작업 포인트

### S-01 랜딩

- Hero 섹션: 중앙 정렬, CTA 버튼 크게
- 3단계 플로우: 아이콘 + 짧은 텍스트, 수평 배치
- 데스크톱 1440px, 모바일 375px 프레임 권장

### S-02 문제 입력

- Form 필드 그룹핑, 라벨 명확히
- Textarea: min-height 120px
- "생성하기" 버튼: 전체 너비 또는 중앙 정렬

### S-03 로딩

- 4단계 스텝 인디케이터 (수직 리스트)
- 각 스텝: 체크 아이콘(완료) / 스피너(진행) / 빈 원(대기)
- (선택) 프로그레스 바

### S-04 결과

- 아코디언 또는 탭으로 `patent_draft` 섹션 접기/펼치기
- TRIZ 카드: `number` + `name_ko` + `description` 요약
- 선행특허: `similarity_score`를 %로 표시 (예: 85%)
- DOCX 다운로드 버튼: Primary 스타일

### 컴포넌트화

- 버튼: Primary, Secondary, Ghost variants
- 입력 필드: default, focus, error, disabled
- 카드: TRIZ, SimilarPatent 재사용 컴포넌트

---

## 4. 프로토타입 링크

Figma Prototype으로 사용자 플로우를 연결하면 좋습니다.

| From | To | 트리거 |
| :-- | :-- | :-- |
| S-01 CTA | S-02 | 클릭 |
| S-02 "생성하기" | S-03 | 클릭 |
| S-03 (자동) | S-04 | 3초 딜레이 등 |
| S-04 "다시 생성" | S-02 | 클릭 |
| S-04 "DOCX 다운로드" | (다운로드 시뮬레이션) | 클릭 |

---

## 5. 내보내기 및 협업

### 개발팀 공유

- **Figma 링크** 공유 (View 권한)
- **화면 정의서**와 함께 전달
- **Dev Mode** 활용 시 스타일, 간격, 에셋 내보내기 용이

### 에셋

- 로고, 아이콘: SVG 권장
- 내보내기 경로: `frontend/assets/`

---

## 6. 참고 자료

- [Figma 한글 문서](https://www.figma.com/ko/community)
- [Figma Design Systems](https://www.figma.com/blog/design-systems-101-what-is-a-design-system/)
