"""
Tests for backend/analyzer.py — obligation extraction, conflict detection, and citations.
"""

import pytest
from backend.analyzer import ComplianceAnalyzer, OBLIGATION_PATTERNS
from backend.models import (
    Citation, ConfidenceLevel, EscalationReason, Obligation, RiskLevel,
)
from data.regulatory_sources import REGULATORY_SOURCES, WEALTHSIMPLE_PRODUCTS, EXISTING_CONTROLS


class TestObligationPatterns:
    """Verify the integrity of the OBLIGATION_PATTERNS config."""

    def test_all_patterns_have_required_keys(self):
        required_keys = {"keywords", "risk_default", "products", "controls"}
        for domain, pattern in OBLIGATION_PATTERNS.items():
            for key in required_keys:
                assert key in pattern, f"Pattern '{domain}' missing key '{key}'"

    def test_all_products_in_patterns_exist(self):
        for domain, pattern in OBLIGATION_PATTERNS.items():
            for pid in pattern["products"]:
                assert pid in WEALTHSIMPLE_PRODUCTS, (
                    f"Pattern '{domain}' references unknown product '{pid}'"
                )

    def test_all_controls_in_patterns_exist(self):
        for domain, pattern in OBLIGATION_PATTERNS.items():
            for ctrl_id in pattern["controls"]:
                assert ctrl_id in EXISTING_CONTROLS, (
                    f"Pattern '{domain}' references unknown control '{ctrl_id}'"
                )

    def test_minimum_pattern_count(self):
        """System should have at least 20 obligation patterns."""
        assert len(OBLIGATION_PATTERNS) >= 20

    def test_risk_levels_are_valid(self):
        for domain, pattern in OBLIGATION_PATTERNS.items():
            assert isinstance(pattern["risk_default"], RiskLevel), (
                f"Pattern '{domain}' has invalid risk_default type"
            )


class TestAnalyzerExtraction:
    """Test the deterministic obligation extraction engine."""

    def test_extracts_kyc_from_text(self, analyzer, sample_kyc_text):
        obligations = analyzer._analyze_text_deterministic(sample_kyc_text)
        domains = [ob.description for ob in obligations]
        assert any("[KYC]" in d for d in domains)

    def test_extracts_aml_from_text(self, analyzer, sample_aml_text):
        obligations = analyzer._analyze_text_deterministic(sample_aml_text)
        domains = [ob.description for ob in obligations]
        assert any("[AML]" in d for d in domains)

    def test_multi_domain_extraction(self, analyzer, sample_multi_domain_text):
        obligations = analyzer._analyze_text_deterministic(sample_multi_domain_text)
        extracted_domains = set()
        for ob in obligations:
            # Parse domain from "[DOMAIN]" in description
            if "[" in ob.description and "]" in ob.description:
                domain = ob.description.split("[")[1].split("]")[0]
                extracted_domains.add(domain)
        assert "KYC" in extracted_domains
        assert "SUITABILITY" in extracted_domains
        assert "RECORD_KEEPING" in extracted_domains

    def test_no_extraction_from_irrelevant_text(self, analyzer):
        obligations = analyzer._analyze_text_deterministic(
            "The weather today is sunny with a chance of rain."
        )
        assert len(obligations) == 0

    def test_citation_extracted_for_obligations(self, analyzer, sample_kyc_text):
        obligations = analyzer._analyze_text_deterministic(sample_kyc_text)
        for ob in obligations:
            if "[KYC]" in ob.description:
                assert ob.citation is not None
                assert len(ob.citation.excerpt) > 10

    def test_products_mapped_correctly(self, analyzer, sample_kyc_text):
        obligations = analyzer._analyze_text_deterministic(sample_kyc_text)
        kyc_obligations = [ob for ob in obligations if "[KYC]" in ob.description]
        assert len(kyc_obligations) > 0
        products = kyc_obligations[0].mapped_products
        product_ids = {p["id"] for p in products}
        assert "ws_invest" in product_ids
        assert "ws_trade" in product_ids


