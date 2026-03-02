(() => {
  const { useState, useEffect, useMemo } = React;
  const {
    Icons,
    DEMO_ANALYSIS,
    DEMO_EVAL,
    formatTorontoTime,
    formatTorontoDateTime,
    parseDomain,
    parseTitle,
    scrollToSection,
    useToast,
    ToastContainer,
    RiskTag,
    StatusTag,
    CitationBlock,
    ObligationCard,
    EmptyState,
  } = window.ComplianceUI;

  const API_BASE = window.location.origin;

  function App() {
    const [tab, setTab] = useState("obligations");
    const [data, setData] = useState(DEMO_ANALYSIS);
    const [evalData, setEvalData] = useState(DEMO_EVAL);
    const [riskFilter, setRiskFilter] = useState("all");
    const [statusFilter, setStatusFilter] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");
    const [reviewModal, setReviewModal] = useState(null);
    const [reviewNotes, setReviewNotes] = useState("");
    const [selectedObligation, setSelectedObligation] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [pasteText, setPasteText] = useState("");
    const [isPasteAnalyzing, setIsPasteAnalyzing] = useState(false);
    const [pasteResults, setPasteResults] = useState(null);
    const [pasteEngine, setPasteEngine] = useState("llm");
    const [cacheStats, setCacheStats] = useState(null);
    const [isCacheLoading, setIsCacheLoading] = useState(false);
    const [isCacheClearing, setIsCacheClearing] = useState(false);
    const [currentRole, setCurrentRole] = useState("compliance_officer");
    const [isReverting, setIsReverting] = useState(null);
    const { toasts, addToast } = useToast();

    useEffect(() => {
      fetch(`${API_BASE}/api/analysis`)
        .then((r) => r.json())
        .then((result) => {
          if (result.obligations) {
            setData({
              obligations: result.obligations || [],
              conflicts: result.conflicts || [],
              audit_log: result.audit_log || [],
              stats: result.stats || {},
            });
          }
          setIsLoading(false);
        })
        .catch(() => setIsLoading(false));
    }, []);

    function fetchCacheStats(silent = false) {
      if (!silent) {
        setIsCacheLoading(true);
      }
      return fetch(`${API_BASE}/api/cache/stats`)
        .then((r) => r.json())
        .then((stats) => {
          setCacheStats(stats);
        })
        .catch(() => {
          if (!silent) {
            addToast("Unable to load cache stats", "error");
          }
        })
        .finally(() => {
          if (!silent) {
            setIsCacheLoading(false);
          }
        });
    }

    useEffect(() => {
      fetchCacheStats(true);
    }, []);

    function handleClearCache() {
      setIsCacheClearing(true);
      fetch(`${API_BASE}/api/cache/clear`, { method: "POST" })
        .then((r) => r.json())
        .then((result) => {
          fetchCacheStats(true);
          const removed = result?.cleared?.removed_entries ?? 0;
          addToast(`Cleared ${removed} cached response(s)`, "success");
        })
        .catch(() => {
          addToast("Unable to clear cache", "error");
        })
        .finally(() => {
          setIsCacheClearing(false);
        });
    }

    const filteredObligations = useMemo(() => {
      return data.obligations.filter((o) => {
        if (riskFilter !== "all" && o.risk_level !== riskFilter) return false;
        if (
          statusFilter === "needs_review" &&
          !(o.requires_human_review && o.status === "draft")
        )
          return false;
        if (statusFilter === "approved" && o.status !== "approved")
          return false;
        if (statusFilter === "rejected" && o.status !== "rejected")
          return false;
        if (searchQuery.trim()) {
          const q = searchQuery.trim().toLowerCase();
          const text = (
            o.description +
            " " +
            (o.citation?.excerpt || "")
          ).toLowerCase();
          if (!text.includes(q)) return false;
        }
        return true;
      });
    }, [data.obligations, riskFilter, statusFilter, searchQuery]);

    const reviewQueue = useMemo(() => {
      const priority = { critical: 1, high: 2, medium: 3, low: 4 };
      return data.obligations
        .filter((o) => o.requires_human_review && o.status === "draft")
        .slice()
        .sort((a, b) => {
          const riskOrder =
            (priority[a.risk_level] || 9) - (priority[b.risk_level] || 9);
          if (riskOrder !== 0) return riskOrder;
          const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
          const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
          return aTime - bTime;
        });
    }, [data.obligations]);

    async function handleReview(obligationId, action, notesOverride) {
      const notes = notesOverride ?? reviewNotes;
      try {
        const response = await fetch(`${API_BASE}/api/review`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            obligation_id: obligationId,
            reviewer: `${currentRole}@wealthsimple.com`,
            action,
            role: currentRole,
            notes,
          }),
        });
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Review failed");
        }
        const result = await response.json();
        setData(result);
        if (selectedObligation) {
          const refreshed = result.obligations.find(
            (o) => o.id === selectedObligation.id,
          );
          setSelectedObligation(refreshed || null);
        }
        setReviewModal(null);
        setReviewNotes("");
        addToast(
          action === "approve"
            ? "Obligation approved successfully"
            : "Obligation rejected",
          action === "approve" ? "success" : "error",
        );
      } catch (error) {
        addToast(error.message || "Review failed", "error");
      }
    }

    async function handleRevert(obligationId) {
      if (currentRole !== "admin") {
        addToast("Only admin role can revert reviews", "error");
        return;
      }
      setIsReverting(obligationId);
      try {
        const response = await fetch(`${API_BASE}/api/review/revert`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            obligation_id: obligationId,
            admin_user: "admin@wealthsimple.com",
            admin_role: "admin",
          }),
        });
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Revert failed");
        }
        const result = await response.json();
        setData(result);
        if (selectedObligation) {
          const refreshed = result.obligations.find(
            (o) => o.id === selectedObligation.id,
          );
          setSelectedObligation(refreshed || null);
        }
        addToast(
          "Review reverted — obligation restored to previous state",
          "success",
        );
      } catch (error) {
        addToast(error.message || "Revert failed", "error");
      } finally {
        setIsReverting(null);
      }
    }

    const canReview =
      currentRole === "admin" || currentRole === "compliance_officer";
    const canRevert = currentRole === "admin";

    function applyQuickFilter(type) {
      if (type === "conflicts") {
        setTab("conflicts");
        scrollToSection("conflicts-section");
        return;
      }
      setTab("obligations");
      setSearchQuery("");
      if (type === "needs_review") {
        setStatusFilter("needs_review");
        setRiskFilter("all");
        scrollToSection("obligations-section");
        return;
      }
      if (type === "critical") {
        setRiskFilter("critical");
        setStatusFilter("all");
        scrollToSection("obligations-section");
        return;
      }
      if (type === "high") {
        setRiskFilter("high");
        setStatusFilter("all");
        scrollToSection("obligations-section");
        return;
      }
      setRiskFilter("all");
      setStatusFilter("all");
      scrollToSection("obligations-section");
    }

    function handleRunAnalysis() {
      setIsAnalyzing(true);
      addToast("Running compliance analysis...", "info");
      fetch(`${API_BASE}/api/analyze`, { method: "POST" })
        .then((r) => r.json())
        .then((result) => {
          setData({
            obligations: result.obligations || [],
            conflicts: result.conflicts || [],
            audit_log: result.audit_log || [],
            stats: result.stats || {},
          });
          setIsAnalyzing(false);
          addToast(
            `Analysis complete — ${(result.obligations || []).length} obligations found`,
            "success",
          );
        })
        .catch(() => {
          setData(DEMO_ANALYSIS);
          setIsAnalyzing(false);
          addToast("Using demo data (server unavailable)", "info");
        });
    }

    function handlePasteAnalyze() {
      if (!pasteText.trim()) return;
      setIsPasteAnalyzing(true);
      setPasteResults(null);
      fetch(`${API_BASE}/api/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: pasteText,
          use_llm: pasteEngine === "llm",
        }),
      })
        .then((r) => r.json())
        .then((result) => {
          setPasteResults(result);
          setIsPasteAnalyzing(false);
          fetchCacheStats(true);
          addToast("Text analysis complete", "success");
        })
        .catch((err) => {
          setPasteResults({ error: err.message || "Analysis failed" });
          setIsPasteAnalyzing(false);
          addToast("Analysis failed", "error");
        });
    }

    function handleRunEval() {
      addToast("Running evaluation harness...", "info");
      fetch(`${API_BASE}/api/eval/run`)
        .then((r) => r.json())
        .then((result) => {
          if (result.metrics) {
            setEvalData({ metrics: result.metrics });
            addToast("Evaluation complete", "success");
          }
        })
        .catch(() => {
          addToast("Using cached eval results", "info");
        });
    }

    const criticalCount = data.obligations.filter(
      (o) => o.risk_level === "critical",
    ).length;
    const highCount = data.obligations.filter(
      (o) => o.risk_level === "high",
    ).length;

    const tabs = [
      {
        key: "obligations",
        label: "Obligations",
        count: data.obligations.length,
      },
      {
        key: "queue",
        label: "Review Queue",
        count: reviewQueue.length,
      },
      {
        key: "conflicts",
        label: "Conflicts",
        count: data.conflicts.length,
      },
      { key: "audit", label: "Audit Log", count: data.audit_log.length },
      { key: "analyze", label: "Analyze Text" },
      { key: "eval", label: "Eval Harness" },
    ];

    return (
      <div className="app-wrapper">
        {/* HEADER */}
        <div className="header">
          <div className="header-inner">
            <div className="header-left">
              <div className="header-logo">CA</div>
              <div>
                <div className="header-title">Compliance AI</div>
                <div className="header-subtitle">
                  Regulatory monitoring for Wealthsimple
                </div>
              </div>
            </div>
            <div className="header-right">
              <div className="role-selector">
                <select
                  value={currentRole}
                  onChange={(e) => {
                    setCurrentRole(e.target.value);
                    addToast(`Switched to ${e.target.value} role`, "info");
                  }}
                  className="role-dropdown"
                >
                  <option value="admin">Admin</option>
                  <option value="compliance_officer">Compliance Officer</option>
                  <option value="analyst">Analyst (Read-only)</option>
                  <option value="viewer">Viewer (Read-only)</option>
                </select>
              </div>
              <div className="status-badge">
                <div
                  className={`status-dot ${isLoading ? "connecting" : ""}`}
                />
                {isLoading ? "Connecting..." : "System Live"}
              </div>
              <a
                href="https://github.com/Shams261/wealthsimple-compliance-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-github"
                style={{ textDecoration: "none" }}
              >
                <Icons.github size={14} /> GitHub
              </a>
              <button
                className="btn btn-primary"
                onClick={handleRunAnalysis}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? (
                  <React.Fragment>
                    <Icons.activity
                      size={14}
                      style={{ animation: "pulse 1s infinite" }}
                    />{" "}
                    Analyzing...
                  </React.Fragment>
                ) : (
                  <React.Fragment>
                    <Icons.zap size={14} /> Run Analysis
                  </React.Fragment>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* STATS */}
        <div className="stats-section">
          <div className="stats-grid">
            {[
              {
                label: "Total Obligations",
                value: data.stats.total_obligations || 0,
                sub: `across ${data.sources_count || 10} regulators`,
                color: "var(--accent)",
                icon: <Icons.fileText size={16} />,
                filterKey: "all",
              },
              {
                label: "Needs Review",
                value: data.stats.needs_human_review || 0,
                sub: "flagged for team",
                color: "var(--orange)",
                icon: <Icons.eye size={16} />,
                filterKey: "needs_review",
              },
              {
                label: "Citation Coverage",
                value: `${data.stats.citation_coverage || 0}%`,
                sub: "evidence-backed",
                color: "var(--green)",
                icon: <Icons.checkCircle size={16} />,
                filterKey: "all",
              },
              {
                label: "Critical Risk",
                value: criticalCount,
                sub: "immediate attention",
                color: "var(--red)",
                icon: <Icons.alertTriangle size={16} />,
                filterKey: "critical",
              },
              {
                label: "High Risk",
                value: highCount,
                sub: "elevated priority",
                color: "var(--orange)",
                icon: <Icons.shield size={16} />,
                filterKey: "high",
              },
              {
                label: "Conflicts",
                value: data.conflicts.length,
                sub: "cross-regulator",
                color: "var(--yellow)",
                icon: <Icons.zap size={16} />,
                filterKey: "conflicts",
              },
            ].map((s, i) => (
              <div
                className={`stat-card is-clickable`}
                key={i}
                style={{ "--stat-accent": s.color }}
                role="button"
                tabIndex={0}
                onClick={() => applyQuickFilter(s.filterKey)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    applyQuickFilter(s.filterKey);
                  }
                }}
              >
                <div
                  className="stat-icon"
                  style={{
                    background: s.color + "12",
                    color: s.color,
                    border: `1px solid ${s.color}25`,
                  }}
                >
                  {s.icon}
                </div>
                <div className="stat-label">{s.label}</div>
                <div className="stat-value" style={{ color: s.color }}>
                  {s.value}
                </div>
                <div className="stat-sub">{s.sub}</div>
                <div className="stat-hint">Click to view</div>
              </div>
            ))}
          </div>
        </div>

        {/* TAB BAR + SEARCH */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 28,
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div className="tab-bar">
            {tabs.map((t) => (
              <button
                key={t.key}
                className={`tab-item ${tab === t.key ? "active" : ""}`}
                onClick={() => setTab(t.key)}
              >
                {t.label}
                {t.count !== undefined && (
                  <span className="tab-badge">{t.count}</span>
                )}
              </button>
            ))}
          </div>
          {tab === "obligations" && (
            <div className="search-bar">
              <Icons.search size={15} />
              <input
                type="text"
                placeholder="Search obligations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          )}
        </div>

        {/* === OBLIGATIONS TAB === */}
        {tab === "obligations" && (
          <div className="fade-in" id="obligations-section">
            <div className="filters-bar">
              <span className="filter-label">Risk</span>
              {["all", "critical", "high", "medium", "low"].map((f) => (
                <button
                  key={f}
                  className={`filter-chip ${riskFilter === f ? "active" : ""}`}
                  onClick={() => setRiskFilter(f)}
                >
                  {f === "all" ? "All" : f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
              <div className="filter-divider" />
              <span className="filter-label">Status</span>
              {["all", "needs_review", "approved", "rejected"].map((f) => (
                <button
                  key={f}
                  className={`filter-chip ${statusFilter === f ? "active" : ""}`}
                  onClick={() => setStatusFilter(f)}
                >
                  {f === "all"
                    ? "All"
                    : f === "needs_review"
                      ? "Needs Review"
                      : f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
            <div className="scroll-area">
              {isLoading ? (
                <React.Fragment>
                  <div className="skeleton skeleton-card"></div>
                  <div className="skeleton skeleton-card"></div>
                  <div className="skeleton skeleton-card"></div>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  {filteredObligations.map((ob, i) => (
                    <ObligationCard
                      key={ob.id}
                      ob={ob}
                      index={i}
                      canReview={canReview}
                      canRevert={canRevert}
                      onOpen={(item) => setSelectedObligation(item)}
                      onApprove={(id) => {
                        setReviewModal(id);
                        setReviewNotes("");
                      }}
                      onReject={(id) => handleReview(id, "reject")}
                      onRevert={(id) => handleRevert(id)}
                    />
                  ))}
                  {filteredObligations.length === 0 && (
                    <EmptyState
                      icon={<Icons.search size={24} />}
                      title="No obligations found"
                      message="Try adjusting the filters or search query"
                    />
                  )}
                </React.Fragment>
              )}
            </div>
          </div>
        )}

        {/* === REVIEW QUEUE TAB === */}
        {tab === "queue" && (
          <div className="fade-in" id="queue-section">
            <div className="section-header">
              <div>
                <h3>Review Queue</h3>
                <p>{reviewQueue.length} obligation(s) awaiting human review</p>
              </div>
              <button
                className="btn"
                onClick={() => {
                  setTab("obligations");
                  setStatusFilter("needs_review");
                  setRiskFilter("all");
                  scrollToSection("obligations-section");
                }}
              >
                Open In Obligations
              </button>
            </div>
            {reviewQueue.length === 0 ? (
              <EmptyState
                icon={<Icons.checkCircle size={24} />}
                title="No items in queue"
                message="All obligations have been reviewed"
              />
            ) : (
              <div>
                {reviewQueue.map((ob, i) => (
                  <ObligationCard
                    key={ob.id}
                    ob={ob}
                    index={i}
                    canReview={canReview}
                    canRevert={canRevert}
                    onOpen={(item) => setSelectedObligation(item)}
                    onApprove={(id) => {
                      setReviewModal(id);
                      setReviewNotes("");
                    }}
                    onReject={(id) => handleReview(id, "reject", "")}
                    onRevert={(id) => handleRevert(id)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* === CONFLICTS TAB === */}
        {tab === "conflicts" && (
          <div className="scroll-area fade-in" id="conflicts-section">
            {data.conflicts.length === 0 && (
              <EmptyState
                icon={<Icons.checkCircle size={24} />}
                title="No conflicts detected"
                message="All regulatory sources are in alignment"
              />
            )}
            {data.conflicts.map((c, i) => (
              <div
                className="conflict-card fade-in"
                key={c.id}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className="conflict-header">
                  <div className="conflict-icon">!</div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontWeight: 700,
                        fontSize: 15,
                        letterSpacing: "-0.3px",
                      }}
                    >
                      Policy Conflict Detected
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--text-muted)",
                        marginTop: 3,
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                      }}
                    >
                      <span
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: 3,
                          background: "var(--yellow)",
                          display: "inline-block",
                        }}
                      />
                      Status: {c.resolution_status}
                    </div>
                  </div>
                  <span className="tag tag-critical">ESCALATED</span>
                </div>
                <div
                  style={{
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    lineHeight: 1.7,
                  }}
                >
                  {c.description}
                </div>
                <div className="conflict-sources">
                  <div>
                    <div className="conflict-label">Source A</div>
                    <CitationBlock citation={c.source_a} />
                  </div>
                  <div>
                    <div className="conflict-label">Source B</div>
                    <CitationBlock citation={c.source_b} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* === AUDIT LOG TAB === */}
        {tab === "audit" && (
          <div className="scroll-area fade-in">
            <div className="audit-timeline">
              {data.audit_log.map((entry, i) => (
                <div
                  className="log-entry"
                  key={entry.id}
                  style={{ animationDelay: `${i * 0.03}s` }}
                >
                  <span className="log-time">
                    {formatTorontoTime(entry.timestamp)}
                  </span>
                  <span className="log-action">
                    {entry.action.replace(/_/g, " ")}
                  </span>
                  <span className="log-detail">
                    [{entry.entity_type}:{entry.entity_id}] {entry.notes}
                  </span>
                  <span className="log-actor">{entry.actor}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* === ANALYZE TEXT TAB === */}
        {tab === "analyze" && (
          <div className="analyze-section fade-in">
            <div className="analyze-header">
              <h3>Analyze Regulatory Text</h3>
              <p>
                Paste any regulation or guidance document and the system will
                extract obligations, map them to Wealthsimple products, and flag
                items requiring human review.
              </p>
            </div>
            <textarea
              className="analyze-textarea"
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder={
                'Paste regulatory text here...\n\nExample:\n"An organization must report to the Privacy Commissioner any breach of security safeguards involving personal information under its control if it is reasonable in the circumstances to believe that the breach creates a real risk of significant harm to an individual."'
              }
            />
            <div className="analyze-toolbar">
              <div className="engine-toggle">
                <button
                  className={`engine-option ${pasteEngine === "llm" ? "active" : ""}`}
                  onClick={() => setPasteEngine("llm")}
                >
                  <Icons.sparkles /> Claude LLM
                </button>
                <button
                  className={`engine-option ${pasteEngine === "deterministic" ? "active" : ""}`}
                  onClick={() => setPasteEngine("deterministic")}
                >
                  Deterministic
                </button>
              </div>
              <button
                className="btn btn-primary"
                onClick={handlePasteAnalyze}
                disabled={isPasteAnalyzing || !pasteText.trim()}
              >
                {isPasteAnalyzing ? (
                  <React.Fragment>
                    <Icons.activity
                      size={14}
                      style={{ animation: "pulse 1s infinite" }}
                    />{" "}
                    Analyzing...
                  </React.Fragment>
                ) : (
                  <React.Fragment>
                    <Icons.play size={14} /> Analyze
                  </React.Fragment>
                )}
              </button>
            </div>
            <div
              style={{
                marginTop: 12,
                padding: "12px 14px",
                border: "1px solid var(--border)",
                borderRadius: 10,
                background: "var(--bg-card)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 10,
                flexWrap: "wrap",
              }}
            >
              <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
                <strong>LLM Cache</strong>
                {cacheStats
                  ? ` · Active ${cacheStats.active_entries}/${cacheStats.total_entries} · TTL ${cacheStats.ttl_days}d`
                  : " · Not loaded"}
              </div>
              <button
                className="btn btn-sm"
                onClick={() => fetchCacheStats(false)}
                disabled={isCacheLoading || isCacheClearing}
              >
                {isCacheLoading ? "Refreshing..." : "Refresh Cache Stats"}
              </button>
              <button
                className="btn btn-sm btn-reject"
                onClick={handleClearCache}
                disabled={isCacheClearing || isCacheLoading}
              >
                {isCacheClearing ? "Clearing..." : "Clear Cache"}
              </button>
            </div>
            {pasteResults && !pasteResults.error && (
              <div>
                <div className="results-banner">
                  <Icons.checkCircle size={16} />
                  Found {pasteResults.obligations?.length || 0} obligation(s) —
                  Citation coverage:{" "}
                  {pasteResults.stats?.citation_coverage || 0}%
                </div>
                <div className="scroll-area">
                  {(pasteResults.obligations || []).map((ob, i) => (
                    <ObligationCard
                      key={ob.id}
                      ob={{
                        ...ob,
                        escalation_reasons: ob.escalation_reasons || [],
                        mapped_products: ob.mapped_products || [],
                        mapped_controls: ob.mapped_controls || [],
                      }}
                      onApprove={() => {}}
                      onReject={() => {}}
                      onOpen={(item) => setSelectedObligation(item)}
                      index={i}
                    />
                  ))}
                </div>
              </div>
            )}
            {pasteResults && pasteResults.error && (
              <div className="error-box" style={{ marginTop: 16 }}>
                <Icons.alertTriangle size={16} />
                Error: {pasteResults.error}
              </div>
            )}
          </div>
        )}

        {/* === EVAL HARNESS TAB === */}
        {tab === "eval" && (
          <div className="fade-in">
            <div className="section-header">
              <div>
                <h3>Evaluation Harness</h3>
                <p>
                  {evalData.metrics.total_test_cases} regulatory snippets with
                  expected output mappings
                </p>
              </div>
              <button className="btn" onClick={handleRunEval}>
                <Icons.play size={14} /> Run Live Eval
              </button>
            </div>
            <div className="eval-hero-grid">
              {[
                {
                  label: "Extraction Accuracy",
                  value: evalData.metrics.obligation_extraction_accuracy,
                  color: "var(--accent)",
                  gradient:
                    "linear-gradient(135deg, rgba(139,108,239,0.08), transparent)",
                },
                {
                  label: "Product Mapping",
                  value: evalData.metrics.product_mapping_accuracy,
                  color: "var(--blue)",
                  gradient:
                    "linear-gradient(135deg, rgba(96,165,250,0.08), transparent)",
                },
                {
                  label: "Risk Accuracy",
                  value: evalData.metrics.risk_level_accuracy,
                  color: "var(--green)",
                  gradient:
                    "linear-gradient(135deg, rgba(52,211,153,0.08), transparent)",
                },
              ].map((m, i) => (
                <div className="eval-hero-card" key={i}>
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      background: m.gradient,
                      pointerEvents: "none",
                    }}
                  />
                  <div
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 2,
                      background: m.color,
                    }}
                  />
                  <div
                    className="eval-score"
                    style={{ color: m.color, position: "relative" }}
                  >
                    {m.value.toFixed(0)}%
                  </div>
                  <div className="eval-label" style={{ position: "relative" }}>
                    {m.label}
                  </div>
                </div>
              ))}
            </div>
            {[
              {
                label: "Obligation Extraction",
                value: evalData.metrics.obligation_extraction_accuracy,
                color: "var(--accent)",
              },
              {
                label: "Product Mapping",
                value: evalData.metrics.product_mapping_accuracy,
                color: "var(--blue)",
              },
              {
                label: "Control Mapping",
                value: evalData.metrics.control_mapping_accuracy,
                color: "var(--green)",
              },
              {
                label: "Citation Coverage",
                value: evalData.metrics.citation_coverage,
                color: "var(--green)",
              },
              {
                label: "Risk Level Accuracy",
                value: evalData.metrics.risk_level_accuracy,
                color: "var(--yellow)",
              },
              {
                label: "Escalation Accuracy",
                value: evalData.metrics.escalation_accuracy,
                color: "var(--orange)",
              },
            ].map((m, i) => (
              <div className="eval-detail-row" key={i}>
                <span className="eval-bar-label">{m.label}</span>
                <div className="eval-bar-right">
                  <div className="eval-bar-track">
                    <div
                      className="eval-bar-fill"
                      style={{ width: `${m.value}%`, background: m.color }}
                    />
                  </div>
                  <span className="eval-bar-value" style={{ color: m.color }}>
                    {m.value.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
            <div className="eval-summary-grid">
              {[
                {
                  label: "Domain Matches",
                  value: evalData.metrics.perfect_domain_matches,
                },
                {
                  label: "Risk Matches",
                  value: evalData.metrics.perfect_risk_matches,
                },
                {
                  label: "Escalation Matches",
                  value: evalData.metrics.perfect_escalation_matches,
                },
              ].map((m, i) => (
                <div className="eval-summary-item" key={i}>
                  <div
                    className="eval-summary-value"
                    style={{ color: "var(--green)" }}
                  >
                    {m.value}/{evalData.metrics.total_test_cases}
                  </div>
                  <div className="eval-summary-label">{m.label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* REVIEW MODAL */}
        {reviewModal && (
          <div className="modal-backdrop" onClick={() => setReviewModal(null)}>
            <div
              className="modal-panel fade-in"
              onClick={(e) => e.stopPropagation()}
            >
              <h3>Approve Obligation</h3>
              <p>
                Add optional review notes. This action will be recorded in the
                audit trail for compliance tracking.
              </p>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Review notes..."
              />
              <div className="modal-actions">
                <button className="btn" onClick={() => setReviewModal(null)}>
                  Cancel
                </button>
                <button
                  className="btn btn-approve"
                  onClick={() =>
                    handleReview(reviewModal, "approve", reviewNotes)
                  }
                >
                  <Icons.check size={14} /> Approve
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedObligation && (
          <React.Fragment>
            <div
              className="drawer-overlay"
              onClick={() => setSelectedObligation(null)}
            />
            <div className="drawer" role="dialog" aria-modal="true">
              <div className="drawer-header">
                <div>
                  <div className="drawer-title">
                    {parseTitle(selectedObligation.description)}
                  </div>
                  <div className="drawer-sub">
                    {parseDomain(selectedObligation.description)}
                  </div>
                </div>
                <button
                  className="btn btn-sm"
                  onClick={() => setSelectedObligation(null)}
                >
                  Close
                </button>
              </div>
              <div className="drawer-body">
                <div className="drawer-section">
                  <h4>Status</h4>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <RiskTag level={selectedObligation.risk_level} />
                    <StatusTag status={selectedObligation.status} />
                  </div>
                </div>
                <div className="drawer-section">
                  <h4>Review Actions</h4>
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      marginBottom: 8,
                    }}
                  >
                    Current role:{" "}
                    <strong style={{ color: "var(--accent)" }}>
                      {currentRole}
                    </strong>
                    {canReview
                      ? " — can approve/reject"
                      : " — read-only access"}
                    {canRevert ? " + can revert" : ""}
                  </div>
                  <div className="drawer-actions">
                    <textarea
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      placeholder="Add review notes (optional)..."
                    />
                    {selectedObligation.status === "draft" && canReview && (
                      <React.Fragment>
                        <button
                          className="btn btn-approve"
                          onClick={() =>
                            handleReview(
                              selectedObligation.id,
                              "approve",
                              reviewNotes,
                            )
                          }
                        >
                          <Icons.check size={14} /> Approve
                        </button>
                        <button
                          className="btn btn-reject"
                          onClick={() =>
                            handleReview(
                              selectedObligation.id,
                              "reject",
                              reviewNotes,
                            )
                          }
                        >
                          <Icons.x size={14} /> Reject
                        </button>
                      </React.Fragment>
                    )}
                    {selectedObligation.status === "draft" && !canReview && (
                      <div
                        style={{
                          fontSize: 13,
                          color: "var(--text-muted)",
                          fontStyle: "italic",
                        }}
                      >
                        Switch to compliance_officer or admin role to review.
                      </div>
                    )}
                    {selectedObligation.status !== "draft" && (
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          flexWrap: "wrap",
                        }}
                      >
                        <div
                          style={{ fontSize: 13, color: "var(--text-muted)" }}
                        >
                          Status: <strong>{selectedObligation.status}</strong>{" "}
                          by {selectedObligation.reviewed_by || "unknown"}
                        </div>
                        {canRevert && (
                          <button
                            className="btn btn-sm"
                            style={{ fontSize: 12 }}
                            onClick={() => handleRevert(selectedObligation.id)}
                            disabled={isReverting === selectedObligation.id}
                          >
                            {isReverting === selectedObligation.id
                              ? "Reverting..."
                              : "↩ Revert Review"}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="drawer-section">
                  <h4>Summary</h4>
                  <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>
                    {selectedObligation.description}
                  </div>
                </div>
                <div className="drawer-section">
                  <h4>Metadata</h4>
                  <div className="drawer-meta">
                    <div>
                      <strong>Confidence</strong>
                      {selectedObligation.confidence || "-"}
                    </div>
                    <div>
                      <strong>Created</strong>
                      {selectedObligation.created_at
                        ? formatTorontoDateTime(selectedObligation.created_at)
                        : "-"}
                    </div>
                    <div>
                      <strong>Reviewed By</strong>
                      {selectedObligation.reviewed_by || "-"}
                    </div>
                    <div>
                      <strong>Reviewed At</strong>
                      {selectedObligation.reviewed_at
                        ? formatTorontoDateTime(selectedObligation.reviewed_at)
                        : "-"}
                    </div>
                  </div>
                </div>
                <div className="drawer-section">
                  <h4>Evidence</h4>
                  <CitationBlock citation={selectedObligation.citation} />
                </div>
                <div className="drawer-section">
                  <h4>Products & Controls</h4>
                  <div className="pill-label">Products</div>
                  <div className="pill-group">
                    {(selectedObligation.mapped_products || []).map((p, i) => (
                      <span key={i} className="pill">
                        {p.name.replace("Wealthsimple ", "")}
                      </span>
                    ))}
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <div className="pill-label">Controls</div>
                    <div className="pill-group">
                      {(selectedObligation.mapped_controls || []).map(
                        (c, i) => (
                          <span key={i} className="pill pill-green">
                            {c.name}
                          </span>
                        ),
                      )}
                    </div>
                  </div>
                </div>
                <div className="drawer-section">
                  <h4>Audit Trail</h4>
                  {(data.audit_log || [])
                    .filter(
                      (entry) => entry.entity_id === selectedObligation.id,
                    )
                    .map((entry) => (
                      <div key={entry.id} className="audit-item">
                        <strong>{entry.action.replace(/_/g, " ")}</strong> —{" "}
                        {entry.actor}
                        <div
                          style={{
                            fontSize: 12,
                            color: "var(--text-dim)",
                            marginTop: 4,
                          }}
                        >
                          {formatTorontoDateTime(entry.timestamp)}
                          {entry.notes ? ` • ${entry.notes}` : ""}
                        </div>
                      </div>
                    ))}
                  {(data.audit_log || []).filter(
                    (entry) => entry.entity_id === selectedObligation.id,
                  ).length === 0 && (
                    <div className="audit-item">No audit entries yet.</div>
                  )}
                </div>
              </div>
            </div>
          </React.Fragment>
        )}

        {/* FOOTER */}
        <footer className="footer">
          <div>
            <h5>Compliance AI</h5>
            <p>
              Evidence-first compliance intelligence for regulated product
              teams. Built to help reviewers move faster with traceable
              decisions.
            </p>
            <div className="footer-meta">
              System status: {isLoading ? "Connecting" : "Live"} · Region:
              Canada
            </div>
          </div>
          <div>
            <h5>Product</h5>
            <div className="footer-links">
              <span>Review Queue</span>
              <span>Audit Trail</span>
              <span>Evidence Mapping</span>
              <span>Risk Triage</span>
            </div>
          </div>
          <div>
            <h5>Governance</h5>
            <div className="footer-links">
              <span>Data Retention</span>
              <span>Model Oversight</span>
              <span>Change Log</span>
              <span>Security Controls</span>
            </div>
          </div>
        </footer>

        {/* TOAST NOTIFICATIONS */}
        <ToastContainer toasts={toasts} />
      </div>
    );
  }

  ReactDOM.createRoot(document.getElementById("root")).render(<App />);
})();
