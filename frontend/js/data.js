(() => {
  const DEMO_ANALYSIS = (() => {
    const obligations = [
      {
        id: "ob-001",
        description: "[KYC] Obligation from CSA: Know Your Client",
        citation: {
          source_document: "NI 31-103 — Registration Requirements",
          section: "31-103-s13.2 — Know Your Client",
          excerpt:
            "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, it has sufficient information regarding the client's investment needs, objectives, financial circumstances, risk tolerance, investment knowledge, and investment time horizon.",
        },
        risk_level: "high",
        confidence: "high",
        status: "draft",
        mapped_products: [
          { id: "ws_invest", name: "Wealthsimple Invest" },
          { id: "ws_trade", name: "Wealthsimple Trade" },
          { id: "ws_options", name: "Wealthsimple Options" },
        ],
        mapped_controls: [
          { id: "ctrl_kyc_onboarding", name: "KYC Onboarding Flow" },
        ],
        escalation_reasons: ["high_risk", "customer_facing_change"],
        requires_human_review: true,
      },
      {
        id: "ob-002",
        description:
          "[SUITABILITY] Obligation from CSA: Suitability Determination",
        citation: {
          source_document: "NI 31-103 — Registration Requirements",
          section: "31-103-s13.3 — Suitability Determination",
          excerpt:
            "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, the purchase or sale is suitable for the client.",
        },
        risk_level: "high",
        confidence: "high",
        status: "draft",
        mapped_products: [
          { id: "ws_invest", name: "Wealthsimple Invest" },
          { id: "ws_trade", name: "Wealthsimple Trade" },
        ],
        mapped_controls: [
          {
            id: "ctrl_suitability_engine",
            name: "Suitability Assessment Engine",
          },
        ],
        escalation_reasons: ["high_risk", "customer_facing_change"],
        requires_human_review: true,
      },
      {
        id: "ob-003",
        description:
          "[AML] Obligation from FINTRAC: Suspicious Transaction Reporting",
        citation: {
          source_document: "PCMLTFA — FINTRAC Guidelines",
          section: "FINTRAC-STR-1 — Suspicious Transaction Reporting",
          excerpt:
            "If a reporting entity has reasonable grounds to suspect that a transaction or attempted transaction is related to the commission of a money laundering offence or a terrorist activity financing offence, the entity must submit a Suspicious Transaction Report (STR) to FINTRAC within 30 calendar days.",
        },
        risk_level: "critical",
        confidence: "high",
        status: "draft",
        mapped_products: [
          { id: "ws_trade", name: "Wealthsimple Trade" },
          { id: "ws_crypto", name: "Wealthsimple Crypto" },
          { id: "ws_cash", name: "Wealthsimple Cash" },
        ],
        mapped_controls: [
          { id: "ctrl_aml_screening", name: "AML Transaction Monitoring" },
        ],
        escalation_reasons: ["high_risk"],
        requires_human_review: true,
      },
      {
        id: "ob-009",
        description:
          "[BREACH_NOTIFICATION] Obligation from PIPEDA: Breach of Security Safeguards",
        citation: {
          source_document: "PIPEDA",
          section: "PIPEDA-BREACH-1 — Breach of Security Safeguards",
          excerpt:
            "An organization must report to the Privacy Commissioner any breach of security safeguards involving personal information under its control if it is reasonable in the circumstances to believe that the breach creates a real risk of significant harm to an individual.",
        },
        risk_level: "critical",
        confidence: "high",
        status: "draft",
        mapped_products: [
          { id: "ws_invest", name: "Wealthsimple Invest" },
          { id: "ws_trade", name: "Wealthsimple Trade" },
          { id: "ws_crypto", name: "Wealthsimple Crypto" },
          { id: "ws_cash", name: "Wealthsimple Cash" },
          { id: "ws_tax", name: "Wealthsimple Tax" },
        ],
        mapped_controls: [
          {
            id: "ctrl_privacy_framework",
            name: "Privacy and Data Protection Framework",
          },
        ],
        escalation_reasons: ["high_risk"],
        requires_human_review: true,
      },
    ];
    const conflicts = [
      {
        id: "conf-001",
        conflict_type: "policy_conflict",
        description:
          "CSA requires KYC before making recommendations, while FINTRAC allows up to 30 days after account opening for identity verification.",
        source_a: {
          source_document: "NI 31-103",
          section: "31-103-s13.2 — KYC",
          excerpt:
            "...before it makes a recommendation to or accepts an instruction from a client...",
        },
        source_b: {
          source_document: "PCMLTFA — FINTRAC",
          section: "FINTRAC-KYC-1",
          excerpt:
            "Verification must be completed before or within 30 days of the account opening.",
        },
        resolution_status: "pending",
      },
      {
        id: "conf-002",
        conflict_type: "policy_conflict",
        description:
          "PIPEDA requires disposal of data no longer needed, while CIRO requires retaining complaint records for minimum 7 years.",
        source_a: {
          source_document: "PIPEDA",
          section: "PIPEDA-RETENTION-1",
          excerpt:
            "Personal information that is no longer required to fulfil the identified purposes should be destroyed, erased, or made anonymous.",
        },
        source_b: {
          source_document: "CIRO — Dealer Member Rules",
          section: "CIRO-COMP-1",
          excerpt:
            "The dealer must maintain records of all complaints for a minimum of 7 years.",
        },
        resolution_status: "pending",
      },
    ];
    const auditLog = [
      {
        id: "log-001",
        timestamp: "2026-03-01T12:00:01Z",
        action: "analysis_started",
        actor: "system",
        entity_type: "analysis",
        entity_id: "full_scan",
        notes: "Analyzing 7 regulatory sources",
      },
      {
        id: "log-002",
        timestamp: "2026-03-01T12:00:02Z",
        action: "obligation_extracted",
        actor: "system",
        entity_type: "obligation",
        entity_id: "ob-001",
        notes: "Domain: KYC, Confidence: high",
      },
      {
        id: "log-003",
        timestamp: "2026-03-01T12:00:02Z",
        action: "obligation_extracted",
        actor: "system",
        entity_type: "obligation",
        entity_id: "ob-003",
        notes: "Domain: AML, Confidence: high",
      },
      {
        id: "log-004",
        timestamp: "2026-03-01T12:00:03Z",
        action: "conflict_detected",
        actor: "system",
        entity_type: "conflict",
        entity_id: "conf-001",
        notes: "KYC timing conflict",
      },
      {
        id: "log-005",
        timestamp: "2026-03-01T12:00:04Z",
        action: "analysis_completed",
        actor: "system",
        entity_type: "analysis",
        entity_id: "full_scan",
        notes: "18 obligations, 2 conflicts",
      },
    ];
    const stats = {
      total_obligations: obligations.length,
      auto_approved: obligations.filter((o) => !o.requires_human_review).length,
      needs_human_review: obligations.filter((o) => o.requires_human_review)
        .length,
      high_risk_count: obligations.filter(
        (o) => o.risk_level === "high" || o.risk_level === "critical",
      ).length,
      citation_coverage: 100.0,
    };
    return { obligations, conflicts, audit_log: auditLog, stats };
  })();

  const DEMO_EVAL = {
    metrics: {
      total_test_cases: 70,
      obligation_extraction_accuracy: 100.0,
      product_mapping_accuracy: 100.0,
      control_mapping_accuracy: 96.7,
      citation_coverage: 100.0,
      risk_level_accuracy: 100.0,
      escalation_accuracy: 100.0,
      perfect_domain_matches: 70,
      perfect_risk_matches: 70,
      perfect_escalation_matches: 70,
    },
  };

  window.ComplianceUI.DEMO_ANALYSIS = DEMO_ANALYSIS;
  window.ComplianceUI.DEMO_EVAL = DEMO_EVAL;
})();
