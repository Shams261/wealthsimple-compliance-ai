"""
Core Regulatory Compliance Analyzer Engine.

This is the heart of the system: it reads regulatory text, extracts obligations,
maps them to Wealthsimple products/controls, detects conflicts, and enforces
evidence-first citation rules.

Designed to work with any LLM backend (Claude, GPT-4, etc.) via a pluggable
interface. Ships with a deterministic rule-based engine for the demo + eval harness,
and an LLM-powered engine for production use.
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Optional
from urllib import request

from backend import llm_cache
from backend.models import (
    AnalysisResult,
    AuditLogEntry,
    Citation,
    ConfidenceLevel,
    ConflictDetection,
    EscalationReason,
    Obligation,
    ObligationStatus,
    RiskLevel,
)
from data.regulatory_sources import (
    EXISTING_CONTROLS,
    REGULATORY_SOURCES,
    WEALTHSIMPLE_PRODUCTS,
)


# -------------------------------------------------------------------
# KEYWORD → DOMAIN MAPPINGS (for deterministic obligation extraction)
# -------------------------------------------------------------------

OBLIGATION_PATTERNS = {
    "KYC": {
        "keywords": ["know your client", "kyc", "client identification", "verify the identity", "identity verification", "account opening", "financial circumstances"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
        "controls": ["ctrl_kyc_onboarding"],
    },
    "suitability": {
        "keywords": ["suitability", "suitable for the client", "suitable", "investment needs", "risk tolerance", "investment objectives"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_options"],
        "controls": ["ctrl_suitability_engine"],
    },
    "AML": {
        "keywords": ["money laundering", "terrorist financing", "suspicious transaction report", "suspicious transaction", "suspicious activity"],
        "risk_default": RiskLevel.CRITICAL,
        "products": ["ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_aml_screening"],
    },
    "KYP": {
        "keywords": ["know your product", "kyp", "understand the securities", "features, risks", "reasonable basis"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_options"],
        "controls": ["ctrl_suitability_engine"],
    },
    "best_execution": {
        "keywords": ["best execution", "most advantageous execution", "execution terms"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_trade", "ws_options"],
        "controls": ["ctrl_best_execution"],
    },
    "complaint_handling": {
        "keywords": ["complaint", "complaints from clients", "acknowledged in writing"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_complaint_system"],
    },
    "EFT_reporting": {
        "keywords": ["electronic funds transfer", "international", "$10,000", "EFT"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_cash", "ws_crypto"],
        "controls": ["ctrl_aml_screening"],
    },
    "PEP_screening": {
        "keywords": ["politically exposed", "PEP", "head of an international organization", "family member"],
        "risk_default": RiskLevel.CRITICAL,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_aml_screening"],
    },
    "investment_restrictions": {
        "keywords": ["investment restrictions", "10 percent", "net asset value", "concentration"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest"],
        "controls": ["ctrl_suitability_engine"],
    },
    "privacy": {
        "keywords": ["consent", "privacy", "PIPEDA", "privacy practices"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
        "controls": ["ctrl_privacy_framework"],
    },
    "breach_notification": {
        "keywords": ["breach of security", "real risk of significant harm", "breach of security safeguards", "security breach"],
        "risk_default": RiskLevel.CRITICAL,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
        "controls": ["ctrl_privacy_framework"],
    },
    "data_retention": {
        "keywords": ["retention", "destruction", "no longer required", "erased", "anonymous"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
        "controls": ["ctrl_privacy_framework"],
    },
    "tax_reporting": {
        "keywords": ["T5", "TFSA", "information return", "RC243", "tax"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_tax"],
        "controls": ["ctrl_tax_reporting"],
    },
    "relationship_disclosure": {
        "keywords": ["relationship disclosure", "fees and charges", "types of products", "risk disclosure", "disclosure of all fees", "fee and cost disclosure"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_options"],
        "controls": [],
    },
    "compliance_framework": {
        "keywords": ["compliance risk management", "policies and procedures", "controls and supervision", "compliance system"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
        "controls": ["ctrl_compliance_testing"],
    },
    "compliance_testing": {
        "keywords": ["compliance testing", "testing results", "deficiencies", "remediated"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_compliance_testing"],
    },
    "fundamental_changes": {
        "keywords": ["fundamental investment objectives", "written consent", "majority of the securityholders", "60 days"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest"],
        "controls": [],
    },
    "risk_assessment": {
        "keywords": ["risk assessment", "assess and document the risk", "business relationships"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_kyc_onboarding", "ctrl_aml_screening"],
    },
    "record_keeping": {
        "keywords": ["books and records", "record keeping", "maintain records", "7 years", "retention period", "recordkeeping"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_record_keeping"],
    },
    "capital_requirements": {
        "keywords": ["capital requirements", "capital adequacy", "minimum capital", "risk-adjusted capital", "working capital"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_capital_monitoring"],
    },
    "outsourcing": {
        "keywords": ["outsourcing", "third-party", "material outsourcing", "service provider", "outsource"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
        "controls": ["ctrl_vendor_risk"],
    },
    "margin_requirements": {
        "keywords": ["margin", "margin requirements", "leverage", "margin call", "margin account"],
        "risk_default": RiskLevel.HIGH,
        "products": ["ws_trade", "ws_options"],
        "controls": ["ctrl_margin_system"],
    },
    "crypto_custody": {
        "keywords": ["crypto custody", "custody of crypto", "custodial", "cold storage", "wallet security", "safekeeping of crypto"],
        "risk_default": RiskLevel.CRITICAL,
        "products": ["ws_crypto"],
        "controls": ["ctrl_crypto_custody"],
    },
    "sanctions": {
        "keywords": ["sanctions", "sanctioned", "terrorist property", "designated person", "frozen", "listed entity"],
        "risk_default": RiskLevel.CRITICAL,
        "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
        "controls": ["ctrl_sanctions_screening"],
    },
    "client_reporting": {
        "keywords": ["account statement", "performance report", "quarterly report", "annual report", "client statement"],
        "risk_default": RiskLevel.MEDIUM,
        "products": ["ws_invest", "ws_trade", "ws_options"],
        "controls": ["ctrl_complaint_system"],
    },
}


class ComplianceAnalyzer:
    """
    Deterministic compliance analyzer that extracts obligations from
    regulatory text with evidence-first citations.

    In production, this would be augmented/replaced by an LLM that reads
    the full regulatory text and reasons about obligations. The deterministic
    engine ensures we always have a baseline + can run evals without API costs.
    """

    def __init__(self):
        self.sources = {s["id"]: s for s in REGULATORY_SOURCES}
        self.products = WEALTHSIMPLE_PRODUCTS
        self.controls = EXISTING_CONTROLS
        self.audit_log = []

    def _log(self, action: str, entity_type: str, entity_id: str, actor: str = "system",
             before_state: dict = None, after_state: dict = None, notes: str = None):
        entry = AuditLogEntry(
            action=action,
            actor=actor,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            notes=notes,
        )
        self.audit_log.append(entry)
        return entry

    def _extract_key_sentence(self, text: str, keywords: list) -> Optional[str]:
        """Extract the most relevant sentence containing the keyword."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            lower = sentence.lower()
            for kw in keywords:
                if kw.lower() in lower:
                    return sentence.strip()
        return None

    def _determine_confidence(self, text: str, keywords: list) -> ConfidenceLevel:
        """Determine confidence based on keyword match strength."""
        lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in lower)
        if matches >= 3:
            return ConfidenceLevel.HIGH
        elif matches >= 1:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _detect_customer_facing_impact(self, obligation_desc: str) -> bool:
        """Check if an obligation involves customer-facing changes."""
        customer_keywords = [
            "client", "customer", "notify", "disclosure", "consent",
            "securityholder", "recipient", "complaint", "suitability",
        ]
        lower = obligation_desc.lower()
        return any(kw in lower for kw in customer_keywords)

    def analyze_section(self, source_id: str, section: dict) -> list:
        """Analyze a single regulatory section and extract obligations."""
        obligations = []
        text = section["text"]
        source = self.sources[source_id]

        for domain, pattern in OBLIGATION_PATTERNS.items():
            lower_text = text.lower()
            matched_keywords = [kw for kw in pattern["keywords"] if kw.lower() in lower_text]

            if not matched_keywords:
                continue

            # EVIDENCE-FIRST: Extract exact citation
            excerpt = self._extract_key_sentence(text, matched_keywords)
            if excerpt:
                citation = Citation(
                    source_document=source["title"],
                    section=f"{section['section_id']} — {section['section_title']}",
                    excerpt=excerpt,
                    url=source.get("url"),
                )
            else:
                citation = None  # Will trigger "Insufficient evidence → needs human review"

            confidence = self._determine_confidence(text, pattern["keywords"])

            # Map to products
            mapped_products = [
                {"id": pid, "name": self.products[pid]["name"]}
                for pid in pattern["products"]
                if pid in self.products
            ]

            # Map to controls
            mapped_controls = []
            for ctrl_id in pattern["controls"]:
                if ctrl_id in self.controls:
                    ctrl = self.controls[ctrl_id]
                    mapped_controls.append({
                        "id": ctrl_id,
                        "name": ctrl["name"],
                        "description": ctrl["description"],
                    })

            # Build obligation description
            description = f"[{domain.upper()}] Obligation from {source['issuer']}: {section['section_title']}"

            obligation = Obligation(
                description=description,
                citation=citation,
                risk_level=pattern["risk_default"],
                confidence=confidence,
                mapped_products=mapped_products,
                mapped_controls=mapped_controls,
            )

            # Check for customer-facing impact
            if self._detect_customer_facing_impact(text):
                if EscalationReason.CUSTOMER_FACING_CHANGE not in obligation.escalation_reasons:
                    obligation.escalation_reasons.append(EscalationReason.CUSTOMER_FACING_CHANGE)
                    obligation.requires_human_review = True

            obligations.append(obligation)

            # Audit log
            self._log(
                action="obligation_extracted",
                entity_type="obligation",
                entity_id=obligation.id,
                notes=f"Domain: {domain}, Confidence: {confidence.value}, "
                      f"Citation: {'yes' if citation else 'MISSING'}"
            )

        return obligations

    def detect_conflicts(self, obligations: list) -> list:
        """
        Detect conflicts between obligations from different sources.
        E.g., different retention periods, conflicting requirements.
        """
        conflicts = []

        # Known conflict patterns to check
        conflict_rules = [
            {
                "name": "KYC timing conflict",
                "domain_a": "KYC",
                "domain_b": "KYC",
                "check": lambda a, b: (
                    a.citation and b.citation and
                    a.citation.source_document != b.citation.source_document and
                    ("before" in (a.citation.excerpt or "").lower() or
                     "within 30 days" in (b.citation.excerpt or "").lower())
                ),
                "description": "CSA requires KYC before making recommendations, while FINTRAC allows up to 30 days after account opening for identity verification. Timing requirements may create operational tension.",
            },
            {
                "name": "Data retention vs. privacy conflict",
                "domain_a": "data_retention",
                "domain_b": "complaint_handling",
                "check": lambda a, b: True,
                "description": "PIPEDA requires disposal of data no longer needed, while CIRO requires retaining complaint records for minimum 7 years. Retention policies must reconcile these competing obligations.",
            },
            {
                "name": "Suitability vs. best execution conflict",
                "domain_a": "suitability",
                "domain_b": "best_execution",
                "check": lambda a, b: (
                    a.citation and b.citation and
                    a.citation.source_document != b.citation.source_document
                ),
                "description": "CSA suitability rules require recommending securities that match client risk profiles, while CIRO best execution rules require obtaining the most advantageous price. A low-cost unsuitable security could satisfy best execution but violate suitability, creating operational tension.",
            },
            {
                "name": "Privacy consent vs. AML monitoring conflict",
                "domain_a": "privacy",
                "domain_b": "AML",
                "check": lambda a, b: (
                    a.citation and b.citation and
                    a.citation.source_document != b.citation.source_document
                ),
                "description": "PIPEDA requires meaningful consent before collecting personal information, while FINTRAC's AML regime mandates ongoing transaction monitoring without client opt-out. Consent requirements may conflict with mandatory surveillance obligations.",
            },
            {
                "name": "Data retention vs. breach notification conflict",
                "domain_a": "data_retention",
                "domain_b": "breach_notification",
                "check": lambda a, b: (
                    a.citation and b.citation and
                    a.citation.source_document != b.citation.source_document
                ),
                "description": "PIPEDA requires destroying personal information no longer needed, but breach notification obligations require retaining breach records and evidence for investigation. Early disposal could impair breach response and regulatory reporting.",
            },
            {
                "name": "Investment restrictions vs. fundamental changes conflict",
                "domain_a": "investment_restrictions",
                "domain_b": "fundamental_changes",
                "expects_same_document": True,
                "check": lambda a, b: (
                    a.citation and b.citation and
                    a.citation.source_document == b.citation.source_document
                ),
                "description": "NI 81-102 imposes strict 10% concentration limits on investment funds, while also requiring securityholder consent for fundamental changes. Rebalancing to comply with concentration limits could trigger the fundamental change approval process, creating a compliance deadlock.",
            },
        ]

        # Build domain index
        domain_index = {}
        for ob in obligations:
            for domain in OBLIGATION_PATTERNS:
                if f"[{domain.upper()}]" in ob.description:
                    domain_index.setdefault(domain, []).append(ob)

        # Track seen conflict descriptions to prevent duplicates
        seen_conflicts = set()

        for rule in conflict_rules:
            obs_a = domain_index.get(rule["domain_a"], [])
            obs_b = domain_index.get(rule["domain_b"], [])
            expects_same_doc = rule.get("expects_same_document", False)

            for a in obs_a:
                for b in obs_b:
                    if a.id == b.id:
                        continue
                    # Skip same-document pairs UNLESS the rule explicitly
                    # checks for intra-document conflicts (e.g. NI 81-102
                    # investment_restrictions vs. fundamental_changes).
                    if not expects_same_doc:
                        if (a.citation and b.citation and
                                a.citation.source_document == b.citation.source_document):
                            continue

                    try:
                        if rule["check"](a, b):
                            # Deduplicate: one conflict per rule description
                            dedup_key = rule["description"]
                            if dedup_key in seen_conflicts:
                                continue
                            seen_conflicts.add(dedup_key)

                            conflict = ConflictDetection(
                                conflict_type="policy_conflict",
                                source_a=a.citation,
                                source_b=b.citation,
                                description=rule["description"],
                            )
                            conflicts.append(conflict)

                            self._log(
                                action="conflict_detected",
                                entity_type="conflict",
                                entity_id=conflict.id,
                                notes=f"Between {a.id} and {b.id}: {rule['name']}",
                            )
                    except Exception as exc:
                        self._log(
                            action="conflict_check_error",
                            entity_type="conflict",
                            entity_id="error",
                            notes=f"Rule '{rule['name']}' failed for {a.id} vs {b.id}: {exc}",
                        )

        return conflicts

    def analyze_all_sources(self) -> AnalysisResult:
        """Run full analysis across all regulatory sources."""
        self.audit_log = []
        all_obligations = []

        self._log(
            action="analysis_started",
            entity_type="analysis",
            entity_id="full_scan",
            notes=f"Analyzing {len(self.sources)} regulatory sources",
        )

        for source_id, source in self.sources.items():
            for section in source["sections"]:
                obligations = self.analyze_section(source_id, section)
                all_obligations.extend(obligations)

        # Detect conflicts
        conflicts = self.detect_conflicts(all_obligations)

        # Mark conflict-related obligations for escalation (both sides)
        for conflict in conflicts:
            for ob in all_obligations:
                if ob.citation and (
                    (conflict.source_a and ob.citation.excerpt == conflict.source_a.excerpt) or
                    (conflict.source_b and ob.citation.excerpt == conflict.source_b.excerpt)
                ):
                    if EscalationReason.POLICY_CONFLICT not in ob.escalation_reasons:
                        ob.escalation_reasons.append(EscalationReason.POLICY_CONFLICT)
                        ob.requires_human_review = True

        result = AnalysisResult(
            source_document="Full Regulatory Scan",
            obligations=all_obligations,
            conflicts=conflicts,
            audit_log=self.audit_log,
        )
        result.compute_stats()

        result.summary = (
            f"Analyzed {len(self.sources)} regulatory sources across "
            f"{sum(len(s['sections']) for s in self.sources.values())} sections. "
            f"Extracted {result.total_obligations} obligations. "
            f"{result.needs_human_review} require human review. "
            f"{result.high_risk_count} are high/critical risk. "
            f"Citation coverage: {result.citation_coverage:.1f}%. "
            f"Detected {len(conflicts)} policy conflicts."
        )

        self._log(
            action="analysis_completed",
            entity_type="analysis",
            entity_id="full_scan",
            notes=result.summary,
        )

        return result

    def analyze_single_source(self, source_id: str) -> AnalysisResult:
        """Analyze a single regulatory source."""
        self.audit_log = []

        if source_id not in self.sources:
            raise ValueError(f"Unknown source: {source_id}")

        source = self.sources[source_id]
        all_obligations = []

        for section in source["sections"]:
            obligations = self.analyze_section(source_id, section)
            all_obligations.extend(obligations)

        result = AnalysisResult(
            source_document=source["title"],
            obligations=all_obligations,
            conflicts=[],
            audit_log=self.audit_log,
        )
        result.compute_stats()
        return result

    def review_obligation(self, obligation: Obligation, reviewer: str,
                          action: str, notes: str = "") -> Obligation:
        """
        Human review gate: approve or reject an obligation.
        This is the critical human-in-the-loop step.
        """
        before_state = {"status": obligation.status.value}

        if action == "approve":
            obligation.status = ObligationStatus.APPROVED
        elif action == "reject":
            obligation.status = ObligationStatus.REJECTED
        elif action == "review":
            obligation.status = ObligationStatus.REVIEWED
        else:
            raise ValueError(f"Unknown action: {action}")

        obligation.reviewed_by = reviewer
        obligation.reviewed_at = datetime.now(timezone.utc).isoformat()
        obligation.review_notes = notes

        self._log(
            action=f"obligation_{action}d",
            entity_type="obligation",
            entity_id=obligation.id,
            actor=reviewer,
            before_state=before_state,
            after_state={"status": obligation.status.value},
            notes=notes,
        )

        return obligation

    def analyze_with_llm(self, text: str) -> list:
        """
        Use OpenRouter or Anthropic Claude to extract obligations from free-form
        regulatory text. Falls back to deterministic engine if keys are unavailable
        or LLM calls fail.
        """
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        cache_ttl_days = int(os.environ.get("LLM_CACHE_TTL_DAYS", "30"))

        prompt = f"""You are a Canadian financial regulatory compliance expert. Analyze the following regulatory text and extract all compliance obligations that would apply to Wealthsimple, a fintech company offering these products: Invest (robo-advisor), Trade (self-directed), Crypto, Tax, Cash (banking), and Options.

For each obligation found, respond with a JSON array. Each item must have:
- "description": A clear description of the obligation
- "citation_excerpt": The exact sentence from the text that creates this obligation (quote verbatim). If no clear sentence, use null.
- "risk_level": One of "critical", "high", "medium", "low"
- "confidence": One of "high", "medium", "low"
- "domain": The regulatory domain (e.g., "KYC", "AML", "suitability", "privacy", "breach_notification", "data_retention", "tax_reporting", "complaint_handling", "best_execution", "compliance_framework")
- "affected_products": Array of affected product IDs from ["ws_invest", "ws_trade", "ws_crypto", "ws_tax", "ws_cash", "ws_options"]
- "requires_human_review": true/false — true if risk is high/critical, confidence is low, or evidence is insufficient
- "escalation_reasons": Array of reasons like "high_risk", "low_confidence", "customer_facing_change", "insufficient_evidence"

If you cannot find clear evidence for an obligation, set citation_excerpt to null and add "insufficient_evidence" to escalation_reasons.

IMPORTANT: Return ONLY a valid JSON array, no markdown, no explanation.

Regulatory text:
{text}"""

        if openrouter_key:
            try:
                model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
                cache_key = llm_cache.make_key(
                    text=text,
                    provider="openrouter",
                    model=model,
                    prompt_version="v1",
                )
                cached_payload = llm_cache.get(cache_key, ttl_days=cache_ttl_days)
                if cached_payload is not None:
                    self._log(
                        action="llm_cache_hit",
                        entity_type="analysis",
                        entity_id="llm_analysis",
                        notes=f"Serving cached LLM response (provider=openrouter, model={model})",
                    )
                    return self._build_obligations_from_llm_payload(
                        parsed=cached_payload,
                        engine_label=f"OpenRouter ({model}) [cache]",
                    )

                payload = {
                    "model": model,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": prompt}],
                }

                req = request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "http://localhost:8000"),
                        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "Wealthsimple Compliance AI"),
                    },
                    method="POST",
                )

                llm_timeout = int(os.environ.get("LLM_TIMEOUT_SECONDS", "60"))
                with request.urlopen(req, timeout=llm_timeout) as response:
                    raw_response = json.loads(response.read().decode("utf-8"))

                raw_text = (
                    raw_response.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )

                parsed = self._parse_llm_output(raw_text)
                llm_cache.set(cache_key, parsed)
                return self._build_obligations_from_llm_payload(
                    parsed=parsed,
                    engine_label=f"OpenRouter ({model})",
                )

            except Exception as e:
                self._log(
                    action="llm_analysis_error",
                    entity_type="analysis",
                    entity_id="llm_analysis",
                    notes=f"OpenRouter analysis failed: {str(e)}",
                )

        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)

                model = "claude-sonnet-4-6"
                cache_key = llm_cache.make_key(
                    text=text,
                    provider="anthropic",
                    model=model,
                    prompt_version="v1",
                )
                cached_payload = llm_cache.get(cache_key, ttl_days=cache_ttl_days)
                if cached_payload is not None:
                    self._log(
                        action="llm_cache_hit",
                        entity_type="analysis",
                        entity_id="llm_analysis",
                        notes="Serving cached LLM response (provider=anthropic, model=claude-sonnet-4-6)",
                    )
                    return self._build_obligations_from_llm_payload(
                        parsed=cached_payload,
                        engine_label="Claude LLM [cache]",
                    )

                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )

                raw_text = response.content[0].text.strip()
                parsed = self._parse_llm_output(raw_text)
                llm_cache.set(cache_key, parsed)
                return self._build_obligations_from_llm_payload(
                    parsed=parsed,
                    engine_label="Claude LLM",
                )

            except Exception as e:
                self._log(
                    action="llm_analysis_error",
                    entity_type="analysis",
                    entity_id="llm_analysis",
                    notes=f"Anthropic analysis failed: {str(e)}",
                )

        self._log(
            action="llm_fallback",
            entity_type="analysis",
            entity_id="llm_analysis",
            notes="No working LLM key configured (OPENROUTER_API_KEY or ANTHROPIC_API_KEY) — falling back to deterministic engine",
        )
        return self._analyze_text_deterministic(text)

    def _parse_llm_output(self, raw_text: str):
        """Parse LLM JSON output with robust error handling."""
        if not raw_text or not raw_text.strip():
            self._log(
                action="llm_parse_error",
                entity_type="analysis",
                entity_id="llm_analysis",
                notes="LLM returned empty response",
            )
            return []

        # Strip markdown code fences
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            self._log(
                action="llm_parse_error",
                entity_type="analysis",
                entity_id="llm_analysis",
                notes=f"LLM returned invalid JSON: {e}. First 200 chars: {raw_text[:200]}",
            )
            return []

        if isinstance(parsed, dict):
            parsed = parsed.get("obligations", parsed.get("results", []))
        if not isinstance(parsed, list):
            self._log(
                action="llm_parse_error",
                entity_type="analysis",
                entity_id="llm_analysis",
                notes=f"LLM returned unexpected type: {type(parsed).__name__}",
            )
            return []
        return parsed

    def _build_obligations_from_llm_payload(self, parsed, engine_label: str) -> list:
        obligations = []
        domain_lookup = {domain.lower(): domain for domain in OBLIGATION_PATTERNS.keys()}

        for item in parsed:
            citation = None
            if item.get("citation_excerpt"):
                citation = Citation(
                    source_document="User-provided regulatory text",
                    section="LLM Analysis",
                    excerpt=item["citation_excerpt"],
                )

            risk_map = {"critical": RiskLevel.CRITICAL, "high": RiskLevel.HIGH, "medium": RiskLevel.MEDIUM, "low": RiskLevel.LOW}
            conf_map = {"high": ConfidenceLevel.HIGH, "medium": ConfidenceLevel.MEDIUM, "low": ConfidenceLevel.LOW}

            domain = item.get("domain", "unknown").upper()
            normalized_domain_key = domain_lookup.get(str(item.get("domain", "")).lower())
            pattern = OBLIGATION_PATTERNS.get(normalized_domain_key) if normalized_domain_key else None

            mapped_products = []
            allowed_products = set(pattern["products"]) if pattern else None
            for pid in item.get("affected_products", []) or []:
                if pid in self.products and (allowed_products is None or pid in allowed_products):
                    mapped_products.append({"id": pid, "name": self.products[pid]["name"]})

            if not mapped_products and pattern:
                mapped_products = [
                    {"id": pid, "name": self.products[pid]["name"]}
                    for pid in pattern["products"]
                    if pid in self.products
                ]

            mapped_controls = []
            if pattern:
                for ctrl_id in pattern.get("controls", []):
                    if ctrl_id in self.controls:
                        ctrl = self.controls[ctrl_id]
                        mapped_controls.append({"id": ctrl_id, "name": ctrl["name"], "description": ctrl["description"]})

            escalation_reasons = []
            for reason in item.get("escalation_reasons", []) or []:
                try:
                    escalation_reasons.append(EscalationReason(reason))
                except ValueError:
                    continue

            obligation = Obligation(
                description=f"[{domain}] {item.get('description', 'Obligation extracted by LLM')}",
                citation=citation,
                risk_level=risk_map.get(item.get("risk_level", "medium"), RiskLevel.MEDIUM),
                confidence=conf_map.get(item.get("confidence", "medium"), ConfidenceLevel.MEDIUM),
                mapped_products=mapped_products,
                mapped_controls=mapped_controls,
                escalation_reasons=escalation_reasons,
            )

            if item.get("requires_human_review") is True:
                obligation.requires_human_review = True

            obligations.append(obligation)
            self._log(
                action="llm_obligation_extracted",
                entity_type="obligation",
                entity_id=obligation.id,
                notes=f"Domain: {domain}, Risk: {item.get('risk_level')}, "
                      f"Citation: {'yes' if citation else 'MISSING'}, Engine: {engine_label}",
            )

        self._log(
            action="llm_analysis_completed",
            entity_type="analysis",
            entity_id="llm_analysis",
            notes=f"LLM extracted {len(obligations)} obligations from user-provided text using {engine_label}",
        )
        return obligations

    def _analyze_text_deterministic(self, text: str) -> list:
        """Run the deterministic keyword engine on arbitrary text."""
        obligations = []
        for domain, pattern in OBLIGATION_PATTERNS.items():
            lower_text = text.lower()
            matched_keywords = [kw for kw in pattern["keywords"] if kw.lower() in lower_text]
            if not matched_keywords:
                continue

            excerpt = self._extract_key_sentence(text, matched_keywords)
            citation = Citation(
                source_document="User-provided regulatory text",
                section="Deterministic Analysis",
                excerpt=excerpt,
            ) if excerpt else None

            confidence = self._determine_confidence(text, pattern["keywords"])
            mapped_products = [
                {"id": pid, "name": self.products[pid]["name"]}
                for pid in pattern["products"] if pid in self.products
            ]
            mapped_controls = []
            for ctrl_id in pattern["controls"]:
                if ctrl_id in self.controls:
                    ctrl = self.controls[ctrl_id]
                    mapped_controls.append({"id": ctrl_id, "name": ctrl["name"], "description": ctrl["description"]})

            obligation = Obligation(
                description=f"[{domain.upper()}] Obligation detected from pasted text",
                citation=citation,
                risk_level=pattern["risk_default"],
                confidence=confidence,
                mapped_products=mapped_products,
                mapped_controls=mapped_controls,
            )
            if self._detect_customer_facing_impact(text):
                if EscalationReason.CUSTOMER_FACING_CHANGE not in obligation.escalation_reasons:
                    obligation.escalation_reasons.append(EscalationReason.CUSTOMER_FACING_CHANGE)
                    obligation.requires_human_review = True

            obligations.append(obligation)
            self._log(
                action="obligation_extracted",
                entity_type="obligation",
                entity_id=obligation.id,
                notes=f"Domain: {domain}, Confidence: {confidence.value}, Engine: deterministic",
            )

        return obligations
