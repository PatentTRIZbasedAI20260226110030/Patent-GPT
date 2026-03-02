import { useState, useEffect, useRef } from "react";

const PAGES = {
  LANDING: "landing",
  INPUT: "input",
  LOADING: "loading",
  TRIZ: "triz",
  SIMILAR: "similar",
  EVASION: "evasion",
  DRAFT: "draft",
  DOWNLOAD: "download",
  SEARCH: "search",
};

const colors = {
  white: "#ffffff",
  bg: "#f7f8fa",
  surface: "#f2f3f5",
  border: "#e5e7eb",
  borderLight: "#eef0f2",
  primary: "#2563eb",
  primaryHover: "#1d4ed8",
  primaryBg: "#eff6ff",
  primaryBorder: "#bfdbfe",
  primaryText: "#1e40af",
  accent: "#059669",
  accentBg: "#ecfdf5",
  accentBorder: "#a7f3d0",
  accentText: "#065f46",
  warning: "#d97706",
  warningBg: "#fffbeb",
  warningBorder: "#fde68a",
  warningText: "#92400e",
  error: "#dc2626",
  text: "#111827",
  textSec: "#4b5563",
  textMuted: "#9ca3af",
  textFaint: "#d1d5db",
};

// ─── Shared Components ───
const Tag = ({ color, children }) => (
  <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: 0.5, color, marginBottom: 6 }}>{children}</div>
);

const Title = ({ size = 22, children, style }) => (
  <div style={{ fontSize: size, fontWeight: 700, color: colors.text, lineHeight: 1.3, letterSpacing: -0.3, ...style }}>{children}</div>
);

const Desc = ({ children, style }) => (
  <div style={{ fontSize: 14, color: colors.textSec, lineHeight: 1.6, marginTop: 6, ...style }}>{children}</div>
);

const BtnFill = ({ children, onClick, style }) => (
  <button onClick={onClick} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: colors.primary, color: "#fff", padding: "14px 24px", borderRadius: 10, fontSize: 15, fontWeight: 600, border: "none", cursor: "pointer", width: "100%", ...style }}>
    {children}
  </button>
);

const BtnGhost = ({ children, onClick, style }) => (
  <button onClick={onClick} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, background: "transparent", color: colors.textSec, padding: "14px 20px", borderRadius: 10, fontSize: 14, fontWeight: 500, border: `1px solid ${colors.border}`, cursor: "pointer", ...style }}>
    {children}
  </button>
);

const ApiTag = ({ children }) => (
  <div style={{ display: "inline-block", background: colors.primaryBg, border: `1px dashed ${colors.primaryBorder}`, borderRadius: 6, padding: "6px 10px", fontFamily: "monospace", fontSize: 10, fontWeight: 600, color: colors.primaryText, marginTop: 12 }}>{children}</div>
);

const Card = ({ children, style }) => (
  <div style={{ background: colors.white, border: `1px solid ${colors.border}`, borderRadius: 14, padding: 18, boxShadow: "0 1px 3px rgba(0,0,0,0.04)", ...style }}>{children}</div>
);

// ─── Phone Shell ───
const PhoneShell = ({ children, page, setPage }) => {
  const scrollRef = useRef(null);
  useEffect(() => { scrollRef.current?.scrollTo(0, 0); }, [page]);

  const navItems = [
    { id: PAGES.LANDING, icon: "⌂", label: "홈" },
    { id: PAGES.SEARCH, icon: "◎", label: "검색" },
    { id: PAGES.INPUT, icon: "✦", label: "생성" },
  ];

  return (
    <div style={{ width: 390, height: 844, background: colors.white, borderRadius: 44, border: `1px solid ${colors.border}`, overflow: "hidden", position: "relative", boxShadow: "0 8px 30px rgba(0,0,0,0.08)", margin: "0 auto" }}>
      {/* Status Bar */}
      <div style={{ height: 54, display: "flex", alignItems: "center", justifyContent: "center", background: colors.white }}>
        <div style={{ width: 126, height: 34, background: "#000", borderRadius: 20 }} />
      </div>
      {/* Content */}
      <div ref={scrollRef} style={{ height: 700, overflowY: "auto", WebkitOverflowScrolling: "touch" }}>
        {children}
      </div>
      {/* Bottom Nav */}
      <div style={{ height: 46, display: "flex", alignItems: "center", justifyContent: "space-around", borderTop: `1px solid ${colors.borderLight}`, background: colors.white, padding: "0 20px" }}>
        {navItems.map((n) => (
          <button key={n.id} onClick={() => setPage(n.id)} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, background: "none", border: "none", cursor: "pointer", padding: "4px 16px" }}>
            <span style={{ fontSize: 16, color: page === n.id ? colors.primary : colors.textMuted }}>{n.icon}</span>
            <span style={{ fontSize: 9, fontWeight: 600, color: page === n.id ? colors.primary : colors.textMuted }}>{n.label}</span>
          </button>
        ))}
      </div>
      {/* Home Indicator */}
      <div style={{ position: "absolute", bottom: 4, left: "50%", transform: "translateX(-50%)", width: 134, height: 5, background: "#c4c4c4", borderRadius: 3 }} />
    </div>
  );
};

