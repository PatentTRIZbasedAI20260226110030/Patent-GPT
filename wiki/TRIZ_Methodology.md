# TRIZ Methodology

## What is TRIZ?

**TRIZ** (Teoriya Resheniya Izobretatelskikh Zadach / 발명 문제 해결 이론) is a systematic methodology for inventive problem-solving developed by Genrich Altshuller. By analyzing over 200,000 patents, Altshuller identified 40 recurring inventive principles that appear across all domains of engineering and technology.

The key insight: **inventive solutions are not random** — they follow repeatable patterns.

## The 40 Inventive Principles

Patent-GPT uses all 40 TRIZ principles stored in `data/triz_principles.json`:

### Structural / Geometric

| # | Principle (EN) | 원리 (KO) | Description |
| :--: | :-- | :-- | :-- |
| 1 | Segmentation | 분할 | Divide an object into independent parts |
| 2 | Taking out | 추출 | Separate an interfering part or property |
| 3 | Local quality | 국소적 품질 | Change from uniform to non-uniform structure |
| 4 | Asymmetry | 비대칭 | Change symmetrical form to asymmetrical |
| 5 | Merging | 통합 | Combine identical or similar objects |
| 6 | Universality | 범용성 | Make a part perform multiple functions |
| 7 | Nested doll | 포개기 | Place one object inside another |
| 14 | Spheroidality | 곡면화 | Move from flat to curved surfaces |
| 17 | Another dimension | 차원 변경 | Move from 1D to 2D to 3D |

### Dynamic / Adaptive

| # | Principle (EN) | 원리 (KO) | Description |
| :--: | :-- | :-- | :-- |
| 8 | Anti-weight | 반중력 | Compensate weight with lift or buoyancy |
| 9 | Preliminary anti-action | 사전 반대 작용 | Pre-stress to counteract harmful effects |
| 10 | Preliminary action | 사전 작용 | Pre-arrange objects for convenient use |
| 11 | Beforehand cushioning | 사전 예방 | Prepare emergency measures in advance |
| 15 | Dynamics | 역동성 | Allow characteristics to adapt in real time |
| 20 | Continuity of useful action | 유용한 작용의 지속 | Carry on work continuously |
| 21 | Skipping | 고속 처리 | Conduct a process at high speed |

### Physical / Chemical

| # | Principle (EN) | 원리 (KO) | Description |
| :--: | :-- | :-- | :-- |
| 18 | Mechanical vibration | 기계적 진동 | Use oscillation or resonance |
| 19 | Periodic action | 주기적 작용 | Replace continuous with periodic action |
| 29 | Pneumatics / hydraulics | 유압/공압 | Use gas or liquid instead of solid parts |
| 30 | Flexible shells / thin films | 유연한 막 | Use flexible shells or thin films |
| 31 | Porous materials | 다공성 물질 | Make an object porous or add porous elements |
| 35 | Parameter changes | 매개변수 변경 | Change physical state, concentration, etc. |
| 36 | Phase transitions | 상전이 | Use phase transition effects |
| 38 | Strong oxidants | 강한 산화제 | Replace normal air with enriched air or oxygen |
| 39 | Inert atmosphere | 불활성 환경 | Replace normal environment with inert one |

### Information / Control

| # | Principle (EN) | 원리 (KO) | Description |
| :--: | :-- | :-- | :-- |
| 12 | Equipotentiality | 등전위 | Eliminate the need to raise or lower objects |
| 13 | The other way round | 반전 | Invert the action or process |
| 16 | Partial or excessive actions | 과부족 | If 100% is hard, do slightly more or less |
| 22 | Blessing in disguise | 전화위복 | Use harmful factors to achieve positive effect |
| 23 | Feedback | 피드백 | Introduce feedback to improve a process |
| 24 | Intermediary | 중간 매개체 | Use an intermediate carrier or process |
| 25 | Self-service | 셀프 서비스 | Make an object serve and maintain itself |
| 26 | Copying | 복사 | Use simpler copies instead of originals |
| 27 | Cheap short-living | 일회용 | Replace expensive durable with cheap disposable |
| 28 | Replace mechanical | 기계 시스템 대체 | Replace mechanical means with sensory |
| 32 | Color changes | 색상 변경 | Change color or transparency |
| 33 | Homogeneity | 동질성 | Make interacting objects from same material |
| 34 | Discarding / recovering | 폐기 및 재생 | Discard after use or restore during use |
| 37 | Thermal expansion | 열팽창 | Use thermal expansion or contraction |
| 40 | Composite materials | 복합 재료 | Replace homogeneous with composite materials |

## How Patent-GPT Uses TRIZ

### Dual Router: Contradiction Matrix + LLM (or ML)

Patent-GPT supports two classification paths via `TRIZ_ROUTER`:

**LLM path** (default):
1. LLM extracts **improving/worsening engineering parameters** from the problem
2. Look up Altshuller's **39×39 Contradiction Matrix** → recommended principles
3. LLM selects **top-3 principles** guided by matrix + few-shot prompting

**ML path**:
- TF-IDF + XGBoost model trained on labeled TRIZ problem data
- Low-latency, deterministic classification without API calls

### The Contradiction Matrix

The 39×39 matrix maps pairs of engineering parameters (improving vs. worsening) to suggested principles:

| Aspect | Matrix Only | Patent-GPT (Matrix + LLM) |
| :-- | :-- | :-- |
| Input | Must identify exact parameter pair | Natural language description |
| Parameter extraction | Manual | LLM-automated |
| Principle selection | Fixed lookup | Matrix-guided + LLM reasoning |
| Explanation | Principle numbers only | Natural language reasoning |

### Example Flow

```
User: "배터리 충전이 너무 오래 걸린다" (Battery charging takes too long)
         │
         ▼
   TRIZ Classifier (matrix + LLM)
   → Improving: Speed, Worsening: Energy loss
   → Matrix recommends: #21, #28, #35
   → LLM selects top-3 with reasoning
   → Idea: "무선 충전 중 열에너지를 재활용하여 충전 속도를 높이는 시스템"
         │
         ▼
   Patent Searcher (Hybrid)
   → Found 5 similar patents, top score: 0.85
         │
         ▼
   Reasoning Agent
   → Score 0.85 > threshold 0.50 → trigger evasion
   → Redesign with Principle #22 (전화위복)
   → Re-search: top score now 0.42 → pass
         │
         ▼
   Draft Generator → KIPO format patent draft + DOCX
```

## References

- Altshuller, G. (1984). *Creativity as an Exact Science*
- [TRIZ Journal](https://triz-journal.com/)
- [Oxford Creativity — TRIZ Effects Database](https://www.triz.co.uk/)
