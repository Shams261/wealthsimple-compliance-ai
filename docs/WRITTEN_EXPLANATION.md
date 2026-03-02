# Wealthsimple Compliance AI — Written Explanation

## What can the human now do that they couldn't before?

A compliance officer at a CIRO-registered dealer like Wealthsimple spends 2–4 weeks per regulatory update: reading dense legal text, extracting obligations, mapping them to products, and checking for gaps. A single miss can trigger enforcement action or loss of registration.

This system eliminates that bottleneck. A compliance officer can now paste raw regulatory text and receive, in seconds, a structured obligation map: every requirement extracted, cited with the verbatim source excerpt, risk-scored (critical/high/medium/low), mapped to affected Wealthsimple products (Invest, Trade, Crypto, Tax, Cash, Options), and linked to existing controls. Conflicts between regulators are detected automatically — for example, CSA requiring KYC _before_ recommendations while FINTRAC allows 30 days post-opening. The system doesn't replace the compliance officer — it gives them superpowers.

## What is AI responsible for?

The AI performs the cognitive heavy-lifting: scanning regulatory text across 25 domains (KYC, AML, suitability, sanctions, crypto custody, privacy, etc.), extracting obligations with evidence-first citations, assigning risk levels, mapping to products and controls, and detecting cross-source conflicts. A three-tier LLM chain (OpenRouter → Anthropic → Deterministic fallback) ensures the system always works — even without API keys. Every obligation cites the exact source text. If the AI cannot find evidence, it says so explicitly instead of guessing.

## Where must AI stop?

In regulated financial services, an AI that confidently gives wrong answers is worse than no AI at all. The AI never approves an obligation — every item enters as Draft and only a human with the correct RBAC role can move it to Approved or Rejected. High-risk obligations (AML, KYC, sanctions) require mandatory human review — hard-coded in the data model, not configurable. When confidence is low or evidence is insufficient, the system escalates instead of processing. Policy conflicts are surfaced with both source excerpts, never auto-resolved. Every action is recorded in an immutable audit log — the trail regulators require.

## What would break first at scale?

The human review bottleneck. If 80% of obligations need review, the system shifts work rather than reducing it. Mitigation: confidence calibration to reduce false escalations, domain-specific routing (KYC to KYC specialists), and review SLAs. The deterministic engine's keyword matching is effective for structured regulatory text but brittle on novel language — the LLM chain already handles this, with the deterministic engine serving as eval baseline. Cross-jurisdictional expansion multiplies conflict detection combinatorially; priority-based rules indexed by domain keep it tractable. Real-time ingestion (Canada Gazette, CSA notices) requires polling infrastructure beyond the prototype — the architecture supports it via the analyze-text endpoint.

**6 months at Wealthsimple:** Replace keyword matching with LLM extraction validated against the 70-case eval harness. Integrate with internal control inventory for live gap analysis. Build real-time regulatory feed ingestion with push alerts. Add regulatory change diffing. Scale human review with multi-reviewer workflows and SLA tracking.
