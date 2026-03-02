# Wealthsimple AI Builders — Written Explanation

**Applicant:** Shams Tabrez  
**Project:** Regulatory Compliance AI — AI-Native Monitoring System for Canadian Financial Regulation  
**Live Demo:** [wealthsimple-compliance-ai.onrender.com](https://wealthsimple-compliance-ai.onrender.com)  
**Source Code:** [github.com/Shams261/wealthsimple-compliance-ai](https://github.com/Shams261/wealthsimple-compliance-ai)

---

## 1. What can the human now do that they couldn't before?

A compliance officer at a CIRO-registered dealer like Wealthsimple spends 2-4 weeks per regulatory update: reading 50-100 pages of dense legal text, manually extracting obligations, categorizing them in spreadsheets, mapping them to products, and checking whether existing controls cover them. This is the bottleneck — not the decision-making, but the **reading, extracting, and mapping**.

This system eliminates that bottleneck entirely.

A compliance officer can now:

- **Paste any regulatory text** (a new CSA Notice, an OSFI guideline update, a FINTRAC advisory) and receive a complete obligation map in seconds — not weeks.
- **See exactly why** each obligation was extracted: the system cites the **verbatim excerpt** from the source text that creates the obligation. No black-box outputs.
- **Know which products are affected**: each obligation is automatically mapped to affected Wealthsimple products (Invest, Trade, Crypto, Tax, Cash, Options).
- **See what's already covered**: each obligation is mapped to existing controls (KYC onboarding, AML screening, suitability engine, etc.), instantly showing gaps.
- **Catch conflicts they'd miss**: the system detects contradictions between regulators — for example, CSA requires KYC completion _before_ making investment recommendations, but FINTRAC allows 30 days post-account-opening to complete identity verification. A human reading these documents separately would likely miss this tension.
- **Focus on judgment, not grunt work**: instead of reading and categorizing, the officer spends time on the decisions that actually require human expertise — should this obligation be approved? Does this conflict matter for our specific products?

**The system doesn't replace the compliance officer. It gives them superpowers.** What previously required a team of analysts and weeks of work now takes one person and seconds of compute.

---

## 2. What is AI responsible for?

The AI handles the cognitive labor that currently bottlenecks compliance teams:

### Obligation Extraction

The system scans regulatory text and identifies specific requirements using 25 domain-specialized pattern matchers (KYC, AML, suitability, sanctions, crypto custody, privacy, etc.). For novel or ambiguous language, a three-tier LLM chain (OpenRouter → Anthropic → Deterministic fallback) provides reasoning-based extraction.

### Evidence-First Citation

Every extracted obligation includes the **exact excerpt** from the regulatory text that creates the requirement. The AI does not summarize or paraphrase — it quotes. If it cannot find a citation, it explicitly flags the obligation for human review with the reason "Insufficient evidence."

### Risk Classification

The AI assigns risk levels (Low / Medium / High / Critical) based on the regulatory domain. AML and sanctions are always Critical. Privacy and data retention are Medium. The classification rules are deterministic and auditable — not hidden in an LLM prompt.

### Product and Control Mapping

Based on the regulatory domain, the AI maps obligations to affected Wealthsimple products and existing controls. For example, a KYC obligation is mapped to Invest, Trade, Crypto, Cash, and Options — and linked to the `ctrl_kyc_onboarding` control.

### Conflict Detection

Six cross-source conflict rules detect contradictions between regulators. For example:

- CSA vs. FINTRAC on KYC timing
- PIPEDA vs. FINTRAC on data retention vs. privacy minimization
- CSA suitability requirements vs. CIRO best-execution obligations

### Auto-Escalation

The AI identifies when it **should not be trusted** and flags items for human review. This is not optional — it is hard-coded:

- High or Critical risk → human review required
- Low confidence → human review required
- Missing citation → human review required
- Customer-facing changes detected → human review required
- Cross-source conflicts → never auto-resolved

---

## 3. Where must AI stop?

This is the most important design decision in the system. In regulated financial services, an AI that confidently gives wrong answers is worse than no AI at all.

### Hard Boundaries (Enforced in Code)

**The AI never approves an obligation.** Every obligation enters the system in `DRAFT` status. Only a human with the correct RBAC role can move it to `APPROVED` or `REJECTED`. The system enforces this with:

- **4-role RBAC**: Admin, Compliance Officer, Analyst, Viewer — each with explicit permissions. Viewers cannot review. Analysts cannot revert. Only admins can undo.
- **Auto-escalation**: High-risk items (AML, sanctions, KYC) are automatically flagged for human review regardless of confidence. The AI cannot override these triggers — they are `__post_init__` rules on the frozen dataclass, not configurable parameters.
- **Citation requirement**: If the AI cannot cite the specific text creating an obligation, it refuses to classify and instead surfaces the escalation reason `INSUFFICIENT_EVIDENCE`.
- **Conflict neutrality**: When two regulators contradict each other, the system presents both positions with their source citations. It **never picks a side**. This is a judgment call that requires legal expertise and institutional context that AI does not have.
- **Immutable audit trail**: Every action (creation, review, approval, rejection, revert) is logged with timestamp, role, and reason. The audit trail is append-only. This is not just good practice — it is a regulatory requirement for CIRO-registered firms.

### Why These Boundaries?

Compliance decisions carry real consequences: enforcement actions, loss of registration, client harm. The cost of a false negative (missing a real obligation) is regulatory exposure. The cost of a false positive (flagging something that isn't an obligation) is wasted analyst time. The system is calibrated to **over-flag rather than under-flag** — it is better to ask a human to review something unnecessary than to silently miss a real obligation.

---

## 4. What would break first at scale?

### The Human Review Bottleneck

At Wealthsimple's scale (10+ regulatory sources, frequent updates), the first thing to break is **human review throughput**. If the system flags 80% of obligations for review, it shifts work rather than reducing it. The mitigation is:

1. **Confidence calibration**: Tune extraction patterns and LLM prompts to increase confidence on well-understood domains, reducing the percentage that requires review.
2. **Domain-specific routing**: Route KYC obligations to the KYC specialist, AML to the AML specialist — instead of a single queue.
3. **Review SLAs**: Track time-to-review by domain and escalate when SLAs are breached.

### Keyword Brittleness

The deterministic engine uses keyword matching across 25 domains. This works well for structured regulatory text (which follows conventions) but would struggle with:

- Novel regulatory language that doesn't match existing patterns
- Regulatory text in different formats or styles
- Cross-jurisdictional expansion (US, EU regulations use different terminology)

The three-tier LLM chain already mitigates this — the deterministic engine serves as the eval baseline and safety net, while the LLM handles novel language.

### Conflict Combinatorics

Currently, 6 cross-source conflict rules cover the most important contradictions. As the system expands to more sources and jurisdictions, the number of potential conflicts grows combinatorially (N×N). The mitigation is priority-based conflict rules — only checking the conflicts that have regulatory significance, indexed by domain.

### Real-Time Ingestion

The current system analyzes text on-demand. At scale, Wealthsimple would need:

- Automated polling of the Canada Gazette, CSA notices, FINTRAC advisories
- Webhook-triggered analysis when new regulatory documents are published
- Push notifications to relevant compliance officers

The architecture supports this (the `/api/analyze-text` endpoint accepts any text), but the ingestion infrastructure layer would need to be built.

### What I Would Build in 6 Months

| Month | Deliverable                                                                                                       |
| ----- | ----------------------------------------------------------------------------------------------------------------- |
| **1** | Replace keyword matching with LLM extraction, validated against the 70-case eval harness (no accuracy regression) |
| **2** | Integrate with Wealthsimple's internal control inventory and product registry for live gap analysis               |
| **3** | Real-time regulatory feed ingestion with push alerts for new obligations                                          |
| **4** | Regulatory change diffing — when amendments are published, show what changed                                      |
| **5** | Multi-reviewer workflow with escalation chains and SLA tracking                                                   |
| **6** | Executive dashboard for board reporting and regulatory exam preparation                                           |

---

## Technical Summary

| Dimension       | Details                                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Backend**     | Python 3.10+ / FastAPI / 17 REST endpoints / gunicorn + uvicorn workers                                              |
| **Frontend**    | React 18 SPA / 6 tabs / No build step (Babel in-browser)                                                             |
| **AI**          | OpenRouter API (Claude 3.5 Sonnet) / Anthropic fallback / Deterministic safety net                                   |
| **Data**        | 10 Canadian regulatory sources / 47 sections / 25 domain patterns                                                    |
| **Persistence** | SQLite (WAL mode) / JSON LLM cache (SHA-256, TTL-based)                                                              |
| **Security**    | Token-bucket rate limiter / Configurable CORS / 4-role RBAC                                                          |
| **Testing**     | 91 pytest tests / 70 eval test cases / 6 accuracy metrics                                                            |
| **Deployment**  | Docker / Render / Live at [wealthsimple-compliance-ai.onrender.com](https://wealthsimple-compliance-ai.onrender.com) |

---

_Built with the conviction that AI should amplify human judgment, not replace it — especially where the stakes are real._
