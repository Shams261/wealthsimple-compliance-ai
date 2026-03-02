<div align="center">

# 🏛️ Wealthsimple Compliance AI

### AI-Native Regulatory Compliance Monitoring System

_Built for the [Wealthsimple AI Builders Program](https://www.wealthsimple.com/en-ca/careers/ai-builders)_

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white)](https://react.dev)
[![Tests](https://img.shields.io/badge/Tests-91%20passed-brightgreen?logo=pytest&logoColor=white)](#testing)
[![Eval](https://img.shields.io/badge/Eval-70%2F70%20%E2%9C%93-brightgreen)](#eval-harness)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo](https://wealthsimple-compliance-ai.onrender.com)** · **[API Docs](https://wealthsimple-compliance-ai.onrender.com/docs)** · **[Written Explanation (500 words)](docs/WRITTEN_EXPLANATION.md)** · **[Architecture](#architecture)**

</div>

---

## Table of Contents

- [The Problem](#the-problem)
- [What This System Does](#what-this-system-does)
- [The 4 Questions](#the-4-questions-this-project-answers)
- [Architecture](#architecture)
- [Data Flow](#data-flow--how-obligations-move-through-the-system)
- [User Flow](#user-flow)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Eval Harness](#eval-harness)
- [Testing](#testing)
- [Deployment](#deployment)
- [Design Decisions](#design-decisions)

---

## The Problem

Canadian financial institutions operate under a web of **overlapping regulators**: CSA, FINTRAC, CIRO, OSFI, CRA, and the Privacy Commissioner. When regulations change, compliance teams must:

1. **Read** dense legal text across multiple sources (hundreds of pages)
2. **Extract** specific obligations ("what must we do?")
3. **Map** obligations to products (which of our 6+ products are affected?)
4. **Check** existing controls (do we already handle this?)
5. **Flag** gaps and conflicts between different regulators
6. **Review** and approve — with full audit trail for regulatory exams

**This process takes weeks, costs millions industrywide, and a single missed obligation can trigger enforcement action or loss of registration.**

At Wealthsimple's scale — **6+ products, 3M+ users, $50B+ in assets** — the manual approach doesn't scale.

### Who Suffers Today?

| Stakeholder             | Pain                                                                 |
| ----------------------- | -------------------------------------------------------------------- |
| **Compliance Officers** | Drown in regulatory updates; can't process fast enough               |
| **Product Teams**       | Ship slowly waiting for compliance sign-off                          |
| **The Business**        | Bears regulatory risk from human error in a manual process           |
| **Clients**             | Indirectly affected when compliance gaps lead to service disruptions |

---

## What This System Does

This system **reads regulatory text, extracts obligations with evidence-first citations, maps them to Wealthsimple products and controls, detects cross-source conflicts, and enforces human review gates** — with a built-in eval harness that proves it works.

```
┌─────────────────────────────────────────────────────────────┐
│                   BEFORE (Manual Process)                     │
│                                                               │
│  Regulatory    →  Compliance    →  Spreadsheet  →  Manual    │
│  Update           Officer          Tracking        Review    │
│  Published        Reads 100+       Maps to         Takes     │
│                   pages            products        weeks     │
│                                                               │
│  ⏱️  Time: 2-4 weeks per regulatory update                    │
│  ❌ Error-prone: Human categorization misses edge cases       │
│  📊 No metrics: No way to measure accuracy or coverage        │
└─────────────────────────────────────────────────────────────┘

                          ↓ ↓ ↓

┌─────────────────────────────────────────────────────────────┐
│                   AFTER (This System)                         │
│                                                               │
│  Regulatory    →  AI Extracts   →  Auto-Maps    →  Human    │
│  Text Input       Obligations      Products &      Reviews   │
│  (Any source)     with Citations   Controls        Flagged   │
│                                                    Items     │
│                                                               │
│  ⏱️  Time: Seconds per regulatory update                      │
│  ✅ Evidence-first: Every obligation cites exact source text  │
│  📊 Measurable: 70-case eval harness proves accuracy          │
└─────────────────────────────────────────────────────────────┘
```

### Key Capabilities

| Capability                | Details                                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Regulatory Scanning**   | 10 Canadian regulatory sources (CSA, FINTRAC, CIRO, OSFI, PIPEDA, CRA, CDIC, Bank Act, NI 31-103, PCMLTFA) |
| **Obligation Extraction** | 25 domain-specific pattern matchers (KYC, AML, suitability, crypto custody, sanctions, etc.)               |
| **Product Mapping**       | Maps to 6 Wealthsimple products: Invest, Trade, Crypto, Tax, Cash, Options                                 |
| **Control Mapping**       | Maps to 14 existing controls (KYC onboarding, AML screening, suitability engine, etc.)                     |
| **Conflict Detection**    | 6 cross-source conflict rules (KYC timing, data retention vs. privacy, etc.)                               |
| **Risk Classification**   | 4-tier: Low → Medium → High → Critical with auto-escalation                                                |
| **Human Review**          | 4-role RBAC with atomic approve/reject/revert and full audit trail                                         |
| **LLM Analysis**          | Three-tier LLM chain: OpenRouter → Anthropic → Deterministic fallback                                      |
| **Eval Harness**          | 70 test cases, 6 metrics, proves the system works on real regulatory text                                  |

---

## The 4 Questions This Project Answers

### 1. What can the human now do that they couldn't before?

A compliance officer can now feed raw regulatory text — a new CSA bulletin, an OSFI guideline update, a FINTRAC advisory — and receive, in **seconds**, a structured obligation map:

- Every requirement **extracted** and described in plain language
- **Cited** with the exact source excerpt that creates the obligation (verbatim quote)
- **Risk-scored** (critical/high/medium/low) with transparent reasoning
- **Mapped** to affected Wealthsimple products (Invest, Trade, Crypto, Tax, Cash, Options)
- **Linked** to existing controls that already cover it (suitability engine, AML screening, etc.)
- **Conflicts detected** automatically — e.g., CSA requires KYC _before_ recommendations while FINTRAC allows 30 days post-opening

**Before:** A compliance officer reads a 50-page regulatory update for 2-4 weeks, manually categorizes obligations in spreadsheets, and hopes nothing is missed.

**After:** The same officer gets a complete, cited, risk-scored obligation map in seconds — then spends time on **judgment calls** (should we approve this? does this conflict matter?) instead of reading and categorizing.

### 2. What is AI responsible for?

The AI performs the **cognitive heavy-lifting** that compliance analysts do today:

```
AI Responsibilities:
├── Extract obligations from regulatory language
├── Identify the specific domain (KYC, AML, suitability, etc.)
├── Map to affected Wealthsimple products
├── Map to existing controls that cover the obligation
├── Assign risk levels based on domain severity
├── Calculate confidence scores based on evidence strength
├── Detect conflicts between different regulatory sources
├── Cite exact source text for every obligation
└── Flag items that need human review with specific reasons
```

The AI is a **force multiplier**: it turns a 2-week manual process into a 10-second automated scan, but it **never makes final decisions** on high-stakes items.

### 3. Where must AI stop?

This is the most important question. The system has **hard-coded boundaries** where AI stops and humans take over:

```
┌──────────────────────────────────────────────────────┐
│              AUTO-ESCALATION TRIGGERS                  │
│                                                        │
│  🔴 Risk = HIGH or CRITICAL                           │
│     → Mandatory human review (AML, KYC, sanctions)    │
│                                                        │
│  🟡 Confidence = LOW                                  │
│     → "Insufficient evidence → needs human review"    │
│                                                        │
│  🟠 No citation found                                │
│     → AI won't process without evidence               │
│                                                        │
│  🔵 Customer-facing change detected                  │
│     → Always requires human sign-off                  │
│                                                        │
│  ⚫ Policy conflict between sources                  │
│     → Both excerpts surfaced, never auto-resolved     │
│                                                        │
│  Every obligation: Draft → Reviewed → Approved/Rejected│
│  Every action logged in immutable audit trail          │
└──────────────────────────────────────────────────────┘
```

**In code** (from [`backend/models.py`](backend/models.py)):

```python
def __post_init__(self):
    # Auto-flag for human review — these rules are NOT configurable by AI
    if self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        self.requires_human_review = True
        self.escalation_reasons.append(EscalationReason.HIGH_RISK)
    if self.confidence == ConfidenceLevel.LOW:
        self.requires_human_review = True
        self.escalation_reasons.append(EscalationReason.LOW_CONFIDENCE)
    if self.citation is None:
        self.requires_human_review = True
        self.escalation_reasons.append(EscalationReason.INSUFFICIENT_EVIDENCE)
```

The system **amplifies human judgment; it never replaces it** on decisions that carry regulatory or reputational risk.

### 4. What would break first at scale?

| Scaling Challenge           | Why It Breaks                                                                                            | Mitigation Strategy                                                                      |
| --------------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Keyword brittleness**     | Deterministic engine uses keyword matching — effective for structured text but brittle on novel language | Three-tier LLM chain already built; deterministic engine serves as eval baseline         |
| **Human review bottleneck** | If 80% of obligations need review, the system shifts work rather than reducing it                        | Confidence tuning + domain-specific review routing by role                               |
| **Conflict combinatorics**  | Cross-jurisdictional expansion multiplies N×N conflict detection                                         | Priority-based conflict rules + domain indexing (O(n) per rule)                          |
| **Regulatory ambiguity**    | Same phrase can create different obligations depending on context                                        | LLM integration with citation-grounded reasoning; deterministic as safety net            |
| **Real-time ingestion**     | Canada Gazette, CSA notices need polling infrastructure                                                  | Architecture supports webhook-triggered analysis; needs infra layer                      |
| **Multi-jurisdiction**      | International expansion needs jurisdiction-specific patterns                                             | Modular pattern system (`OBLIGATION_PATTERNS` dict) supports per-jurisdiction extensions |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                          │
│                                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐    │
│  │   Frontend   │    │  FastAPI      │    │  Compliance Engine   │    │
│  │   React 18   │◄──►│  REST API     │◄──►│  analyzer.py         │    │
│  │   6-Tab SPA  │    │  17 Endpoints │    │                      │    │
│  │              │    │              │    │  ┌─────────────────┐  │    │
│  │  • Dashboard │    │  Middleware:  │    │  │  Deterministic  │  │    │
│  │  • Analyze   │    │  • Rate Limit│    │  │  25 Domain      │  │    │
│  │  • Eval      │    │  • CORS      │    │  │  Patterns       │  │    │
│  │  • Audit Log │    │  • Logging   │    │  └────────┬────────┘  │    │
│  │  • Cache     │    │  • Error     │    │           │           │    │
│  │  • Admin     │    │    Handler   │    │  ┌────────▼────────┐  │    │
│  └─────────────┘    └──────────────┘    │  │  LLM Chain      │  │    │
│                                          │  │  OpenRouter →   │  │    │
│                                          │  │  Anthropic →    │  │    │
│                                          │  │  Deterministic  │  │    │
│                                          │  └────────┬────────┘  │    │
│                                          │           │           │    │
│                                          │  ┌────────▼────────┐  │    │
│                                          │  │ Conflict Detect │  │    │
│                                          │  │ 6 Cross-Source  │  │    │
│                                          │  │ Rules           │  │    │
│                                          │  └─────────────────┘  │    │
│                                          └──────────────────────┘    │
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐    │
│  │  SQLite DB   │    │  LLM Cache   │    │  Eval Harness        │    │
│  │  (WAL mode)  │    │  (JSON file) │    │  70 test cases       │    │
│  │              │    │              │    │  6 metrics            │    │
│  │  • State     │    │  • SHA-256   │    │  ≥97% accuracy       │    │
│  │  • Reviews   │    │    keying    │    │                      │    │
│  │  • Audit Log │    │  • TTL-based │    │  91 pytest tests     │    │
│  │  • RBAC      │    │  • Thread-   │    │  <1s execution       │    │
│  │              │    │    safe      │    │                      │    │
│  └──────────────┘    └──────────────┘    └──────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

| Decision                      | Reasoning                                                                                          |
| ----------------------------- | -------------------------------------------------------------------------------------------------- |
| **Single-process deployment** | Frontend served by FastAPI → no CORS issues, one URL, one Dockerfile                               |
| **SQLite with WAL mode**      | Zero-config persistence, concurrent reads, atomic transactions — swap to PostgreSQL for production |
| **Three-tier LLM chain**      | OpenRouter → Anthropic → Deterministic ensures the app **always works** even without API keys      |
| **JSON file cache**           | SHA-256 keyed, TTL-based, thread-safe — saves API costs without external dependencies              |
| **Deterministic baseline**    | 25 keyword patterns provide an eval-testable, LLM-independent safety net                           |

---

## Data Flow — How Obligations Move Through the System

```
                    ┌─────────────────────┐
                    │  REGULATORY TEXT     │
                    │  (10 sources or      │
                    │   free-text input)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  OBLIGATION          │
                    │  EXTRACTION          │
                    │                      │
                    │  For each domain:    │
                    │  1. Keyword match    │
                    │  2. Extract citation │
                    │  3. Score confidence │
                    │  4. Classify risk    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  PRODUCT & CONTROL   │
                    │  MAPPING             │
                    │                      │
                    │  Domain → Products:  │
                    │  KYC → [Invest,      │
                    │   Trade, Crypto,     │
                    │   Cash, Options]     │
                    │                      │
                    │  Domain → Controls:  │
                    │  KYC → [ctrl_kyc_    │
                    │   onboarding]        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  AUTO-ESCALATION     │
                    │  ENGINE              │
                    │                      │
                    │  Check triggers:     │
                    │  • High/Critical risk│
                    │  • Low confidence    │
                    │  • Missing citation  │
                    │  • Customer-facing   │
                    │  • Policy conflict   │
                    │                      │
                    │  → Set human_review  │
                    │    = true / false    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  CONFLICT DETECTION  │
                    │                      │
                    │  6 cross-source      │
                    │  rules checked:      │
                    │  • KYC timing        │
                    │  • Retention vs      │
                    │    privacy           │
                    │  • Suitability vs    │
                    │    best execution    │
                    │  • Privacy vs AML    │
                    │  • Retention vs      │
                    │    breach            │
                    │  • Restrictions vs   │
                    │    fundamental       │
                    │    changes           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  PERSISTENCE         │
                    │                      │
                    │  SQLite (WAL mode):  │
                    │  • analysis_state    │
                    │  • review_history    │
                    │  • audit_log         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  HUMAN REVIEW        │
                    │  WORKFLOW             │
                    │                      │
                    │  Draft               │
                    │    ↓                 │
                    │  Reviewed            │
                    │    ↓                 │
                    │  Approved / Rejected │
                    │    ↓ (admin only)    │
                    │  Reverted            │
                    │                      │
                    │  RBAC enforced:      │
                    │  4 roles, atomic     │
                    │  transactions        │
                    └─────────────────────┘
```

### Obligation Lifecycle

```
  ┌────────┐    AI Extracts    ┌─────────┐    Officer Reviews    ┌──────────┐
  │ Source  │ ──────────────► │  DRAFT   │ ────────────────────► │ APPROVED │
  │ Text   │                  │          │                       │          │
  └────────┘                  │ • Cited  │    or                 └──────────┘
                              │ • Scored │    ↓
                              │ • Mapped │ ┌──────────┐
                              └─────────┘ │ REJECTED  │
                                   ↑      └──────────┘
                                   │           ↑
                              Admin Revert     │
                              (with audit)─────┘
```

---

## User Flow

### Flow 1: Regulatory Source Scanning

```
User clicks "Scan Regulatory Sources"
    │
    ├─► System reads 10 regulatory sources (47 sections)
    │
    ├─► For each section, 25 domain matchers run
    │
    ├─► Obligations created with:
    │   • Cited excerpt from source text
    │   • Risk level (low/medium/high/critical)
    │   • Confidence score
    │   • Product mapping
    │   • Control mapping
    │   • Escalation flags
    │
    ├─► Conflict detection runs across all obligations
    │
    └─► Dashboard shows obligation cards with filters
        User can approve/reject each with role-based access
```

### Flow 2: Free-Text LLM Analysis

```
User pastes regulatory text → Clicks "Analyze with AI"
    │
    ├─► Three-tier LLM chain:
    │   1. Check LLM cache (SHA-256 key) → hit? Return cached
    │   2. Try OpenRouter (Claude 3.5 Sonnet) → success? Cache & return
    │   3. Try Anthropic SDK → success? Cache & return
    │   4. Fallback: Deterministic engine (always works)
    │
    ├─► LLM output normalized:
    │   • Domain names case-insensitive matched
    │   • Missing products backfilled from pattern
    │   • Controls mapped from domain patterns
    │   • Malformed JSON handled gracefully
    │
    └─► Obligations displayed with same card UI
```

### Flow 3: Human Review Workflow

```
Compliance Officer sees flagged obligation
    │
    ├─► Checks citation (exact source text linked)
    ├─► Checks risk level and confidence
    ├─► Checks mapped products and controls
    │
    ├─► Decision:
    │   ├─► APPROVE → Status changes, audit log entry
    │   ├─► REJECT  → Status changes, audit log entry
    │   └─► (Admin) REVERT → Restores previous status
    │
    └─► All actions recorded in:
        • SQLite review_history table
        • In-memory audit log
        • Timestamped with role attribution
```

---

## Tech Stack

| Layer         | Technology                           | Why                                       |
| ------------- | ------------------------------------ | ----------------------------------------- |
| **Backend**   | Python 3.10+, FastAPI, uvicorn       | Async, auto-docs (Swagger), type-safe     |
| **Frontend**  | React 18 (no build step)             | Interactive SPA, served by FastAPI        |
| **LLM**       | OpenRouter API (Claude 3.5 Sonnet)   | Multi-model access, Anthropic fallback    |
| **Database**  | SQLite (WAL mode)                    | Zero-config, concurrent reads, atomic ops |
| **Cache**     | JSON file (SHA-256 keyed)            | Thread-safe, TTL-based, zero dependencies |
| **Testing**   | pytest (91 tests)                    | Fast (<1s), comprehensive coverage        |
| **Eval**      | Custom harness (70 cases, 6 metrics) | Proves accuracy on real regulatory text   |
| **Container** | Docker (gunicorn + uvicorn workers)  | Production-ready, cloud-deployable        |
| **Security**  | Rate limiting, CORS, RBAC            | Per-IP token bucket, configurable origins |

---

## Project Structure

```
wealthsimple-compliance-ai/
│
├── backend/                     # Core application
│   ├── server.py                # FastAPI server (17 endpoints, middleware, RBAC)
│   ├── analyzer.py              # Compliance engine (25 patterns, LLM chain, conflicts)
│   ├── models.py                # Frozen dataclasses, enums, auto-escalation logic
│   ├── storage.py               # SQLite persistence, atomic review, RBAC, revert
│   └── llm_cache.py             # Persistent LLM cache (SHA-256, TTL, thread-safe)
│
├── data/
│   └── regulatory_sources.py    # 10 sources, 47 sections, 6 products, 14 controls
│
├── eval/
│   ├── test_cases.py            # 70 eval test cases across 25 domains
│   └── run_eval.py              # Eval runner with 6 metrics
│
├── frontend/
│   ├── index.html               # SPA entry point
│   ├── styles.css               # Full CSS with custom properties
│   └── js/
│       ├── app-main.jsx         # Main app (6 tabs, role selector)
│       ├── components.jsx       # Reusable UI components
│       ├── data.js              # Demo data and constants
│       ├── icons.jsx            # SVG icon components
│       ├── namespace.js         # App namespace setup
│       └── utils.js             # Formatting helpers
│
├── tests/                       # 91 pytest tests
│   ├── conftest.py              # Shared fixtures
│   ├── test_analyzer.py         # Engine tests (20)
│   ├── test_api.py              # API endpoint tests (23)
│   ├── test_models.py           # Model tests (9)
│   ├── test_storage.py          # Storage + RBAC tests (16)
│   ├── test_cache.py            # Cache tests (7)
│   └── test_eval.py             # Eval harness tests (3)
│
├── docs/                        # Submission documents
│   ├── PABCF_500_WORDS.md       # 500-word written explanation
│   └── AI_BUILDERS_SUBMISSION.md # Detailed 4-question answers
│
├── Dockerfile                   # Production container (gunicorn + uvicorn)
├── Makefile                     # 9 developer targets
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── .gitignore                   # Comprehensive ignore rules
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- (Optional) OpenRouter API key for LLM features

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Shams261/wealthsimple-compliance-ai.git
cd wealthsimple-compliance-ai

# Set up environment
cp .env.example .env
# Edit .env to add OPENROUTER_API_KEY (optional — system works without it)

# Install dependencies
make install

# Run the server
make run
# → Open http://localhost:8000
```

### With Docker

```bash
make docker-run
# → Open http://localhost:8000
```

### Run Tests

```bash
make test   # 91 tests, <1s
make eval   # 70 eval cases, 6 metrics
```

---

## API Reference

The system exposes **17 REST endpoints**. Full interactive documentation available at [`/docs`](https://wealthsimple-compliance-ai.onrender.com/docs) (auto-generated Swagger UI).

### Core Endpoints

| Method | Endpoint            | Description                                                  |
| ------ | ------------------- | ------------------------------------------------------------ |
| `GET`  | `/api/health`       | Comprehensive health check (DB, analyzer, cache, LLM status) |
| `GET`  | `/api/sources`      | List all 10 regulatory sources                               |
| `GET`  | `/api/products`     | List all 6 Wealthsimple products                             |
| `GET`  | `/api/controls`     | List all 14 existing controls                                |
| `POST` | `/api/analyze`      | Run full regulatory scan (all sources or by source_id)       |
| `GET`  | `/api/analysis`     | Get last analysis result                                     |
| `POST` | `/api/analyze-text` | Analyze free-text via LLM chain                              |

### Human Review Endpoints

| Method | Endpoint                   | Description                               |
| ------ | -------------------------- | ----------------------------------------- |
| `POST` | `/api/review`              | Approve/reject obligation (RBAC enforced) |
| `GET`  | `/api/review/history/{id}` | Full review history for an obligation     |
| `POST` | `/api/review/revert`       | Admin-only revert of last review action   |
| `GET`  | `/api/roles`               | List all roles and their permissions      |
| `GET`  | `/api/audit-log`           | Full system audit log                     |

### Eval and Cache Endpoints

| Method | Endpoint                 | Description                               |
| ------ | ------------------------ | ----------------------------------------- |
| `GET`  | `/api/eval/run`          | Run 70-case eval harness, return metrics  |
| `POST` | `/api/eval/test-snippet` | Test any snippet against expected values  |
| `GET`  | `/api/cache/stats`       | LLM cache statistics (hits, misses, size) |
| `POST` | `/api/cache/clear`       | Clear all cached LLM responses            |

### Example: Analyze Regulatory Text

```bash
curl -X POST https://wealthsimple-compliance-ai.onrender.com/api/analyze-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "All dealers must implement enhanced due diligence for politically exposed persons including ongoing monitoring of transactions exceeding $10,000 CAD."
  }'
```

---

## Eval Harness

The eval harness is the **proof that the system works**. It is not a toy demo — it is a measurable, reproducible accuracy benchmark.

### 70 Test Cases x 6 Metrics

```
$ python -m eval.run_eval

Evaluation Results:
   obligation_detection : 100.00%  ← Did we find obligations?
   domain_classification: 100.00%  ← Correct regulatory domain?
   risk_assessment      : 100.00%  ← Correct risk level?
   citation_quality     : 100.00%  ← Are citations present?
   product_mapping      : 100.00%  ← Correct products mapped?
   control_mapping      :  97.14%  ← Correct controls mapped?

  70/70 test cases passed
```

### Why 97.14% on Control Mapping?

2 of 70 test cases have edge-case controls that the deterministic engine does not map perfectly (e.g., a new control type not in the current 14). This is **honest scoring, not inflated**. The LLM chain handles these edge cases correctly.

### Domain Coverage

The 70 test cases cover all 25 regulatory domains:

`KYC` · `AML` · `suitability` · `KYP` · `best_execution` · `complaint_handling` · `EFT_reporting` · `PEP_screening` · `investment_restrictions` · `privacy` · `breach_notification` · `data_retention` · `tax_reporting` · `relationship_disclosure` · `compliance_framework` · `compliance_testing` · `fundamental_changes` · `risk_assessment` · `record_keeping` · `capital_requirements` · `outsourcing` · `margin_requirements` · `crypto_custody` · `sanctions` · `client_reporting`

---

## Testing

### 91 Tests in Under 1 Second

```
$ make test

tests/test_analyzer.py    20 passed  ← Engine, patterns, risk scoring
tests/test_api.py         23 passed  ← All 17 endpoints + rate limiting
tests/test_models.py       9 passed  ← Dataclasses, auto-escalation
tests/test_storage.py     16 passed  ← SQLite, RBAC, atomic review, revert
tests/test_cache.py        7 passed  ← Cache set/get, TTL, stats
tests/test_eval.py         3 passed  ← Eval runner, score thresholds

91 passed in 0.67s
```

### What the Tests Verify

- **Analyzer:** All 25 domain patterns extract correctly; risk levels and confidence scores are assigned properly
- **API:** Every endpoint responds correctly, including edge cases (empty text, invalid roles, rate limits returning 429)
- **Models:** Frozen dataclasses prevent mutation; auto-escalation triggers correctly for all combinations
- **Storage:** Atomic review prevents race conditions; RBAC denies unauthorized actions; revert restores previous state
- **Cache:** SHA-256 keys are deterministic; TTL expiry works; thread-safety under concurrent access
- **Eval:** All 6 metrics stay above 90% — this is the regression guard

---

## Deployment

### Live on Render

The app is deployed at **[wealthsimple-compliance-ai.onrender.com](https://wealthsimple-compliance-ai.onrender.com)**

### Deploy Your Own

```bash
# Option 1: Render (recommended)
# Push to GitHub → New Web Service → Docker → Add env vars

# Option 2: Railway
brew install railway && railway login && railway up

# Option 3: Docker anywhere
docker build -t compliance-ai .
docker run -p 8000:8000 --env-file .env compliance-ai
```

### Environment Variables

| Variable             | Required | Default | Description                                   |
| -------------------- | -------- | ------- | --------------------------------------------- |
| `OPENROUTER_API_KEY` | No       | —       | Enables LLM-powered analysis                  |
| `ALLOWED_ORIGINS`    | No       | `*`     | CORS origins (comma-separated for production) |
| `RATE_LIMIT_RPM`     | No       | `60`    | Max API requests per minute per IP            |
| `PORT`               | No       | `8000`  | Server port (auto-set by Render/Railway)      |
| `LLM_CACHE_TTL_DAYS` | No       | `30`    | Cache expiry in days                          |

---

## Design Decisions

### Why Evidence-First Citations?

In regulated industries, "the AI said so" is not acceptable. Every obligation must trace back to a specific excerpt from a specific regulatory document. If the system cannot find the evidence, it explicitly says "Insufficient evidence → needs human review" instead of guessing. This is the **fundamental design principle** — no hallucinated obligations.

### Why Deterministic + LLM?

The deterministic engine (25 keyword patterns) serves three purposes:

1. **Eval baseline:** Reproducible accuracy without API costs
2. **Safety net:** Always works, even offline or without API keys
3. **Ground truth:** LLM output is normalized against the same domain/product/control mappings

The LLM chain adds reasoning over novel regulatory language that keyword matching cannot handle.

### Why Not a Separate Frontend?

Single-process deployment (FastAPI serves React) means:

- No CORS configuration needed in development
- One URL to share (no "API at X, frontend at Y")
- One Dockerfile, one deployment, one health check
- Simpler for reviewers to run locally

### Why SQLite?

- Zero configuration (no database server to install)
- WAL mode gives concurrent reads without locks
- Atomic transactions prevent race conditions in reviews
- For production: swap `_connect()` to return a PostgreSQL connection — the rest of the code is unchanged

---

## 6-Month Roadmap at Wealthsimple

| Phase       | What                                                                                 | Impact                                        |
| ----------- | ------------------------------------------------------------------------------------ | --------------------------------------------- |
| **Month 1** | Replace keyword matching with LLM extraction, validated against 70-case eval harness | No regression, better accuracy on novel text  |
| **Month 2** | Integrate with Wealthsimple's internal control inventory and product registry        | Live gap analysis instead of static mappings  |
| **Month 3** | Real-time regulatory feed ingestion (Canada Gazette, CSA, FINTRAC)                   | Push alerts when new obligations are detected |
| **Month 4** | Regulatory change diffing — when amendments are published, show what changed         | Compliance team focuses only on deltas        |
| **Month 5** | Multi-reviewer workflow with escalation chains and SLA tracking                      | Scale human review across the compliance team |
| **Month 6** | Dashboard for executive reporting and regulatory exam preparation                    | Board-ready compliance posture reports        |

---

<div align="center">

**Built with conviction that AI should amplify human judgment, not replace it.**

Built by [Shams Tabrez](https://github.com/Shams261) for the [Wealthsimple AI Builders Program](https://www.wealthsimple.com/en-ca/careers/ai-builders)

</div>