// ─── PAGE: Landing ───
const LandingPage = ({ setPage }) => (
  <div>
    <div style={{ padding: "36px 28px 28px", background: "linear-gradient(180deg, #f0f5ff 0%, #fff 100%)", textAlign: "center" }}>
      <Tag color={colors.primary}>TRIZ 기반 특허 AI</Tag>
      <div style={{ fontSize: 28, fontWeight: 800, color: colors.text, letterSpacing: -1 }}>
        Patent<span style={{ color: colors.primary }}>GPT</span>
      </div>
      <Desc style={{ marginTop: 10 }}>문제를 설명하면 TRIZ 40 발명원리 기반으로{"\n"}특허 아이디어를 생성하고 명세서를 작성합니다</Desc>
      <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 24 }}>
        <BtnFill onClick={() => setPage(PAGES.INPUT)} style={{ width: "auto", padding: "14px 28px" }}>아이디어 생성</BtnFill>
        <BtnGhost onClick={() => setPage(PAGES.SEARCH)}>선행기술 검색</BtnGhost>
      </div>
    </div>

    <div style={{ margin: "0 20px", padding: 16, background: colors.white, border: `1px solid ${colors.border}`, borderRadius: 14, boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
        {["TRIZ 분류", "선행기술", "회피설계", "명세서"].map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 5 }}>
            {i > 0 && <span style={{ color: colors.textFaint, fontSize: 10, margin: "0 2px" }}>→</span>}
            <div style={{ width: 22, height: 22, borderRadius: 6, background: colors.primaryBg, color: colors.primary, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, fontFamily: "monospace" }}>{i + 1}</div>
            <span style={{ fontSize: 12, fontWeight: 500, color: colors.text }}>{s}</span>
          </div>
        ))}
      </div>
    </div>

    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, margin: "16px 20px 20px" }}>
      {[
        { icon: "T", bg: colors.primaryBg, color: colors.primary, title: "아이디어 발굴", desc: "TRIZ 40원리 기반 체계적 생성" },
        { icon: "S", bg: colors.accentBg, color: colors.accent, title: "유사도 검증", desc: "Hybrid Search + Reranking" },
        { icon: "D", bg: "#fef3c7", color: "#b45309", title: "명세서 초안", desc: "KIPO 형식 DOCX 자동 생성" },
      ].map((v, i) => (
        <Card key={i} style={{ padding: "16px 10px", textAlign: "center" }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: v.bg, color: v.color, margin: "0 auto 10px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 800, fontFamily: "monospace" }}>{v.icon}</div>
          <div style={{ fontSize: 12, fontWeight: 700, color: colors.text }}>{v.title}</div>
          <div style={{ fontSize: 10, color: colors.textMuted, marginTop: 3, lineHeight: 1.4 }}>{v.desc}</div>
        </Card>
      ))}
    </div>
  </div>
);

