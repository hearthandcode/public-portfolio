# Session Logging Protocol — When the Studied Tool Is Also the Data Collection Instrument

## Core Principle

When the AI agent is **both the studied phenomenon AND the data-collection instrument**, treat it as a **dual-role artifact** requiring parallel logging streams that are explicitly bridged in the methodological log.

---

## 8 Concrete Protocol Implications

### 1. Four-Part Log Structure (Lincoln & Guba + Ortlipp)
```
session_log/
├── schedule_logistics.md      # timestamps, model params, context window, task intent
├── affective_diary.md         # lived experience: affect, surprise, friction, flow, executive function state
├── methodological_log.md      # decisions + rationale, coupling-failure tags, recovery actions, alternative paths
└── ai_interaction_transcript/ # raw prompt/response pairs with metadata (JSONL)
```

**Mapping to trustworthiness criteria:**
- `schedule_logistics` → **dependability** (traceable process)
- `affective_diary` → **confirmability** (researcher influence documented)
- `methodological_log` → **credibility** (decision audit trail)
- `ai_interaction_transcript` → **transferability** (thick description for context matching)

---

### 2. Pre-Session Cognitive Baseline Entry
**Required fields (before any AI interaction):**
```markdown
## Pre-Session Baseline — YYYY-MM-DD HH:MM
- **Intent**: What question am I bringing to this session?
- **Energy**: 1-10 scale + qualitative note (focused/scattered/fatigued/hyperfocused)
- **Executive Function State**: initiation_easy / initiation_hard / switching_cost_high
- **Expectations**: What do I predict will happen? What would "good coupling" feel like?
- **Blind Spot Hypothesis**: What might I miss because of my current state?
```

---

### 3. Post-Session Cognitive Delta Entry
**Required fields (immediately after session):**
```markdown
## Post-Session Delta — YYYY-MM-DD HH:MM
- **Understanding Shift**: What do I now understand that I didn't before?
- **Affect Trace**: frustration → curiosity → flow → fatigue (tag transitions)
- **Executive Function Recovery**: recovered / partial / depleted
- **Coupling Quality**: smooth / intermittent / failed → recovered / failed → abandoned
- **Key Insight**: One sentence capture of the most valuable emergent finding
- **Methodological Decision**: Did I change approach mid-session? Why?
```

---

### 4. Coupling-Failure Tagging Scheme
**Standardized codes (append to methodological_log entries):**
| Tag | Definition | Example |
|-----|------------|---------|
| `CF-LATENCY` | Tool response time broke flow | >30s wait for model response |
| `CF-MISALIGNMENT` | Output didn't match intent despite clear prompt | Asked for summary, got code |
| `CF-HALLUCINATION` | Fabricated content presented as fact | Invented citation, fake API |
| `CF-CONTEXT-LOSS` | Model lost thread context | Forgot earlier constraint |
| `CF-RECOVERY-ACTION` | Explicit step taken to recover | Re-prompted with context, switched model, manual edit |

**Each tag entry must include:** timestamp, turn number, recovery time (turns), subjective friction (1-5)

---

### 5. Human-Review Checkpoint (Weekly Adjudication)
**Cadence:** Every 7 sessions or calendar week, whichever comes first
**Process (per Lee & Yi 2025):**
1. Export session bundle: raw logs + coded segments + reviewer memos
2. Human reviewer codes AI-assisted themes vs. raw log excerpts
3. Produce **traceability matrix**: theme → supporting log excerpt → reviewer confidence (A/B/C)
4. Update versioned codebook with adjudicated codes
5. Flag any `CF-*` patterns recurring >3 times/week for protocol revision

---

### 6. Thick-Description Minima (Per Entry)
**Every `affective_diary` and `methodological_log` entry must include:**
- **Sensory/contextual detail**: Where am I? Time? Device? Ambient conditions?
- **Internal monologue excerpt**: Verbatim thought at decision point (1-3 sentences)
- **Decision-point rationale**: Why this action, not the alternative?
- **Alternative paths considered**: At least one explicit counterfactual

*This satisfies Geertz's "thick description" and Lincoln & Guba's "widest possible range of information for inclusion in the thick description"*

---

### 7. Positionality Refresh (Monthly)
**300-word statement addressing:**
```markdown
## Positionality Refresh — YYYY-MM
- **Relationship Shift**: How has my relationship to the tool changed this month?
- **Emergent Blind Spots**: What am I now NOT seeing that I was seeing before?
- **Power Dynamics**: Who is driving — me or the tool? Where did agency shift?
- **Epistemic Stance**: Am I treating the tool as oracle, partner, mirror, or phenomenon?
- **Ethical Tension**: Any moment where tool use felt extractive or self-betraying?
```

---

### 8. Audit-Trail Export (Weekly JSON Bundle)
**Format mapping to Halpern's 6 categories:**
```json
{
  "week": "YYYY-WW",
  "raw_data": ["schedule_logistics.md", "ai_interaction_transcript/*.jsonl"],
  "data_reduction": ["coded_segments.csv", "theme_frequency.json"],
  "data_reconstruction": ["synthesized_findings.md", "traceability_matrix.csv"],
  "process_notes": ["methodological_log.md", "coupling_failure_log.csv"],
  "intentions_dispositions": ["pre_session_baselines/*.md", "post_session_deltas/*.md", "positionality_refresh.md"],
  "instrument_development": ["prompt_templates/*.md", "model_configs/*.json", "tagging_scheme_vN.md"]
}
```

---

## Dual-Role Artifact Handling: The Bridge

**Critical protocol rule:** Every `methodological_log` entry that references an AI interaction **must** explicitly link the two modes:

```
[Instrument Mode] At 14:23 the model hallucinated a function signature
        ↓
[Affective Mode] I felt frustration (chest tightness, urge to abandon)
        ↓
[Methodological Mode] I switched to verification protocol (re-prompted with "cite source")
        ↓
[Coupling Metric] Recovery took 3 turns, friction=4/5
```

**This satisfies:**
- Lincoln & Guba: human instrument documented as thoroughly as brass instruments
- Autoethnography intimacy epistemology: self-study co-constructed with the tool
- Confirmability: data-based warrants for every interpretive claim
- Dependability: logical, documented, traceable process from raw interaction to finding

---

## Quick-Reference Card

| When... | Log To... | Tag With... |
|---------|-----------|-------------|
| Starting session | `schedule_logistics` + `affective_diary` (baseline) | `PRE-SESSION` |
| AI responds | `ai_interaction_transcript` (auto) | turn_number, model, params |
| I feel something | `affective_diary` | `AFFECT`, `CF-*` if coupling issue |
| I make a decision | `methodological_log` | `DECISION`, rationale, alternatives |
| Session ends | `affective_diary` (delta) + `schedule_logistics` (closure) | `POST-SESSION` |
| Weekly | Export JSON bundle + human review | `WEEKLY-AUDIT` |
| Monthly | Positionality refresh | `POSITIONALITY` |