class TestAnalyzeAllSources:
    """Test full regulatory scan across all sources."""

    def test_analyze_all_returns_obligations(self, analyzer):
        result = analyzer.analyze_all_sources()
        assert result.total_obligations > 50, (
            f"Expected 50+ obligations, got {result.total_obligations}"
        )

    def test_analyze_all_has_audit_log(self, analyzer):
        result = analyzer.analyze_all_sources()
        assert len(result.audit_log) > 0

    def test_analyze_all_has_conflicts(self, analyzer):
        result = analyzer.analyze_all_sources()
        assert len(result.conflicts) >= 4, (
            f"Expected at least 4 conflicts, got {len(result.conflicts)}"
        )

    def test_analyze_all_citation_coverage(self, analyzer):
        result = analyzer.analyze_all_sources()
        assert result.citation_coverage > 90.0, (
            f"Citation coverage too low: {result.citation_coverage:.1f}%"
        )

    def test_analyze_all_computes_summary(self, analyzer):
        result = analyzer.analyze_all_sources()
        assert "obligations" in result.summary.lower()
        assert "human review" in result.summary.lower()

    def test_analyze_single_source(self, analyzer):
        result = analyzer.analyze_single_source("CSA_31-103")
        assert result.total_obligations > 0
        assert result.source_document != ""

    def test_analyze_unknown_source_raises(self, analyzer):
        with pytest.raises(ValueError, match="Unknown source"):
            analyzer.analyze_single_source("NONEXISTENT_SOURCE")


class TestConflictDetection:
    """Test cross-regulator conflict detection."""

    def test_detects_kyc_timing_conflict(self, analyzer):
        result = analyzer.analyze_all_sources()
        conflict_descs = [c.description for c in result.conflicts]
        assert any("KYC" in d for d in conflict_descs)

    def test_detects_data_retention_vs_privacy(self, analyzer):
        result = analyzer.analyze_all_sources()
        conflict_descs = [c.description.lower() for c in result.conflicts]
        assert any("retention" in d for d in conflict_descs)

    def test_conflicts_have_citations(self, analyzer):
        result = analyzer.analyze_all_sources()
        for conflict in result.conflicts:
            # At least one side should have a citation
            assert conflict.source_a is not None or conflict.source_b is not None

    def test_conflict_escalates_obligations(self, analyzer):
        result = analyzer.analyze_all_sources()
        escalated = [
            ob for ob in result.obligations
            if EscalationReason.POLICY_CONFLICT in ob.escalation_reasons
        ]
        assert len(escalated) > 0, "No obligations escalated due to policy conflicts"


class TestReviewObligation:
    """Test the human review gate."""

    def test_approve_obligation(self, analyzer):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        reviewed = analyzer.review_obligation(ob, "reviewer@ws.com", "approve", "Looks good")
        assert reviewed.status.value == "approved"
        assert reviewed.reviewed_by == "reviewer@ws.com"

    def test_reject_obligation(self, analyzer):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        reviewed = analyzer.review_obligation(ob, "reviewer@ws.com", "reject", "Not applicable")
        assert reviewed.status.value == "rejected"

    def test_invalid_review_action_raises(self, analyzer):
        ob = Obligation(description="Test")
        with pytest.raises(ValueError, match="Unknown action"):
            analyzer.review_obligation(ob, "reviewer@ws.com", "invalid_action")


class TestConfidence:
    """Test confidence level determination."""

    def test_high_confidence_multiple_keywords(self, analyzer):
        text = "know your client kyc identity verification financial circumstances"
        conf = analyzer._determine_confidence(text, OBLIGATION_PATTERNS["KYC"]["keywords"])
        assert conf == ConfidenceLevel.HIGH

    def test_medium_confidence_single_keyword(self, analyzer):
        text = "The registrant must follow kyc rules."
        conf = analyzer._determine_confidence(text, OBLIGATION_PATTERNS["KYC"]["keywords"])
        assert conf == ConfidenceLevel.MEDIUM

    def test_low_confidence_no_keywords(self, analyzer):
        text = "The weather is nice today."
        conf = analyzer._determine_confidence(text, OBLIGATION_PATTERNS["KYC"]["keywords"])
        assert conf == ConfidenceLevel.LOW