// ─── PAGE: Input ───
const InputPage = ({ setPage }) => {
  const [problem, setProblem] = useState("");
  const [field, setField] = useState("");
  const [attempts, setAttempts] = useState(3);

  return (
    <div style={{ padding: 24 }}>
      <Tag color={colors.primary}>STEP 1 OF 4</Tag>
      <Title>문제를 설명해주세요</Title>
      <Desc>해결하고 싶은 기술적 문제나 모순을 자유롭게 작성하세요</Desc>

      <Card style={{ marginTop: 20 }}>
        <label style={{ fontSize: 12, fontWeight: 600, color: colors.textSec, display: "block", marginBottom: 6 }}>
          문제 설명 <span style={{ color: colors.error }}>*</span>
        </label>
        <textarea
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="예: 기기를 얇게 유지하면서 발열을 줄여야 한다..."
          style={{ width: "100%", minHeight: 100, background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "13px 14px", fontSize: 14, color: colors.text, resize: "vertical", outline: "none", lineHeight: 1.7, fontFamily: "inherit" }}
        />
      </Card>

      <Card style={{ marginTop: 12 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: colors.textMuted, marginBottom: 12 }}>선택 입력</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: colors.textSec, display: "block", marginBottom: 6 }}>기술 분야</label>
            <input value={field} onChange={(e) => setField(e.target.value)} placeholder="예: 전자기기" style={{ width: "100%", background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "10px 14px", fontSize: 13, color: colors.text, outline: "none" }} />
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: colors.textSec, display: "block", marginBottom: 6 }}>최대 회피설계 횟수</label>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {[1, 2, 3, 4, 5].map((n) => (
                <button key={n} onClick={() => setAttempts(n)} style={{ width: 32, height: 32, borderRadius: 8, background: attempts === n ? colors.primary : colors.bg, color: attempts === n ? "#fff" : colors.textSec, border: `1px solid ${attempts === n ? colors.primary : colors.border}`, fontSize: 13, fontWeight: 600, cursor: "pointer" }}>{n}</button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <div style={{ marginTop: 16, background: colors.primaryBg, border: `1px dashed ${colors.primaryBorder}`, borderRadius: 10, padding: "12px 14px" }}>
        <div style={{ fontFamily: "monospace", fontSize: 10, fontWeight: 700, color: colors.primaryText, marginBottom: 4 }}>API: POST /api/v1/patent/generate</div>
        <pre style={{ fontFamily: "monospace", fontSize: 11, color: colors.textSec, lineHeight: 1.7, margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify({ problem_description: problem || "string", technical_field: field || "string", max_evasion_attempts: attempts }, null, 2)}</pre>
      </div>

      <BtnFill onClick={() => setPage(PAGES.LOADING)} style={{ marginTop: 14 }}>분석 시작</BtnFill>
    </div>
  );
};

// ─── PAGE: Loading ───
const LoadingPage = ({ setPage }) => {
  const [stage, setStage] = useState(0);
  const [logs, setLogs] = useState([]);

  const allLogs = [
    { text: "✓ [TRIZ] 원리 #35, #28 매핑 완료", color: colors.accent },
    { text: "→ [검색] KIPRISplus API 조회 중...", color: colors.primary },
    { text: "✓ [검색] 유사 특허 3건 발견", color: colors.accent },
    { text: "→ [추론] Cross-Encoder 리랭킹 실행...", color: colors.primary },
    { text: "✓ [추론] 유사도 분석 완료", color: colors.accent },
    { text: "→ [생성] 명세서 구조화 출력 중...", color: colors.primary },
  ];

  useEffect(() => {
    const timers = [];
    timers.push(setTimeout(() => { setStage(1); setLogs([allLogs[0]]); }, 800));
    timers.push(setTimeout(() => { setLogs((p) => [...p, allLogs[1]]); }, 1600));
    timers.push(setTimeout(() => { setStage(2); setLogs((p) => [...p, allLogs[2]]); }, 2800));
    timers.push(setTimeout(() => { setLogs((p) => [...p, allLogs[3]]); }, 3600));
    timers.push(setTimeout(() => { setStage(3); setLogs((p) => [...p, allLogs[4]]); }, 4800));
    timers.push(setTimeout(() => { setLogs((p) => [...p, allLogs[5]]); }, 5400));
    timers.push(setTimeout(() => { setStage(4); }, 6200));
    timers.push(setTimeout(() => { setPage(PAGES.TRIZ); }, 7200));
    return () => timers.forEach(clearTimeout);
  }, []);

  const stages = [
    { name: "Stage 1: TRIZ 분류", sub: "문제 → TRIZ 발명원리 매핑" },
    { name: "Stage 2: 선행기술 검색", sub: "BM25 + ChromaDB + Cross-Encoder" },
    { name: "Stage 3: 추론 에이전트", sub: "유사도 검증 + 회피설계 루프" },
    { name: "Stage 4: 명세서 생성", sub: "Pydantic + python-docx" },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <Title size={20}>AI 분석 진행 중</Title>
        <Desc>4단계 파이프라인을 순차 실행합니다</Desc>
      </div>

      {stages.map((s, i) => {
        const isDone = stage > i;
        const isActive = stage === i;
        const bg = isDone ? colors.accentBg : isActive ? colors.primaryBg : "transparent";
        const borderColor = isDone ? colors.accentBorder : isActive ? colors.primaryBorder : colors.borderLight;

        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: 14, borderRadius: 10, border: `1px solid ${borderColor}`, background: bg, marginBottom: 6, transition: "all 0.4s ease" }}>
            <div style={{ width: 34, height: 34, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, fontFamily: "monospace", flexShrink: 0, background: isDone ? colors.accent : isActive ? colors.primary : colors.surface, color: isDone || isActive ? "#fff" : colors.textMuted }}>
              {isDone ? "✓" : i + 1}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: isDone || isActive ? colors.text : colors.textMuted }}>{s.name}</div>
              <div style={{ fontSize: 11, color: colors.textMuted, marginTop: 1 }}>{s.sub}</div>
            </div>
            {isDone && <span style={{ fontSize: 10, fontWeight: 700, color: colors.accent }}>완료</span>}
            {isActive && <span style={{ fontSize: 10, fontWeight: 700, color: colors.primary }}>처리중</span>}
          </div>
        );
      })}

      <div style={{ marginTop: 16, padding: 14, background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 10 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: colors.textSec, marginBottom: 10 }}>실시간 추론 로그</div>
        {logs.map((l, i) => (
          <div key={i} style={{ fontFamily: "monospace", fontSize: 11, lineHeight: 2, color: l.color, transition: "all 0.3s" }}>{l.text}</div>
        ))}
        {logs.length === 0 && <div style={{ fontFamily: "monospace", fontSize: 11, color: colors.textMuted }}>○ 분석 준비 중...</div>}
      </div>
    </div>
  );
};

