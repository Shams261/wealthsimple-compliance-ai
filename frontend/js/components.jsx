(() => {
const { useState, useCallback } = React;
const { Icons, parseDomain, parseTitle } = window.ComplianceUI;

function useToast() {
  const [toasts, setToasts] = useState([]);
  const addToast = useCallback((msg, type = "success") => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, msg, type }]);
    setTimeout(
      () => setToasts((prev) => prev.filter((t) => t.id !== id)),
      3200,
    );
  }, []);
  return { toasts, addToast };
}

function ToastContainer({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          <div className="toast-dot" />
          {t.msg}
        </div>
      ))}
    </div>
  );
}

// ==========================================
// COMPONENTS
// ==========================================

function RiskTag({ level }) {
  return <span className={`tag tag-${level}`}>{level}</span>;
}
function StatusTag({ status }) {
  return <span className={`tag tag-${status}`}>{status}</span>;
}

function EscalationTags({ reasons }) {
  const labels = {
    high_risk: "HIGH RISK",
    low_confidence: "LOW CONFIDENCE",
    policy_conflict: "CONFLICT",
    ambiguous_source: "AMBIGUOUS",
    customer_facing_change: "CUSTOMER-FACING",
    insufficient_evidence: "NO EVIDENCE",
  };
  return (
    <div
      style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 8 }}
    >
      {reasons.map((r, i) => (
        <span key={i} className="tag tag-escalation">
          {labels[r] || r}
        </span>
      ))}
    </div>
  );
}

function CitationBlock({ citation }) {
  if (!citation)
    return (
      <div className="no-citation">
        <Icons.alertTriangle size={14} />
        Insufficient evidence — needs human review
      </div>
    );
  return (
    <div className="citation">
      <div className="citation-text">"{citation.excerpt}"</div>
      <span className="citation-source">
        {citation.section} — {citation.source_document}
      </span>
    </div>
  );
}

function ObligationCard({ ob, onApprove, onReject, onRevert, onOpen, index, canReview, canRevert }) {
  const domain = parseDomain(ob.description);
  const title = parseTitle(ob.description);
  return (
    <div
      className="card card-interactive fade-in"
      style={{ animationDelay: `${(index || 0) * 0.04}s` }}
      onClick={() => onOpen?.(ob)}
    >
      <div className="card-header">
        <div style={{ flex: 1, minWidth: 0 }}>
          {domain && <div className="card-domain">{domain}</div>}
          <div className="card-title">{title}</div>
          <EscalationTags reasons={ob.escalation_reasons} />
        </div>
        <div className="card-tags">
          <RiskTag level={ob.risk_level} />
          <StatusTag status={ob.status} />
        </div>
      </div>
      <CitationBlock citation={ob.citation} />
      <div className="card-footer">
        <div>
          <div className="pill-label">Products</div>
          <div className="pill-group">
            {ob.mapped_products.map((p, i) => (
              <span key={i} className="pill">
                {p.name.replace("Wealthsimple ", "")}
              </span>
            ))}
          </div>
          {ob.mapped_controls.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <div className="pill-label">Controls</div>
              <div className="pill-group">
                {ob.mapped_controls.map((c, i) => (
                  <span key={i} className="pill pill-green">
                    {c.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        {ob.requires_human_review && ob.status === "draft" && canReview !== false && (
          <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
            <button
              className="btn btn-sm btn-approve"
              onClick={(e) => {
                e.stopPropagation();
                onApprove(ob.id);
              }}
            >
              <Icons.check size={13} /> Approve
            </button>
            <button
              className="btn btn-sm btn-reject"
              onClick={(e) => {
                e.stopPropagation();
                onReject(ob.id);
              }}
            >
              <Icons.x size={13} /> Reject
            </button>
          </div>
        )}
        {ob.requires_human_review && ob.status === "draft" && canReview === false && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 12,
              color: "var(--text-muted)",
              fontWeight: 500,
              fontStyle: "italic",
            }}
          >
            <Icons.shield size={14} />
            Requires compliance_officer or admin role
          </div>
        )}
        {ob.status === "approved" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 12,
                color: "var(--green)",
                fontWeight: 600,
              }}
            >
              <Icons.checkCircle size={14} />
              Approved by {ob.reviewed_by}
            </div>
            {canRevert && onRevert && (
              <button
                className="btn btn-sm"
                style={{ fontSize: 11, padding: "3px 8px", opacity: 0.8 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onRevert(ob.id);
                }}
                title="Revert this review (admin only)"
              >
                ↩ Undo
              </button>
            )}
          </div>
        )}
        {ob.status === "rejected" && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 12,
                color: "var(--red)",
                fontWeight: 600,
              }}
            >
              <Icons.x size={14} />
              Rejected
            </div>
            {canRevert && onRevert && (
              <button
                className="btn btn-sm"
                style={{ fontSize: 11, padding: "3px 8px", opacity: 0.8 }}
                onClick={(e) => {
                  e.stopPropagation();
                  onRevert(ob.id);
                }}
                title="Revert this review (admin only)"
              >
                ↩ Undo
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function SkeletonCards({ count }) {
  return Array.from({ length: count }).map((_, i) => (
    <div
      key={i}
      className="skeleton skeleton-card"
      style={{ animationDelay: `${i * 0.1}s` }}
    />
  ));
}

function EmptyState({ icon, title, message }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}

window.ComplianceUI.useToast = useToast;
window.ComplianceUI.ToastContainer = ToastContainer;
window.ComplianceUI.RiskTag = RiskTag;
window.ComplianceUI.StatusTag = StatusTag;
window.ComplianceUI.EscalationTags = EscalationTags;
window.ComplianceUI.CitationBlock = CitationBlock;
window.ComplianceUI.ObligationCard = ObligationCard;
window.ComplianceUI.SkeletonCards = SkeletonCards;
window.ComplianceUI.EmptyState = EmptyState;
})();
