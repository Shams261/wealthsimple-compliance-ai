"""
Tests for backend/models.py — data model integrity, serialization, and auto-flagging.
"""

import pytest
from backend.models import (
    AnalysisResult, Citation, ConfidenceLevel, ConflictDetection,
    EscalationReason, Obligation, ObligationStatus, RiskLevel,
)


class TestCitation:
    def test_citation_creation(self):
        c = Citation(
            source_document="NI 31-103",
            section="13.2",
            excerpt="Must verify identity",
        )
        assert c.source_document == "NI 31-103"
        assert c.excerpt == "Must verify identity"

    def test_citation_to_dict(self):
        c = Citation(
            source_document="NI 31-103",
            section="13.2",
            excerpt="Test excerpt",
            url="https://example.com",
        )
        d = c.to_dict()
        assert d["source_document"] == "NI 31-103"
        assert d["url"] == "https://example.com"
        assert "excerpt" in d

    def test_citation_is_frozen(self):
        c = Citation(source_document="X", section="Y", excerpt="Z")
        with pytest.raises(AttributeError):
            c.source_document = "changed"


class TestObligation:
    def test_high_risk_auto_flags_human_review(self):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        assert ob.requires_human_review is True
        assert EscalationReason.HIGH_RISK in ob.escalation_reasons

    def test_critical_risk_auto_flags_human_review(self):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.CRITICAL,
            confidence=ConfidenceLevel.HIGH,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        assert ob.requires_human_review is True

    def test_low_confidence_auto_flags_human_review(self):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.LOW,
            confidence=ConfidenceLevel.LOW,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        assert ob.requires_human_review is True
        assert EscalationReason.LOW_CONFIDENCE in ob.escalation_reasons

    def test_missing_citation_flags_insufficient_evidence(self):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.LOW,
            confidence=ConfidenceLevel.HIGH,
            citation=None,
        )
        assert ob.requires_human_review is True
        assert EscalationReason.INSUFFICIENT_EVIDENCE in ob.escalation_reasons

    def test_low_risk_high_confidence_with_citation_no_review(self):
        ob = Obligation(
            description="Test",
            risk_level=RiskLevel.LOW,
            confidence=ConfidenceLevel.HIGH,
            citation=Citation(source_document="X", section="Y", excerpt="Z"),
        )
        assert ob.requires_human_review is False

    def test_obligation_to_dict(self):
        ob = Obligation(
            description="[KYC] Test obligation",
            risk_level=RiskLevel.HIGH,
            confidence=ConfidenceLevel.MEDIUM,
            citation=Citation(source_document="NI 31-103", section="13.2", excerpt="Test"),
        )
        d = ob.to_dict()
        assert d["risk_level"] == "high"
        assert d["confidence"] == "medium"
        assert d["status"] == "draft"
        assert "id" in d
        assert isinstance(d["escalation_reasons"], list)

    def test_obligation_unique_ids(self):
        ob1 = Obligation(description="A")
        ob2 = Obligation(description="B")
        assert ob1.id != ob2.id


class TestAnalysisResult:
    def test_compute_stats(self):
        obs = [
            Obligation(
                description="Low risk",
                risk_level=RiskLevel.LOW,
                confidence=ConfidenceLevel.HIGH,
                citation=Citation(source_document="X", section="Y", excerpt="Z"),
            ),
            Obligation(
                description="High risk",
                risk_level=RiskLevel.HIGH,
                confidence=ConfidenceLevel.HIGH,
                citation=Citation(source_document="X", section="Y", excerpt="Z"),
            ),
            Obligation(
                description="No citation",
                risk_level=RiskLevel.LOW,
                confidence=ConfidenceLevel.HIGH,
                citation=None,
            ),
        ]
        result = AnalysisResult(
            source_document="Test",
            obligations=obs,
            conflicts=[],
            audit_log=[],
        )
        result.compute_stats()
        assert result.total_obligations == 3
        assert result.high_risk_count == 1
        assert result.needs_human_review == 2  # high risk + no citation
        assert result.citation_coverage == pytest.approx(66.7, abs=0.1)

    def test_to_dict_structure(self):
        result = AnalysisResult(
            source_document="Test",
            obligations=[],
            conflicts=[],
            audit_log=[],
        )
        d = result.to_dict()
        assert "stats" in d
        assert "obligations" in d
        assert "conflicts" in d
        assert "audit_log" in d
        assert d["stats"]["total_obligations"] == 0