// ─── PAGE: TRIZ Results ───
const TrizPage = ({ setPage }) => {
  const trizData = [
    { num: "35", name: "파라미터 변환", pct: 94, desc: "물체의 물리적 상태, 농도, 밀도, 유연도, 온도 등을 변경한다" },
    { num: "28", name: "기계 시스템 대체", pct: 87, desc: "기계적 수단을 광학, 음향, 열적 수단으로 대체한다" },
    { num: "15", name: "역학적 성질 변화", pct: 72, desc: "물체 또는 환경의 역학적 성질을 변경한다" },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Tag color={colors.accent}>ANALYSIS COMPLETE</Tag>
      <Title size={20}>TRIZ 분석 결과</Title>
      <Desc style={{ marginBottom: 16 }}>적용된 발명원리와 매칭률</Desc>

      {trizData.map((t, i) => (
        <Card key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start", marginBottom: 8 }}>
          <div style={{ minWidth: 44, height: 44, borderRadius: 10, background: colors.primaryBg, color: colors.primary, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 800, fontFamily: "monospace" }}>{t.num}</div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 14, fontWeight: 600, color: colors.text }}>{t.name}</span>
              <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 4, background: t.pct >= 90 ? colors.accentBg : colors.primaryBg, color: t.pct >= 90 ? colors.accentText : colors.primaryText }}>{t.pct}%</span>
            </div>
            <div style={{ fontSize: 12, color: colors.textSec, marginTop: 4, lineHeight: 1.5 }}>{t.desc}</div>
          </div>
        </Card>
      ))}

      <div style={{ marginTop: 14, padding: 18, background: colors.primaryBg, border: `1px solid ${colors.primaryBorder}`, borderRadius: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: colors.primary, marginBottom: 8 }}>생성된 아이디어</div>
        <div style={{ fontSize: 14, color: colors.text, lineHeight: 1.7 }}>
          그래핀 기반 나노구조 방열 시트를 적용하여, 기기 두께를 0.3mm 이하로 유지하면서 열전도율을 기존 대비 300% 향상시키는 복합 방열 구조
        </div>
      </div>

      <BtnFill onClick={() => setPage(PAGES.SIMILAR)} style={{ marginTop: 14 }}>선행기술 확인</BtnFill>
      <ApiTag>Response: triz_principles[] · matching_score</ApiTag>
    </div>
  );
};

