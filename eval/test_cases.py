"""
Eval Harness Test Cases — 70 regulatory snippets with expected mappings.

Each test case is a regulatory snippet with the expected:
  - Obligations to be extracted (by domain)
  - Product mappings
  - Control mappings
  - Risk level
  - Whether it should require human review
  - Whether a citation should be produced
  - Whether escalation should occur (and why)

This is the eval set that proves the system isn't hand-wavy.
"""

EVAL_TEST_CASES = [
    # ========================================
    # KYC / IDENTITY VERIFICATION (Cases 1-5)
    # ========================================
    {
        "id": "EVAL-001",
        "snippet": "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, it has sufficient information regarding the client's investment needs, objectives, financial circumstances, risk tolerance, investment knowledge, and investment time horizon.",
        "source": "CSA NI 31-103, Section 13.2",
        "expected": {
            "domains": ["KYC", "suitability"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_kyc_onboarding", "ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-002",
        "snippet": "Reporting entities must verify the identity of every person or entity for which they open an account. For individuals, this means verifying the person's name, date of birth, and address using reliable, independent source documents.",
        "source": "FINTRAC Guidelines, KYC Section",
        "expected": {
            "domains": ["KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-003",
        "snippet": "Verification must be completed before or within 30 days of the account opening.",
        "source": "FINTRAC Guidelines, KYC Section",
        "expected": {
            "domains": ["KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-004",
        "snippet": "A registered firm must deliver to a client all information that a reasonable investor would consider important about the client's relationship with the registrant, including the types of products and services offered.",
        "source": "CSA NI 31-103, Section 14.2",
        "expected": {
            "domains": ["relationship_disclosure"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": [],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-005",
        "snippet": "The client's risk tolerance must be assessed as part of the know your client process and updated whenever there is a material change in the client's circumstances.",
        "source": "CSA Companion Policy 31-103CP",
        "expected": {
            "domains": ["KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # AML / SUSPICIOUS ACTIVITY (Cases 6-10)
    # ========================================
    {
        "id": "EVAL-006",
        "snippet": "If a reporting entity has reasonable grounds to suspect that a transaction or attempted transaction is related to the commission of a money laundering offence, the entity must submit a Suspicious Transaction Report (STR) to FINTRAC within 30 calendar days.",
        "source": "FINTRAC Guidelines, STR Section",
        "expected": {
            "domains": ["AML"],
            "products": ["ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-007",
        "snippet": "Reporting entities must report to FINTRAC every international electronic funds transfer of $10,000 or more, whether sent or received, within 5 business days after the transfer.",
        "source": "FINTRAC Guidelines, EFT Section",
        "expected": {
            "domains": ["EFT_reporting"],
            "products": ["ws_cash", "ws_crypto"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-008",
        "snippet": "Reporting entities must make reasonable efforts to determine whether a client is a politically exposed foreign person, a politically exposed domestic person, or a head of an international organization.",
        "source": "FINTRAC Guidelines, PEP Section",
        "expected": {
            "domains": ["PEP_screening"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-009",
        "snippet": "Enhanced due diligence measures must be applied when dealing with politically exposed persons, including obtaining senior management approval for the business relationship.",
        "source": "FINTRAC Guidelines, PEP Section",
        "expected": {
            "domains": ["PEP_screening"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-010",
        "snippet": "A reporting entity must assess and document the risk of a money laundering or terrorist activity financing offence for each of its business relationships.",
        "source": "FINTRAC Guidelines, Risk Assessment Section",
        "expected": {
            "domains": ["AML", "risk_assessment"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening", "ctrl_kyc_onboarding"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # SUITABILITY / KYP (Cases 11-15)
    # ========================================
    {
        "id": "EVAL-011",
        "snippet": "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, the purchase or sale is suitable for the client.",
        "source": "CSA NI 31-103, Section 13.3",
        "expected": {
            "domains": ["suitability"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-012",
        "snippet": "A dealer member must take reasonable steps to understand the securities it recommends, including the structure, features, risks, initial and ongoing costs, and the impact of those costs on a client's return.",
        "source": "CIRO Dealer Member Rules, KYP Section",
        "expected": {
            "domains": ["KYP"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-013",
        "snippet": "A dealer member must not recommend a security to a client unless the dealer has a reasonable basis for concluding that the security is suitable for that client.",
        "source": "CIRO Dealer Member Rules, KYP Section",
        "expected": {
            "domains": ["KYP", "suitability"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-014",
        "snippet": "A dealer member must make reasonable efforts to achieve best execution when acting for a client, including obtaining the most advantageous execution terms reasonably available.",
        "source": "CIRO Universal Market Integrity Rules",
        "expected": {
            "domains": ["best_execution"],
            "products": ["ws_trade", "ws_options"],
            "controls": ["ctrl_best_execution"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-015",
        "snippet": "An investment fund must not purchase a security of an issuer if, immediately after the transaction, more than 10 percent of the net asset value would be invested in securities of any one issuer.",
        "source": "CSA NI 81-102, Section 2.1",
        "expected": {
            "domains": ["investment_restrictions"],
            "products": ["ws_invest"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # PRIVACY / DATA (Cases 16-20)
    # ========================================
    {
        "id": "EVAL-016",
        "snippet": "An organization must obtain meaningful consent for the collection, use, or disclosure of personal information. The form of consent must take into account the sensitivity of the information.",
        "source": "PIPEDA, Consent Section",
        "expected": {
            "domains": ["privacy"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-017",
        "snippet": "An organization must report to the Privacy Commissioner any breach of security safeguards involving personal information if it is reasonable to believe that the breach creates a real risk of significant harm.",
        "source": "PIPEDA, Breach Notification Section",
        "expected": {
            "domains": ["breach_notification"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-018",
        "snippet": "Personal information that is no longer required to fulfil the identified purposes should be destroyed, erased, or made anonymous.",
        "source": "PIPEDA, Data Retention Section",
        "expected": {
            "domains": ["data_retention"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "medium",
            "requires_human_review": False,
            "has_citation": True,
            "escalation_reasons": [],
        },
    },
    {
        "id": "EVAL-019",
        "snippet": "Organizations must develop guidelines and implement procedures for the retention and destruction of personal information, including minimum and maximum retention periods.",
        "source": "PIPEDA, Data Retention Section",
        "expected": {
            "domains": ["data_retention"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "medium",
            "requires_human_review": False,
            "has_citation": True,
            "escalation_reasons": [],
        },
    },
    {
        "id": "EVAL-020",
        "snippet": "Organizations must notify individuals of any material changes to their privacy practices and make their privacy practices available in a readily accessible form.",
        "source": "PIPEDA, Consent Section",
        "expected": {
            "domains": ["privacy"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # TAX / REPORTING (Cases 21-24)
    # ========================================
    {
        "id": "EVAL-021",
        "snippet": "Every person that makes a payment of investment income, including interest, dividends, or royalties, must file a T5 information return. The T5 slip must be issued to the recipient by the last day of February.",
        "source": "CRA Tax Filing Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-022",
        "snippet": "An issuer of a Tax-Free Savings Account must file an annual information return (RC243) with the CRA reporting all TFSA transactions. Failure to file can result in penalties of $25 per day.",
        "source": "CRA TFSA Reporting Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-023",
        "snippet": "The issuer must also report any excess TFSA contributions to the CRA.",
        "source": "CRA TFSA Reporting Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-024",
        "snippet": "A registered firm must deliver to a client all fees and charges associated with the client's account, and the dispute resolution process available to the client.",
        "source": "CSA NI 31-103, Section 14.2",
        "expected": {
            "domains": ["relationship_disclosure"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": [],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },

    # ========================================
    # COMPLIANCE FRAMEWORK (Cases 25-27)
    # ========================================
    {
        "id": "EVAL-025",
        "snippet": "A registered firm must establish, maintain and apply policies and procedures that establish a system of controls and supervision sufficient to provide reasonable assurance of compliance with securities legislation.",
        "source": "CSA NI 31-103, Section 11.1",
        "expected": {
            "domains": ["compliance_framework"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_compliance_testing"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-026",
        "snippet": "An institution must perform regular compliance testing to verify that policies, procedures, processes, and controls are operating effectively.",
        "source": "OSFI E-13, Compliance Testing Section",
        "expected": {
            "domains": ["compliance_testing"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_compliance_testing"],
            "risk_level": "medium",
            "requires_human_review": False,
            "has_citation": True,
            "escalation_reasons": [],
        },
    },
    {
        "id": "EVAL-027",
        "snippet": "Testing results must be reported to senior management and the board of directors, and any deficiencies identified must be remediated in a timely manner.",
        "source": "OSFI E-13, Compliance Testing Section",
        "expected": {
            "domains": ["compliance_testing"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_compliance_testing"],
            "risk_level": "medium",
            "requires_human_review": False,
            "has_citation": True,
            "escalation_reasons": [],
        },
    },

    # ========================================
    # COMPLAINT HANDLING / MISC (Cases 28-30)
    # ========================================
    {
        "id": "EVAL-028",
        "snippet": "Every complaint must be acknowledged in writing within 5 business days and a substantive response must be provided within 90 calendar days. The dealer must maintain records of all complaints for a minimum of 7 years.",
        "source": "CIRO Dealer Member Rules, Complaint Handling",
        "expected": {
            "domains": ["complaint_handling"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_complaint_system"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-029",
        "snippet": "The manager of an investment fund must not change the fundamental investment objectives unless the written consent of a majority of the securityholders has been obtained. Written notice must be sent at least 60 days before the effective date.",
        "source": "CSA NI 81-102, Section 5.1",
        "expected": {
            "domains": ["fundamental_changes"],
            "products": ["ws_invest"],
            "controls": [],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-030",
        "snippet": "A federally regulated financial institution must have a compliance risk management framework that includes policies and procedures to identify, assess, manage, monitor, and report on compliance risks.",
        "source": "OSFI E-13, Framework Section",
        "expected": {
            "domains": ["compliance_framework"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_compliance_testing"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # EDGE CASES — CRYPTO SPECIFIC (Cases 31-34)
    # ========================================
    {
        "id": "EVAL-031",
        "snippet": "A crypto asset trading platform must verify the identity of every client before enabling trading. Client identification must follow the same KYC procedures as traditional account opening.",
        "source": "CSA Staff Notice 21-327, KYC Section",
        "expected": {
            "domains": ["KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-032",
        "snippet": "A reporting entity that deals in virtual currency must submit a suspicious transaction report to FINTRAC for any virtual currency transaction related to money laundering or terrorist financing.",
        "source": "FINTRAC Virtual Currency Guidelines",
        "expected": {
            "domains": ["AML"],
            "products": ["ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-033",
        "snippet": "Enhanced due diligence must be applied to all virtual currency transactions involving a politically exposed person or a family member of a PEP. The platform must determine if the wallet owner is a PEP before processing.",
        "source": "FINTRAC Virtual Currency Guidelines",
        "expected": {
            "domains": ["PEP_screening"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-034",
        "snippet": "Prior to providing crypto trading services, the platform must verify the identity of the client and assess whether the product is suitable for the client based on the client's financial circumstances and risk tolerance.",
        "source": "CSA Staff Notice 21-327, Suitability Section",
        "expected": {
            "domains": ["suitability", "KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_suitability_engine", "ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # EDGE CASES — OPTIONS SPECIFIC (Cases 35-37)
    # ========================================
    {
        "id": "EVAL-035",
        "snippet": "A dealer must verify the identity of any client before opening an options account and determine that the purchase is suitable for the client based on the client's investment needs, risk tolerance, and financial circumstances.",
        "source": "CIRO Options Rules, Account Opening",
        "expected": {
            "domains": ["suitability", "KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_suitability_engine", "ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-036",
        "snippet": "A dealer member must perform best execution analysis quarterly for options orders, ensuring clients receive the most advantageous terms available under the circumstances.",
        "source": "CIRO Universal Market Integrity Rules, Options Section",
        "expected": {
            "domains": ["best_execution"],
            "products": ["ws_trade", "ws_options"],
            "controls": ["ctrl_best_execution"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-037",
        "snippet": "Concentration limits must be applied to options positions: no single account may hold options contracts representing more than 10 percent of the outstanding securities of any one issuer.",
        "source": "CIRO Options Rules, Position Limits",
        "expected": {
            "domains": ["investment_restrictions"],
            "products": ["ws_invest"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # EDGE CASES — MULTI-DOMAIN OVERLAP (Cases 38-40)
    # ========================================
    {
        "id": "EVAL-038",
        "snippet": "When onboarding a new client, the registrant must collect KYC information, verify identity per FINTRAC requirements, assess risk tolerance, determine suitability, and deliver the relationship disclosure document — all before accepting the first trade instruction.",
        "source": "CSA Companion Policy 31-103CP, Onboarding",
        "expected": {
            "domains": ["KYC", "suitability", "relationship_disclosure"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_kyc_onboarding", "ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-039",
        "snippet": "A reporting entity must assess and document the risk of money laundering for any cash receipt and must submit a suspicious transaction report when there are reasonable grounds to suspect suspicious activity.",
        "source": "FINTRAC Guidelines, Large Cash Transactions",
        "expected": {
            "domains": ["AML", "risk_assessment"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening", "ctrl_kyc_onboarding"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-040",
        "snippet": "Privacy consent must be obtained before collecting personal information for the purposes of KYC verification, and the client must be informed of all data retention and breach notification policies.",
        "source": "PIPEDA + FINTRAC Joint Guidance",
        "expected": {
            "domains": ["privacy", "KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework", "ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # EDGE CASES — BOUNDARY / ADVERSARIAL (Cases 41-45)
    # ========================================
    {
        "id": "EVAL-041",
        "snippet": "The dealer must maintain books and records for a minimum of 7 years from the date of the transaction, including all client communications related to complaints and dispute resolution.",
        "source": "CIRO Record-Keeping Rules",
        "expected": {
            "domains": ["complaint_handling"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_complaint_system"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-042",
        "snippet": "Every RRSP contribution must be reported on a T4RSP slip. The issuer must file the information return with the CRA by the last day of February following the calendar year in which the contribution was made.",
        "source": "CRA RRSP Reporting Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-043",
        "snippet": "An investment fund must not invest more than 10 percent of its net asset value in illiquid assets, and must immediately notify the securities regulatory authority if the fund's illiquid asset holdings exceed this threshold.",
        "source": "CSA NI 81-102, Section 2.4",
        "expected": {
            "domains": ["investment_restrictions"],
            "products": ["ws_invest"],
            "controls": ["ctrl_suitability_engine"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-044",
        "snippet": "Under PIPEDA, an organization must implement privacy safeguards appropriate to the sensitivity of personal information, and obtain consent before collecting or disclosing personal data.",
        "source": "PIPEDA, Safeguards Section",
        "expected": {
            "domains": ["privacy"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_privacy_framework"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-045",
        "snippet": "A registered firm must establish a compliance risk management framework including policies and procedures for controls and supervision of the compliance system and all registrant obligations.",
        "source": "CSA NI 31-103, Section 11.3",
        "expected": {
            "domains": ["compliance_framework"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_compliance_testing"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # EDGE CASES — TAX EDGE CASES (Cases 46-48)
    # ========================================
    {
        "id": "EVAL-046",
        "snippet": "A financial institution must issue a T3 slip for trust income distributed to beneficiaries and file the T3 return within 90 days of the trust's tax year end.",
        "source": "CRA Trust Reporting Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-047",
        "snippet": "The issuer must perform ongoing monitoring of TFSA contribution room and must notify the CRA of any excess contributions within 30 days of the over-contribution being identified.",
        "source": "CRA TFSA Monitoring Requirements",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-048",
        "snippet": "Capital gains and losses from the disposition of securities must be reported on the client's T5008 slip. The dealer must issue the T5008 by the last day of February following the taxation year.",
        "source": "CRA Securities Disposition Reporting",
        "expected": {
            "domains": ["tax_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_tax"],
            "controls": ["ctrl_tax_reporting"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # EDGE CASES — RARE PATHS (Cases 49-50)
    # ========================================
    {
        "id": "EVAL-049",
        "snippet": "If a reporting entity has reasonable grounds to suspect that a transaction is related to terrorist financing or money laundering by a sanctioned entity, it must immediately freeze all property and submit a suspicious transaction report to FINTRAC.",
        "source": "FINTRAC Sanctions Compliance",
        "expected": {
            "domains": ["AML"],
            "products": ["ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-050",
        "snippet": "The fund manager must not change the fundamental investment objectives of the fund without first obtaining the written consent of a majority of the securityholders, and must notify securityholders at least 60 days before any such change.",
        "source": "CSA NI 81-106, Reporting Section",
        "expected": {
            "domains": ["fundamental_changes"],
            "products": ["ws_invest"],
            "controls": [],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # RECORD KEEPING (Cases 51-53)
    # ========================================
    {
        "id": "EVAL-051",
        "snippet": "A registered firm must maintain books and records necessary to demonstrate compliance with securities legislation. These records must be retained for a minimum of 7 years from the date of the last entry.",
        "source": "CSA NI 31-103, Section 11.5",
        "expected": {
            "domains": ["record_keeping"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_record_keeping"],
            "risk_level": "medium",
            "requires_human_review": False,
            "has_citation": True,
            "escalation_reasons": [],
        },
    },
    {
        "id": "EVAL-052",
        "snippet": "Reporting entities must maintain books and records of all transactions, client identification, and compliance activities for a minimum of 5 years.",
        "source": "FINTRAC Record Keeping Guidelines",
        "expected": {
            "domains": ["record_keeping", "KYC"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_options"],
            "controls": ["ctrl_record_keeping", "ctrl_kyc_onboarding"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-053",
        "snippet": "The dealer must maintain records of all client account documentation, communications, and trade confirmations for the applicable retention period as prescribed by the regulator.",
        "source": "CIRO Record-Keeping Rules",
        "expected": {
            "domains": ["record_keeping"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_record_keeping"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },

    # ========================================
    # CAPITAL REQUIREMENTS (Cases 54-55)
    # ========================================
    {
        "id": "EVAL-054",
        "snippet": "A registered dealer must maintain minimum capital at all times, calculated using the risk-adjusted capital formula. Working capital must be sufficient to meet obligations as they come due.",
        "source": "CSA NI 31-103, Section 12.1",
        "expected": {
            "domains": ["capital_requirements"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_capital_monitoring"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-055",
        "snippet": "A federally regulated deposit-taking institution must maintain capital adequacy ratios that meet or exceed the minimum requirements prescribed by OSFI, reflecting credit risk, market risk, and operational risk.",
        "source": "OSFI Guideline A-1, Capital Adequacy",
        "expected": {
            "domains": ["capital_requirements"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_capital_monitoring"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # OUTSOURCING / THIRD-PARTY RISK (Cases 56-58)
    # ========================================
    {
        "id": "EVAL-056",
        "snippet": "A registered firm that outsources a material business activity to a third-party service provider must establish written policies to manage the risks associated with the outsourcing arrangement.",
        "source": "CSA NI 31-103, Section 11.6",
        "expected": {
            "domains": ["outsourcing"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_vendor_risk"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-057",
        "snippet": "A financial institution that enters into a material outsourcing arrangement must ensure that the arrangement does not diminish the institution's ability to meet its obligations. The institution must maintain oversight of the service provider.",
        "source": "OSFI B-10, Third-Party Risk Management",
        "expected": {
            "domains": ["outsourcing"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_vendor_risk"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-058",
        "snippet": "An organization that transfers personal information to a third-party service provider in another jurisdiction must ensure a comparable level of privacy protection is maintained by contractual means.",
        "source": "PIPEDA, Cross-Border Transfers",
        "expected": {
            "domains": ["outsourcing", "privacy"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash", "ws_tax"],
            "controls": ["ctrl_vendor_risk", "ctrl_privacy_framework"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # MARGIN REQUIREMENTS (Cases 59-60)
    # ========================================
    {
        "id": "EVAL-059",
        "snippet": "A dealer member must establish margin requirements for client accounts. Margin call notices must be issued promptly when a client's equity falls below the required margin level.",
        "source": "CIRO Margin Rules",
        "expected": {
            "domains": ["margin_requirements"],
            "products": ["ws_trade", "ws_options"],
            "controls": ["ctrl_margin_system"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-060",
        "snippet": "Leverage through derivatives must be fully covered by liquid assets. Margin requirements must be met at all times for options and futures positions.",
        "source": "CSA NI 81-102, Section 2.6",
        "expected": {
            "domains": ["margin_requirements"],
            "products": ["ws_trade", "ws_options"],
            "controls": ["ctrl_margin_system"],
            "risk_level": "high",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # CRYPTO CUSTODY (Cases 61-62)
    # ========================================
    {
        "id": "EVAL-061",
        "snippet": "A registered crypto asset trading platform must implement appropriate safekeeping arrangements for the crypto custody of client assets, including the use of cold storage for the majority of client holdings.",
        "source": "CSA Staff Notice 21-327, Custody Section",
        "expected": {
            "domains": ["crypto_custody"],
            "products": ["ws_crypto"],
            "controls": ["ctrl_crypto_custody"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-062",
        "snippet": "Segregation of client crypto assets from the platform's own assets is mandatory. Regular third-party audits of wallet security and crypto custody controls must be conducted.",
        "source": "CSA Staff Notice 21-327, Custody Section",
        "expected": {
            "domains": ["crypto_custody"],
            "products": ["ws_crypto"],
            "controls": ["ctrl_crypto_custody"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },

    # ========================================
    # SANCTIONS (Cases 63-64)
    # ========================================
    {
        "id": "EVAL-063",
        "snippet": "A reporting entity must verify that none of its clients are designated persons under Canadian sanctions legislation. If property of a sanctioned entity is identified, it must be immediately frozen and reported to the RCMP.",
        "source": "FINTRAC Sanctions Compliance",
        "expected": {
            "domains": ["sanctions"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_sanctions_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk", "customer_facing_change"],
        },
    },
    {
        "id": "EVAL-064",
        "snippet": "Sanctions screening must be performed at onboarding and on an ongoing basis. Any transaction involving a listed entity or designated person must be immediately blocked and reported.",
        "source": "FINTRAC Sanctions Compliance",
        "expected": {
            "domains": ["sanctions"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_sanctions_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },

    # ========================================
    # CLIENT REPORTING (Cases 65-66)
    # ========================================
    {
        "id": "EVAL-065",
        "snippet": "A registered dealer must deliver a quarterly account statement to each client showing all positions, transactions, market value, and fees. An annual performance report must also be delivered.",
        "source": "CSA NI 31-103, Section 14.14",
        "expected": {
            "domains": ["client_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_complaint_system"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-066",
        "snippet": "A dealer member must send to each client a quarterly report showing all positions held, transactions executed, and the client's cash balance within 10 business days after each quarter.",
        "source": "CIRO Client Statement Rules",
        "expected": {
            "domains": ["client_reporting"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": ["ctrl_complaint_system"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },

    # ========================================
    # CONSUMER PROTECTION — FCAC (Cases 67-68)
    # ========================================
    {
        "id": "EVAL-067",
        "snippet": "A federally regulated financial institution must provide clear disclosure of all fees, charges, penalties, and interest rates. This information must be delivered to the client in plain language before the product is purchased.",
        "source": "FCAC Consumer Protection Framework",
        "expected": {
            "domains": ["relationship_disclosure"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": [],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
    {
        "id": "EVAL-068",
        "snippet": "If a complaint is not resolved to the client's satisfaction within 56 calendar days, the institution must inform the client of their right to escalate the complaint to an external complaints body.",
        "source": "FCAC Complaint Resolution Procedures",
        "expected": {
            "domains": ["complaint_handling"],
            "products": ["ws_invest", "ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_complaint_system"],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },

    # ========================================
    # CROSS-CUTTING EDGE CASES (Cases 69-70)
    # ========================================
    {
        "id": "EVAL-069",
        "snippet": "A crypto platform must implement robust AML controls including transaction monitoring for suspicious activity across blockchain networks. Any transaction involving a money laundering indicator must trigger a suspicious transaction report.",
        "source": "CSA Staff Notice 21-327, AML Section",
        "expected": {
            "domains": ["AML"],
            "products": ["ws_trade", "ws_crypto", "ws_cash"],
            "controls": ["ctrl_aml_screening"],
            "risk_level": "critical",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["high_risk"],
        },
    },
    {
        "id": "EVAL-070",
        "snippet": "Before opening an options trading account, the dealer must deliver a risk disclosure document to the client describing the characteristics and risks of options. The client must acknowledge receipt before any trades.",
        "source": "CIRO Options Rules, Disclosure Section",
        "expected": {
            "domains": ["relationship_disclosure"],
            "products": ["ws_invest", "ws_trade", "ws_options"],
            "controls": [],
            "risk_level": "medium",
            "requires_human_review": True,
            "has_citation": True,
            "escalation_reasons": ["customer_facing_change"],
        },
    },
]
