"""
Data models for the Regulatory Compliance Monitoring System.
All models are immutable audit-friendly dataclasses with full traceability.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ObligationStatus(Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class EscalationReason(Enum):
    HIGH_RISK = "high_risk"
    LOW_CONFIDENCE = "low_confidence"
    POLICY_CONFLICT = "policy_conflict"
    AMBIGUOUS_SOURCE = "ambiguous_source"
    CUSTOMER_FACING_CHANGE = "customer_facing_change"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Citation:
    """An exact excerpt from a regulatory source backing a claim."""
    source_document: str
    section: str
    excerpt: str  # Exact quoted text
    page_or_paragraph: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self):
        return {
            "source_document": self.source_document,
            "section": self.section,
            "excerpt": self.excerpt,
            "page_or_paragraph": self.page_or_paragraph,
            "url": self.url,
        }


@dataclass
class Obligation:
    """A single regulatory obligation extracted from source text."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    citation: Optional[Citation] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: ObligationStatus = ObligationStatus.DRAFT
    mapped_products: list = field(default_factory=list)
    mapped_controls: list = field(default_factory=list)
    escalation_reasons: list = field(default_factory=list)
    requires_human_review: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_notes: Optional[str] = None

    def __post_init__(self):
        # Auto-flag for human review
        if self.risk_level == RiskLevel.HIGH or self.risk_level == RiskLevel.CRITICAL:
            self.requires_human_review = True
            if EscalationReason.HIGH_RISK not in self.escalation_reasons:
                self.escalation_reasons.append(EscalationReason.HIGH_RISK)
        if self.confidence == ConfidenceLevel.LOW:
            self.requires_human_review = True
            if EscalationReason.LOW_CONFIDENCE not in self.escalation_reasons:
                self.escalation_reasons.append(EscalationReason.LOW_CONFIDENCE)
        if self.citation is None:
            self.requires_human_review = True
            if EscalationReason.INSUFFICIENT_EVIDENCE not in self.escalation_reasons:
                self.escalation_reasons.append(EscalationReason.INSUFFICIENT_EVIDENCE)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "citation": self.citation.to_dict() if self.citation else None,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "mapped_products": self.mapped_products,
            "mapped_controls": self.mapped_controls,
            "escalation_reasons": [r.value for r in self.escalation_reasons],
            "requires_human_review": self.requires_human_review,
            "created_at": self.created_at,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "review_notes": self.review_notes,
        }


@dataclass
class ConflictDetection:
    """Represents a detected conflict or ambiguity between two sources."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    conflict_type: str = ""  # "policy_conflict" or "ambiguity"
    source_a: Optional[Citation] = None
    source_b: Optional[Citation] = None
    description: str = ""
    resolution_status: str = "pending"  # pending, escalated, resolved
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self):
        return {
            "id": self.id,
            "conflict_type": self.conflict_type,
            "source_a": self.source_a.to_dict() if self.source_a else None,
            "source_b": self.source_b.to_dict() if self.source_b else None,
            "description": self.description,
            "resolution_status": self.resolution_status,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at,
        }


@dataclass
class AuditLogEntry:
    """Immutable audit log entry for every action in the system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=utc_now_iso)
    action: str = ""  # e.g., "obligation_created", "status_changed", "human_review"
    actor: str = ""  # "system" or username
    entity_type: str = ""  # "obligation", "conflict", "analysis"
    entity_id: str = ""
    before_state: Optional[dict] = None
    after_state: Optional[dict] = None
    notes: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "action": self.action,
            "actor": self.actor,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "notes": self.notes,
        }


@dataclass
class AnalysisResult:
    """Complete result of analyzing a regulatory document."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_document: str = ""
    analysis_timestamp: str = field(default_factory=utc_now_iso)
    obligations: list = field(default_factory=list)  # List[Obligation]
    conflicts: list = field(default_factory=list)  # List[ConflictDetection]
    audit_log: list = field(default_factory=list)  # List[AuditLogEntry]
    summary: str = ""
    total_obligations: int = 0
    auto_approved: int = 0
    needs_human_review: int = 0
    high_risk_count: int = 0
    citation_coverage: float = 0.0  # % of obligations with citations

    def compute_stats(self):
        self.total_obligations = len(self.obligations)
        self.auto_approved = sum(1 for o in self.obligations if not o.requires_human_review)
        self.needs_human_review = sum(1 for o in self.obligations if o.requires_human_review)
        self.high_risk_count = sum(
            1 for o in self.obligations
            if o.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        )
        cited = sum(1 for o in self.obligations if o.citation is not None)
        self.citation_coverage = (cited / self.total_obligations * 100) if self.total_obligations > 0 else 0.0

    def to_dict(self):
        self.compute_stats()
        return {
            "id": self.id,
            "source_document": self.source_document,
            "analysis_timestamp": self.analysis_timestamp,
            "obligations": [o.to_dict() for o in self.obligations],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "audit_log": [a.to_dict() for a in self.audit_log],
            "summary": self.summary,
            "stats": {
                "total_obligations": self.total_obligations,
                "auto_approved": self.auto_approved,
                "needs_human_review": self.needs_human_review,
                "high_risk_count": self.high_risk_count,
                "citation_coverage": round(self.citation_coverage, 1),
            },
        }