// ─── PAGE: Similar Patents ───
const SimilarPage = ({ setPage }) => {
  const patents = [
    { title: "나노 복합 방열 시트", id: "10-2024-0012345", sim: 85, field: "전자기기 방열", alert: true },
    { title: "그래핀 열전도 필름", id: "10-2023-0098765", sim: 72, field: "소재공학", alert: false },
    { title: "초박형 방열 구조체", id: "10-2024-0045678", sim: 64, field: "모바일 디바이스", alert: false },
  ];

  const simColor = (s) => s >= 80 ? colors.warning : s >= 70 ? colors.primary : colors.accent;

  return (
    <div style={{ padding: 24 }}>
      <Tag color={colors.warning}>PRIOR ART SEARCH</Tag>
      <Title size={20}>유사 선행기술</Title>
      <Desc style={{ marginBottom: 14 }}>Hybrid Search + Cross-Encoder 리랭킹</Desc>

      <div style={{ display: "flex", gap: 10, alignItems: "center", padding: "12px 14px", borderRadius: 10, background: colors.warningBg, border: `1px solid ${colors.warningBorder}`, marginBottom: 12 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: "#fde68a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0, fontWeight: 700, color: colors.warningText }}>!</div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: colors.warningText }}>유사도 80% 초과 감지</div>
          <div style={{ fontSize: 11, color: colors.textSec }}>회피설계가 자동 실행됩니다</div>
        </div>
      </div>

      {patents.map((p, i) => (
        <div key={i} style={{ padding: 14, background: colors.white, borderRadius: 10, marginBottom: 6, boxShadow: "0 1px 3px rgba(0,0,0,0.04)", border: `1px solid ${p.alert ? colors.warningBorder : colors.border}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: colors.text }}>{p.title}</div>
              <div style={{ fontFamily: "monospace", fontSize: 11, color: colors.textMuted, marginTop: 2 }}>{p.id}</div>
            </div>
            <div style={{ fontFamily: "monospace", fontSize: 20, fontWeight: 800, color: simColor(p.sim) }}>{p.sim}%</div>
          </div>
          <div style={{ height: 4, background: colors.surface, borderRadius: 2, overflow: "hidden", marginTop: 8 }}>
            <div style={{ height: "100%", width: `${p.sim}%`, background: simColor(p.sim), borderRadius: 2, transition: "width 0.6s ease" }} />
          </div>
          <div style={{ fontSize: 10, color: colors.textMuted, marginTop: 6 }}>분야: {p.field}</div>
        </div>
      ))}

      <BtnFill onClick={() => setPage(PAGES.EVASION)} style={{ marginTop: 14 }}>회피설계 진행</BtnFill>
      <ApiTag>Response: similar_patents[] · threshold: 0.8</ApiTag>
    </div>
  );
};

// ─── PAGE: Evasion ───
const EvasionPage = ({ setPage }) => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setStep(1), 1000);
    const t2 = setTimeout(() => setStep(2), 2500);
    const t3 = setTimeout(() => setStep(3), 4000);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  const traces = [
    { text: "× [시도 1] 기존 아이디어 유사도 85% → 초과", color: colors.error },
    { text: "→ [회피] TRIZ #35 적용 → PCM 상변화 물질 전환", color: colors.primary },
    { text: "✓ [재검증] 수정 아이디어 유사도 67% → 통과", color: colors.accent },
    { text: "● [완료] 회피설계 성공 → Stage 4 전환", color: colors.accent },
  ];

  const attempts = [
    { label: "시도 1", val: "85%", status: "초과", type: "fail" },
    { label: "시도 2", val: "67%", status: "통과", type: "pass" },
    { label: "시도 3", val: "—", status: "불필요", type: "skip" },
  ];

  const attColors = { fail: { bg: colors.warningBg, border: colors.warningBorder, val: colors.warning }, pass: { bg: colors.accentBg, border: colors.accentBorder, val: colors.accent }, skip: { bg: colors.surface, border: colors.border, val: colors.textMuted } };

  return (
    <div style={{ padding: 24 }}>
      <Tag color={colors.warning}>EVASION DESIGN LOOP</Tag>
      <Title size={20}>회피설계 진행</Title>
      <Desc style={{ marginBottom: 16 }}>LangGraph Agent 자동 대안 설계</Desc>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
        {attempts.map((a, i) => {
          const c = attColors[a.type];
          const visible = a.type === "fail" ? step >= 1 : a.type === "pass" ? step >= 2 : step >= 3;
          return (
            <div key={i} style={{ padding: 14, borderRadius: 10, textAlign: "center", background: visible ? c.bg : colors.surface, border: `1px solid ${visible ? c.border : colors.border}`, transition: "all 0.5s ease", opacity: visible ? 1 : 0.4 }}>
              <div style={{ fontSize: 10, color: colors.textMuted, marginBottom: 2 }}>{a.label}</div>
              <div style={{ fontFamily: "monospace", fontSize: 22, fontWeight: 800, color: visible ? c.val : colors.textMuted }}>{visible ? a.val : "..."}</div>
              <div style={{ fontSize: 9, fontWeight: 700, color: visible ? c.val : colors.textMuted, marginTop: 2 }}>{visible ? a.status : "대기"}</div>
            </div>
          );
        })}
      </div>

      <div style={{ padding: 16, background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: colors.textSec, marginBottom: 10 }}>추론 과정 (reasoning_trace)</div>
        {traces.filter((_, i) => i < step).map((t, i) => (
          <div key={i} style={{ padding: "7px 10px", borderRadius: 4, fontSize: 12, color: t.color, lineHeight: 1.5, marginBottom: 1, background: i % 2 === 1 ? colors.white : "transparent" }}>{t.text}</div>
        ))}
        {step === 0 && <div style={{ fontSize: 12, color: colors.textMuted, padding: "7px 10px" }}>분석 중...</div>}
      </div>

      <ApiTag>LangGraph State: reasoning_trace[] · max_attempts: 3</ApiTag>
      {step >= 3 && <BtnFill onClick={() => setPage(PAGES.DRAFT)} style={{ marginTop: 14 }}>명세서 생성</BtnFill>}
    </div>
  );
};

// ─── PAGE: Draft ───
const DraftPage = ({ setPage }) => (
  <div style={{ padding: 24 }}>
    <Tag color={colors.accent}>PATENT DRAFT GENERATED</Tag>
    <Title size={20}>특허 명세서 초안</Title>
    <Desc style={{ marginBottom: 14 }}>Pydantic 구조화 출력 · KIPO 형식</Desc>

    <div style={{ background: colors.white, border: `1px solid ${colors.border}`, borderRadius: 14, padding: "24px 20px", boxShadow: "0 4px 12px rgba(0,0,0,0.06)", maxHeight: 380, overflow: "hidden", position: "relative" }}>
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 60, background: "linear-gradient(transparent, #fff)", zIndex: 1 }} />
      <div style={{ textAlign: "center", fontSize: 10, color: colors.textMuted, marginBottom: 2 }}>특허출원서</div>
      <div style={{ textAlign: "center", fontSize: 16, fontWeight: 700, color: colors.text, marginBottom: 18, lineHeight: 1.4 }}>
        상변화 물질을 이용한 초박형 적응형 방열 장치 및 그 제조 방법
      </div>
      {[
        { label: "요약", text: "본 발명은 상변화 물질(PCM)을 마이크로캡슐화하여 전자기기 내부에 적용함으로써, 기기의 두께를 최소화하면서도 효과적인 열 관리를 가능하게 하는 방열 장치에 관한 것이다." },
        { label: "기술분야", text: "본 발명은 전자기기의 열 관리 분야에 관한 것으로, 더 상세하게는 상변화 물질 기반의 초박형 방열 구조에 관한 것이다." },
        { label: "해결하고자 하는 과제", text: "종래의 방열 기술은 히트싱크의 부피가 크거나, 방열 성능이 기기 두께에 비례하는 한계가 있었다." },
        { label: "청구항 1", text: "전자기기 내부에 배치되는 방열 장치에 있어서, 상변화 물질이 마이크로캡슐에 봉입된 방열층과..." },
      ].map((s, i) => (
        <div key={i}>
          <div style={{ fontSize: 11, fontWeight: 700, color: colors.primary, marginBottom: 3, marginTop: i === 0 ? 0 : 14 }}>{s.label}</div>
          <div style={{ fontSize: 12, lineHeight: 1.8, color: colors.textSec }}>{s.text}</div>
        </div>
      ))}
    </div>

    <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
      <BtnFill onClick={() => setPage(PAGES.DOWNLOAD)} style={{ flex: 1 }}>DOCX 다운로드</BtnFill>
      <BtnGhost onClick={() => {}} style={{ padding: "14px 16px" }}>재생성</BtnGhost>
    </div>
    <ApiTag>Response: patent_draft{"{}"} → GET /patent/{"{draft_id}"}/docx</ApiTag>
  </div>
);

// ─── PAGE: Download ───
const DownloadPage = ({ setPage }) => (
  <div style={{ padding: 24, textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 680 }}>
    <div style={{ width: 72, height: 72, borderRadius: 18, background: colors.accentBg, border: `1px solid ${colors.accentBorder}`, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={colors.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
    </div>
    <Title size={24}>생성 완료</Title>
    <Desc>특허 명세서 초안이 성공적으로 생성되었습니다</Desc>

    <div style={{ margin: "28px 0", padding: "24px 28px", background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 18, width: "100%", maxWidth: 260, textAlign: "center" }}>
      <div style={{ width: 44, height: 56, background: colors.primaryBg, border: `1px solid ${colors.primaryBorder}`, borderRadius: 6, margin: "0 auto 12px", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", fontSize: 9, fontWeight: 700, color: colors.primary }}>.docx</div>
      <div style={{ fontSize: 13, fontWeight: 600, color: colors.text, fontFamily: "monospace" }}>patent_draft_ab12cd34.docx</div>
      <div style={{ fontSize: 11, color: colors.textMuted, marginTop: 3 }}>KIPO 형식 · 2.3 KB</div>
      <div style={{ marginTop: 16, background: colors.primary, color: "#fff", padding: "11px 0", borderRadius: 8, fontSize: 14, fontWeight: 600, cursor: "pointer" }}>다운로드</div>
    </div>

    <ApiTag>API: GET /api/v1/patent/{"{draft_id}"}/docx</ApiTag>

    <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
      <BtnGhost onClick={() => setPage(PAGES.INPUT)}>새로운 분석</BtnGhost>
      <BtnGhost onClick={() => setPage(PAGES.LANDING)}>홈으로</BtnGhost>
    </div>
  </div>
);

// ─── PAGE: Search ───
const SearchPage = ({ setPage }) => {
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(false);

  const results = [
    { title: "나노 복합 방열 시트 특허", id: "10-2024-0012345" },
    { title: "그래핀 열전도 필름 구조", id: "10-2023-0098765" },
    { title: "초박형 열 분산 장치", id: "10-2024-0045678" },
    { title: "PCM 기반 방열 모듈", id: "10-2023-0056789" },
    { title: "마이크로 채널 냉각 구조", id: "10-2024-0078901" },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Tag color={colors.primary}>QUICK SEARCH</Tag>
      <Title size={20}>선행기술 검색</Title>
      <Desc style={{ marginBottom: 16 }}>전체 파이프라인 없이 독립 검색</Desc>

      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="검색어를 입력하세요..."
          onKeyDown={(e) => e.key === "Enter" && setSearched(true)}
          style={{ flex: 1, background: colors.bg, border: `1px solid ${colors.border}`, borderRadius: 10, padding: "13px 16px", fontSize: 14, color: colors.text, outline: "none" }}
        />
        <button onClick={() => setSearched(true)} style={{ background: colors.primary, color: "#fff", padding: "13px 18px", borderRadius: 10, fontSize: 14, fontWeight: 600, border: "none", cursor: "pointer", whiteSpace: "nowrap" }}>검색</button>
      </div>

      {searched && (
        <>
          <div style={{ background: colors.primaryBg, border: `1px dashed ${colors.primaryBorder}`, borderRadius: 10, padding: "10px 12px", marginBottom: 14 }}>
            <div style={{ fontFamily: "monospace", fontSize: 10, fontWeight: 700, color: colors.primaryText, marginBottom: 4 }}>API: POST /api/v1/patent/search</div>
            <div style={{ fontFamily: "monospace", fontSize: 11, color: colors.textSec }}>{"{ \"query\": \""}{query || "방열 구조"}{"\" }"}</div>
          </div>

          {results.map((r, i) => (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 14px", background: colors.white, border: `1px solid ${colors.border}`, borderRadius: 10, marginBottom: 5, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: colors.text }}>{r.title}</div>
                <div style={{ fontFamily: "monospace", fontSize: 10, color: colors.textMuted, marginTop: 1 }}>{r.id}</div>
              </div>
              <div style={{ fontSize: 10, fontWeight: 600, padding: "4px 10px", borderRadius: 4, background: colors.primaryBg, color: colors.primary, whiteSpace: "nowrap", cursor: "pointer" }}>상세보기</div>
            </div>
          ))}

          <BtnGhost onClick={() => setPage(PAGES.INPUT)} style={{ width: "100%", justifyContent: "center", marginTop: 16 }}>이 키워드로 아이디어 생성 →</BtnGhost>
        </>
      )}

      {!searched && (
        <div style={{ textAlign: "center", padding: "60px 20px", color: colors.textMuted }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>◎</div>
          <div style={{ fontSize: 14 }}>검색어를 입력하고 Enter 또는 검색 버튼을 눌러주세요</div>
        </div>
      )}
    </div>
  );
};

// ─── MAIN APP ───
export default function PatentGPTPrototype() {
  const [page, setPage] = useState(PAGES.LANDING);

  const renderPage = () => {
    switch (page) {
      case PAGES.LANDING: return <LandingPage setPage={setPage} />;
      case PAGES.INPUT: return <InputPage setPage={setPage} />;
      case PAGES.LOADING: return <LoadingPage setPage={setPage} />;
      case PAGES.TRIZ: return <TrizPage setPage={setPage} />;
      case PAGES.SIMILAR: return <SimilarPage setPage={setPage} />;
      case PAGES.EVASION: return <EvasionPage setPage={setPage} />;
      case PAGES.DRAFT: return <DraftPage setPage={setPage} />;
      case PAGES.DOWNLOAD: return <DownloadPage setPage={setPage} />;
      case PAGES.SEARCH: return <SearchPage setPage={setPage} />;
      default: return <LandingPage setPage={setPage} />;
    }
  };

  const pageNames = {
    [PAGES.LANDING]: "Landing",
    [PAGES.INPUT]: "Problem Input",
    [PAGES.LOADING]: "Analysis Loading",
    [PAGES.TRIZ]: "TRIZ Results",
    [PAGES.SIMILAR]: "Similar Patents",
    [PAGES.EVASION]: "Evasion Design",
    [PAGES.DRAFT]: "Patent Draft",
    [PAGES.DOWNLOAD]: "Download",
    [PAGES.SEARCH]: "Quick Search",
  };

  return (
    <div style={{ minHeight: "100vh", background: "#eef0f4", display: "flex", flexDirection: "column", alignItems: "center", padding: "24px 16px", fontFamily: "'Noto Sans KR', -apple-system, sans-serif" }}>
      {/* Page indicator */}
      <div style={{ marginBottom: 16, display: "flex", gap: 4, flexWrap: "wrap", justifyContent: "center" }}>
        {Object.entries(pageNames).map(([key, name]) => (
          <button
            key={key}
            onClick={() => setPage(key)}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              fontSize: 11,
              fontWeight: 600,
              border: "none",
              cursor: "pointer",
              background: page === key ? colors.primary : colors.white,
              color: page === key ? "#fff" : colors.textSec,
              boxShadow: page === key ? "none" : "0 1px 2px rgba(0,0,0,0.06)",
              transition: "all 0.2s",
            }}
          >
            {name}
          </button>
        ))}
      </div>

      <PhoneShell page={page} setPage={setPage}>
        {renderPage()}
      </PhoneShell>

      <div style={{ marginTop: 16, fontFamily: "monospace", fontSize: 11, color: colors.textMuted }}>
        Patent-GPT Interactive Prototype · {pageNames[page]}
      </div>
    </div>
  );
}
