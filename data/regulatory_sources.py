"""
Simulated regulatory sources for the compliance monitoring system.
These represent real Canadian financial regulatory documents that
Wealthsimple must comply with.
"""

# -------------------------------------------------------------------
# REGULATORY SOURCE DOCUMENTS
# Each source has: id, title, issuer, sections with text
# -------------------------------------------------------------------

REGULATORY_SOURCES = [
    {
        "id": "CSA_31-103",
        "title": "National Instrument 31-103 — Registration Requirements, Exemptions and Ongoing Registrant Obligations",
        "issuer": "Canadian Securities Administrators (CSA)",
        "url": "https://www.osc.ca/en/securities-law/instruments-rules-policies/3/31-103",
        "sections": [
            {
                "section_id": "31-103-s13.2",
                "section_title": "Know Your Client (KYC)",
                "text": "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, it has sufficient information regarding the client's investment needs, objectives, financial circumstances, risk tolerance, investment knowledge, and investment time horizon to enable the registrant to determine suitability."
            },
            {
                "section_id": "31-103-s13.3",
                "section_title": "Suitability Determination",
                "text": "A registrant must take reasonable steps to ensure that, before it makes a recommendation to or accepts an instruction from a client to buy or sell a security, the purchase or sale is suitable for the client. In making this determination, the registrant must consider the client's KYC information, the characteristics of the security, and the impact of the transaction on the client's account."
            },
            {
                "section_id": "31-103-s14.2",
                "section_title": "Relationship Disclosure Information",
                "text": "A registered firm must deliver to a client all information that a reasonable investor would consider important about the client's relationship with the registrant, including the types of products and services offered, all fees and charges, the registrant's obligations to the client, and the dispute resolution process."
            },
            {
                "section_id": "31-103-s11.1",
                "section_title": "Compliance System",
                "text": "A registered firm must establish, maintain and apply policies and procedures that establish a system of controls and supervision sufficient to provide reasonable assurance that the firm and each individual acting on its behalf complies with securities legislation, and manage the risks associated with its business in conformity with prudent business practices."
            },
            {
                "section_id": "31-103-s13.2.1",
                "section_title": "KYC Ongoing Updates",
                "text": "The client's risk tolerance and financial circumstances must be assessed as part of the know your client process and updated whenever there is a material change in the client's circumstances. The registrant must verify the identity of the client annually."
            },
            {
                "section_id": "31-103-s11.3",
                "section_title": "Chief Compliance Officer",
                "text": "A registered firm must establish a compliance risk management framework including policies and procedures for controls and supervision. The Chief Compliance Officer must monitor the compliance system and report to the board of directors on the firm's compliance with securities legislation."
            },
            {
                "section_id": "31-103-s11.5",
                "section_title": "Record Keeping",
                "text": "A registered firm must maintain books and records necessary to demonstrate compliance with securities legislation, including records of all client transactions, account documentation, and communications related to investment recommendations. These records must be retained for a minimum of 7 years from the date of the transaction or the date of the last entry."
            },
            {
                "section_id": "31-103-s12.1",
                "section_title": "Capital Requirements",
                "text": "A registered dealer must maintain minimum capital at all times, calculated in accordance with the capital formula prescribed by the securities regulatory authority. The working capital must be sufficient to meet its obligations as they come due and must be reported to the regulator on a monthly basis."
            },
            {
                "section_id": "31-103-s11.6",
                "section_title": "Outsourcing Arrangements",
                "text": "A registered firm that outsources a material business activity to a third-party service provider must establish and maintain written policies and procedures to manage the risks associated with the outsourcing arrangement. The firm remains responsible for compliance with securities legislation regardless of any outsourcing."
            },
            {
                "section_id": "31-103-s14.14",
                "section_title": "Account Statements and Performance Reports",
                "text": "A registered dealer must deliver a quarterly account statement to each client showing all positions, transactions during the period, market value of holdings, and any fees charged. An annual performance report must also be delivered showing total return, change in account value, and cumulative fees paid by the client."
            },
        ],
    },
    {
        "id": "FINTRAC_PCMLTFA",
        "title": "Proceeds of Crime (Money Laundering) and Terrorist Financing Act — FINTRAC Guidelines",
        "issuer": "Financial Transactions and Reports Analysis Centre of Canada (FINTRAC)",
        "url": "https://www.fintrac-canafe.gc.ca/guidance-directives/overview-apercu/1-eng",
        "sections": [
            {
                "section_id": "FINTRAC-KYC-1",
                "section_title": "Client Identification Requirements",
                "text": "Reporting entities must verify the identity of every person or entity for which they open an account. For individuals, this means verifying the person's name, date of birth, and address using reliable, independent source documents, data, or information. Verification must be completed before or within 30 days of the account opening."
            },
            {
                "section_id": "FINTRAC-STR-1",
                "section_title": "Suspicious Transaction Reporting",
                "text": "If a reporting entity has reasonable grounds to suspect that a transaction or attempted transaction is related to the commission of a money laundering offence or a terrorist activity financing offence, the entity must submit a Suspicious Transaction Report (STR) to FINTRAC within 30 calendar days of the detection of the suspicious activity."
            },
            {
                "section_id": "FINTRAC-EFT-1",
                "section_title": "Electronic Funds Transfer Reporting",
                "text": "Reporting entities must report to FINTRAC every international electronic funds transfer of $10,000 or more, whether sent or received, within 5 business days after the transfer. The report must include the ordering client's name, address, date of birth, the beneficiary's name and address, and the purpose of the transfer."
            },
            {
                "section_id": "FINTRAC-RK-1",
                "section_title": "Risk Assessment",
                "text": "A reporting entity must assess and document the risk of a money laundering or terrorist activity financing offence for each of its business relationships, taking into account the purpose and intended nature of the relationship, the client's activity patterns, the geographic location of the client's activities, and any other relevant factors."
            },
            {
                "section_id": "FINTRAC-PEP-1",
                "section_title": "Politically Exposed Persons",
                "text": "Reporting entities must make reasonable efforts to determine whether a client is a politically exposed foreign person, a politically exposed domestic person, a head of an international organization, or a family member or close associate of any of these persons. Enhanced due diligence measures must be applied when dealing with such persons, including obtaining senior management approval for the business relationship."
            },
            {
                "section_id": "FINTRAC-LCTR-1",
                "section_title": "Large Cash Transaction Reporting",
                "text": "A reporting entity must report to FINTRAC every large cash transaction involving the receipt of $10,000 or more in cash in a single transaction. The report must be filed within 15 calendar days of the transaction and include the identity of the person conducting the transaction, the amount, and the purpose."
            },
            {
                "section_id": "FINTRAC-SANC-1",
                "section_title": "Sanctions Compliance",
                "text": "A reporting entity must verify that none of its clients or their beneficial owners are designated persons under Canadian sanctions legislation. If a reporting entity identifies property in its possession or control that is owned by a sanctioned or listed entity, it must immediately freeze the property and report it to the RCMP and CSIS. Sanctions screening must be performed at onboarding and on an ongoing basis."
            },
            {
                "section_id": "FINTRAC-RK-2",
                "section_title": "Record Keeping Requirements",
                "text": "Reporting entities must maintain books and records of all transactions, client identification, and compliance activities. All records related to client due diligence, transaction monitoring, and suspicious transaction reports must be retained for a minimum of 5 years from the date of the last transaction or activity."
            },
            {
                "section_id": "FINTRAC-TRV-1",
                "section_title": "Travel Rule — Wire Transfer Requirements",
                "text": "For every international electronic funds transfer of $1,000 or more, the originating financial institution must include the sender's name, address, account number, and a unique identifier. The receiving institution must verify the completeness of this information and report any deficiencies to FINTRAC."
            },
        ],
    },
    {
        "id": "CSA_NI_81-102",
        "title": "National Instrument 81-102 — Investment Funds",
        "issuer": "Canadian Securities Administrators (CSA)",
        "url": "https://www.osc.ca/en/securities-law/instruments-rules-policies/8/81-102",
        "sections": [
            {
                "section_id": "81-102-s2.1",
                "section_title": "Investment Restrictions",
                "text": "An investment fund must not purchase a security of an issuer, enter into a specified derivatives transaction, or purchase index participation units if, immediately after the transaction, more than 10 percent of the net asset value of the investment fund would be invested in securities of any one issuer."
            },
            {
                "section_id": "81-102-s5.1",
                "section_title": "Fundamental Changes",
                "text": "The manager of an investment fund must not change the fundamental investment objectives of the investment fund unless the written consent of a majority of the securityholders of the investment fund has been obtained. The manager must send a written notice to the securityholders at least 60 days before the effective date of the change."
            },
            {
                "section_id": "81-102-s2.6",
                "section_title": "Borrowing and Leverage Restrictions",
                "text": "An investment fund must not borrow cash or provide a security interest over its portfolio assets except for temporary purposes and in an amount not exceeding 5 percent of its net asset value. Margin requirements must be met at all times. Leverage through derivatives must be fully covered by liquid assets."
            },
            {
                "section_id": "81-102-s6.1",
                "section_title": "Custodian Requirements",
                "text": "An investment fund must appoint a custodian that is a bank listed in Schedule I, II, or III of the Bank Act, or a trust company. The custodian must hold all portfolio assets of the fund in safekeeping and must not commingle fund assets with its own assets or those of other clients."
            },
            {
                "section_id": "81-102-s3.2",
                "section_title": "Prohibited Investments",
                "text": "An investment fund must not knowingly make or hold an investment in an issuer in which any officer, director, or substantial securityholder of the fund manager has a significant interest, unless the investment is made at fair market value and proper disclosure is provided to securityholders in the fund's quarterly report."
            },
        ],
    },
    {
        "id": "IIROC_RULES_2025",
        "title": "CIRO (formerly IIROC) — Universal Market Integrity Rules and Dealer Member Rules",
        "issuer": "Canadian Investment Regulatory Organization (CIRO)",
        "url": "https://www.ciro.ca/office/rules",
        "sections": [
            {
                "section_id": "CIRO-KYP-1",
                "section_title": "Know Your Product (KYP)",
                "text": "A dealer member must take reasonable steps to understand the securities it recommends, including the structure, features, risks, initial and ongoing costs, and the impact of those costs on a client's return. A dealer member must not recommend a security to a client unless the dealer has a reasonable basis for concluding that the security is suitable for that client."
            },
            {
                "section_id": "CIRO-BESTEX-1",
                "section_title": "Best Execution Obligation",
                "text": "A dealer member must make reasonable efforts to achieve best execution when acting for a client. Best execution means obtaining the most advantageous execution terms reasonably available under the circumstances, including price, speed, certainty of execution, and the overall cost of the transaction."
            },
            {
                "section_id": "CIRO-COMP-1",
                "section_title": "Complaint Handling",
                "text": "A dealer member must establish and maintain written policies and procedures for dealing with complaints from clients. Every complaint must be acknowledged in writing within 5 business days and a substantive response must be provided within 90 calendar days. The dealer must maintain records of all complaints for a minimum of 7 years."
            },
            {
                "section_id": "CIRO-MARG-1",
                "section_title": "Margin Requirements",
                "text": "A dealer member must establish margin requirements for client accounts in accordance with CIRO rules. Margin call notices must be issued promptly when a client's equity falls below the required margin level. If the margin deficiency is not corrected within the prescribed time, the dealer must liquidate sufficient positions to restore compliance."
            },
            {
                "section_id": "CIRO-SUPV-1",
                "section_title": "Trade Supervision and Review",
                "text": "A dealer member must establish a system of controls and supervision to ensure that all trading activity is reviewed for compliance with applicable rules. The compliance system must include pre-trade and post-trade surveillance, pattern detection for potential market manipulation, and escalation procedures for unusual activity."
            },
            {
                "section_id": "CIRO-STMT-1",
                "section_title": "Client Account Statements",
                "text": "A dealer member must send to each client a quarterly account statement showing all positions held, transactions executed during the period, market value of securities, any fees and charges, and the client's cash balance. The statement must be delivered within 10 business days after the end of each quarter."
            },
            {
                "section_id": "CIRO-CAP-1",
                "section_title": "Minimum Capital and Insurance",
                "text": "A dealer member must maintain minimum capital as prescribed by CIRO, calculated using the risk-adjusted capital formula. Capital adequacy must be reported monthly. The dealer must also maintain adequate insurance coverage, including fidelity bonding and errors and omissions insurance, to protect client assets."
            },
        ],
    },
    {
        "id": "OSFI_E13",
        "title": "OSFI Guideline E-13 — Legislative Compliance Management",
        "issuer": "Office of the Superintendent of Financial Institutions (OSFI)",
        "url": "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/legislative-compliance-management-guideline",
        "sections": [
            {
                "section_id": "OSFI-E13-s1",
                "section_title": "Compliance Risk Management Framework",
                "text": "A federally regulated financial institution must have a compliance risk management framework that includes policies and procedures to identify, assess, manage, monitor, and report on compliance risks. The framework must be proportionate to the nature, size, complexity, and risk profile of the institution."
            },
            {
                "section_id": "OSFI-E13-s3",
                "section_title": "Compliance Testing and Monitoring",
                "text": "An institution must perform regular compliance testing to verify that policies, procedures, processes, and controls are operating effectively. Testing results must be reported to senior management and the board of directors, and any deficiencies identified must be remediated in a timely manner."
            },
            {
                "section_id": "OSFI-B10-s1",
                "section_title": "Third-Party Risk Management (Outsourcing)",
                "text": "A federally regulated financial institution that enters into a material outsourcing arrangement with a third-party service provider must ensure that the arrangement does not diminish the institution's ability to meet its obligations to depositors, policyholders, and other stakeholders. The institution must maintain oversight of the service provider and conduct regular assessments of the outsourcing risks."
            },
            {
                "section_id": "OSFI-A1-s1",
                "section_title": "Capital Adequacy Requirements",
                "text": "A federally regulated deposit-taking institution must maintain capital adequacy ratios that meet or exceed the minimum requirements prescribed by OSFI. The institution's capital requirements must reflect the nature and extent of risks to which it is exposed, including credit risk, market risk, and operational risk."
            },
            {
                "section_id": "OSFI-E21-s1",
                "section_title": "Operational Resilience",
                "text": "A financial institution must identify its critical operations and ensure they can withstand, adapt to, and recover from operational disruptions. The institution must establish policies and procedures for the compliance system to manage operational risk, including technology failures, cyber incidents, and third-party outages."
            },
        ],
    },
    {
        "id": "CRA_TAX_2025",
        "title": "Canada Revenue Agency — Tax Filing and Reporting Requirements for Financial Institutions",
        "issuer": "Canada Revenue Agency (CRA)",
        "url": "https://www.canada.ca/en/revenue-agency.html",
        "sections": [
            {
                "section_id": "CRA-T5-1",
                "section_title": "T5 Slip Reporting",
                "text": "Every person or partnership that makes a payment of investment income, including interest, dividends, or royalties, to a resident of Canada must file a T5 information return. The T5 slip must be issued to the recipient by the last day of February of the year following the calendar year in which the payment was made."
            },
            {
                "section_id": "CRA-TFSA-1",
                "section_title": "TFSA Contribution Limits and Reporting",
                "text": "An issuer of a Tax-Free Savings Account must file an annual information return (RC243) with the CRA reporting all TFSA transactions, including contributions, withdrawals, and transfers. The issuer must also report any excess TFSA contributions. Failure to file these returns can result in penalties of $25 per day for each day the return is late, to a maximum of $2,500."
            },
            {
                "section_id": "CRA-RRSP-1",
                "section_title": "RRSP Reporting Requirements",
                "text": "An issuer of a Registered Retirement Savings Plan must file an annual information return (T4RSP) with the CRA reporting all RRSP contributions, withdrawals, and transfers. The T4RSP slip must be issued to the recipient by the last day of February of the following year. The tax implications of early withdrawals must be clearly disclosed to the client."
            },
            {
                "section_id": "CRA-T5008-1",
                "section_title": "Securities Disposition Reporting",
                "text": "Every dealer that processes the disposition of securities must file a T5008 information return with the CRA. The T5008 slip must report the proceeds of disposition, the cost basis if known, and the date of the transaction. The slip must be issued by the last day of February following the tax year."
            },
            {
                "section_id": "CRA-T1135-1",
                "section_title": "Foreign Property Reporting",
                "text": "A financial institution that holds specified foreign property with a total cost exceeding $100,000 on behalf of a client must ensure the client is informed of the obligation to file Form T1135, Foreign Income Verification Statement, with the CRA. The institution must maintain records sufficient to assist clients in meeting this tax reporting obligation."
            },
        ],
    },
    {
        "id": "PRIVACY_PIPEDA",
        "title": "Personal Information Protection and Electronic Documents Act (PIPEDA)",
        "issuer": "Office of the Privacy Commissioner of Canada",
        "url": "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/",
        "sections": [
            {
                "section_id": "PIPEDA-CONSENT-1",
                "section_title": "Consent Requirements",
                "text": "An organization must obtain meaningful consent for the collection, use, or disclosure of personal information. The form of consent must take into account the sensitivity of the information. Organizations must make their privacy practices available in a readily accessible form, and must notify individuals of any material changes to their privacy practices."
            },
            {
                "section_id": "PIPEDA-BREACH-1",
                "section_title": "Breach of Security Safeguards",
                "text": "An organization must report to the Privacy Commissioner any breach of security safeguards involving personal information under its control if it is reasonable in the circumstances to believe that the breach creates a real risk of significant harm to an individual. Notification must be given as soon as feasible after the organization determines that the breach has occurred."
            },
            {
                "section_id": "PIPEDA-RETENTION-1",
                "section_title": "Data Retention and Disposal",
                "text": "Personal information that is no longer required to fulfil the identified purposes should be destroyed, erased, or made anonymous. Organizations must develop guidelines and implement procedures for the retention and destruction of personal information, and these guidelines must include minimum and maximum retention periods."
            },
            {
                "section_id": "PIPEDA-ACCESS-1",
                "section_title": "Individual Access Rights",
                "text": "An organization must, upon request, inform an individual of the existence, use, and disclosure of their personal information, and give the individual access to that information. The organization must respond to the access request within 30 days and must provide the information at minimal or no cost to the individual."
            },
            {
                "section_id": "PIPEDA-CROSSBORDER-1",
                "section_title": "Cross-Border Data Transfers",
                "text": "An organization that transfers personal information to a third-party service provider in another jurisdiction must ensure by contractual or other means that a comparable level of privacy protection is maintained. The organization must notify individuals that their personal information may be processed outside of Canada and may be subject to the laws of the foreign jurisdiction."
            },
        ],
    },
    # -------------------------------------------------------------------
    # NEW SOURCE: CSA Staff Notice 21-327 — Crypto Asset Trading Platforms
    # -------------------------------------------------------------------
    {
        "id": "CSA_SN_21_327",
        "title": "CSA Staff Notice 21-327 — Guidance on the Application of Securities Legislation to Entities Facilitating the Trading of Crypto Assets",
        "issuer": "Canadian Securities Administrators (CSA)",
        "url": "https://www.osc.ca/en/securities-law/instruments-rules-policies/2/21-327",
        "sections": [
            {
                "section_id": "SN21-327-s1",
                "section_title": "Crypto Asset Platform Registration",
                "text": "A platform that facilitates the trading of crypto assets must determine whether the crypto assets being traded constitute securities or derivatives under Canadian securities legislation. If so, the platform must register as a dealer and comply with all applicable KYC, suitability, and compliance system requirements."
            },
            {
                "section_id": "SN21-327-s2",
                "section_title": "Crypto Custody and Safekeeping",
                "text": "A registered crypto asset trading platform must implement appropriate safekeeping arrangements for the crypto custody of client assets. This includes the use of cold storage for the majority of client crypto assets, segregation of client assets from the platform's own assets, and regular third-party audits of wallet security and crypto custody controls."
            },
            {
                "section_id": "SN21-327-s3",
                "section_title": "Crypto Suitability and Risk Disclosure",
                "text": "Before enabling a client to trade in crypto assets, the platform must assess whether the specific crypto assets are suitable for the client based on the client's investment needs, risk tolerance, and financial circumstances. Clear risk disclosures must be provided to the client regarding the volatility, liquidity risks, and regulatory uncertainty associated with crypto assets."
            },
            {
                "section_id": "SN21-327-s4",
                "section_title": "Crypto AML and Transaction Monitoring",
                "text": "Crypto asset trading platforms must implement robust AML controls including transaction monitoring for suspicious activity across blockchain networks. Any transaction involving a money laundering or terrorist financing indicator must trigger a suspicious transaction report to FINTRAC within 30 days."
            },
        ],
    },
    # -------------------------------------------------------------------
    # NEW SOURCE: CIRO Options Trading Rules
    # -------------------------------------------------------------------
    {
        "id": "CIRO_OPTIONS",
        "title": "CIRO Rules — Options Trading Requirements",
        "issuer": "Canadian Investment Regulatory Organization (CIRO)",
        "url": "https://www.ciro.ca/office/rules/options",
        "sections": [
            {
                "section_id": "CIRO-OPT-s1",
                "section_title": "Options Account Approval",
                "text": "A dealer member must obtain approval from a designated supervisor before opening an options account for a client. The supervisor must assess the client's investment knowledge, trading experience, risk tolerance, and financial circumstances to determine whether options trading is suitable for the client."
            },
            {
                "section_id": "CIRO-OPT-s2",
                "section_title": "Options Margin and Risk Management",
                "text": "A dealer member must establish and enforce margin requirements for all options positions. Margin call notices must be issued immediately when a client's account equity falls below the required margin level for options positions. Uncovered options writing requires enhanced margin and must be approved by senior management."
            },
            {
                "section_id": "CIRO-OPT-s3",
                "section_title": "Options Risk Disclosure Document",
                "text": "Before opening an options trading account, the dealer must deliver to the client a risk disclosure document describing the characteristics and risks of options trading. The client must acknowledge receipt of the disclosure document before any options trades are executed."
            },
        ],
    },
    # -------------------------------------------------------------------
    # NEW SOURCE: FCAC — Financial Consumer Agency of Canada
    # -------------------------------------------------------------------
    {
        "id": "FCAC_CONSUMER",
        "title": "Financial Consumer Agency of Canada — Consumer Protection Framework",
        "issuer": "Financial Consumer Agency of Canada (FCAC)",
        "url": "https://www.canada.ca/en/financial-consumer-agency.html",
        "sections": [
            {
                "section_id": "FCAC-DISC-1",
                "section_title": "Fee and Cost Disclosure",
                "text": "A federally regulated financial institution must provide clear, timely, and comprehensive disclosure of all fees, charges, penalties, and interest rates associated with its products and services. This information must be delivered to the client in plain language before the product is purchased and whenever the terms are changed."
            },
            {
                "section_id": "FCAC-COMPRES-1",
                "section_title": "Complaint Resolution Procedures",
                "text": "A federally regulated financial institution must establish internal procedures for resolving complaints from clients. If a complaint is not resolved to the client's satisfaction within 56 calendar days, the institution must inform the client of their right to escalate the complaint to an approved external complaints body."
            },
            {
                "section_id": "FCAC-ACCESS-1",
                "section_title": "Accessibility and Inclusion",
                "text": "Financial services must be accessible to persons with disabilities. The institution must provide services in accessible formats and must ensure that its digital platforms, including websites and mobile applications, comply with the Canadian accessibility standards and privacy practices for digital services."
            },
        ],
    },
]


# -------------------------------------------------------------------
# WEALTHSIMPLE PRODUCT MAPPINGS
# Maps regulatory obligations to specific Wealthsimple products
# -------------------------------------------------------------------

WEALTHSIMPLE_PRODUCTS = {
    "ws_invest": {
        "name": "Wealthsimple Invest",
        "description": "Managed investing / robo-advisor",
        "regulatory_domains": ["KYC", "suitability", "investment_restrictions", "KYP", "reporting"],
    },
    "ws_trade": {
        "name": "Wealthsimple Trade",
        "description": "Self-directed trading platform",
        "regulatory_domains": ["KYC", "best_execution", "KYP", "complaint_handling", "reporting"],
    },
    "ws_crypto": {
        "name": "Wealthsimple Crypto",
        "description": "Cryptocurrency trading",
        "regulatory_domains": ["KYC", "AML", "reporting", "risk_assessment"],
    },
    "ws_tax": {
        "name": "Wealthsimple Tax",
        "description": "Tax filing platform",
        "regulatory_domains": ["T5_reporting", "TFSA_reporting", "privacy", "data_retention"],
    },
    "ws_cash": {
        "name": "Wealthsimple Cash",
        "description": "Banking / savings / chequing",
        "regulatory_domains": ["KYC", "AML", "EFT_reporting", "privacy", "PEP_screening"],
    },
    "ws_options": {
        "name": "Wealthsimple Options",
        "description": "Options trading",
        "regulatory_domains": ["KYC", "suitability", "best_execution", "KYP", "risk_assessment"],
    },
}


# -------------------------------------------------------------------
# EXISTING CONTROLS (what Wealthsimple already has in place)
# -------------------------------------------------------------------

EXISTING_CONTROLS = {
    "ctrl_kyc_onboarding": {
        "name": "KYC Onboarding Flow",
        "description": "Identity verification and risk profiling during account opening",
        "covers": ["KYC", "identity_verification", "risk_assessment"],
    },
    "ctrl_aml_screening": {
        "name": "AML Transaction Monitoring",
        "description": "Automated monitoring of transactions for suspicious activity",
        "covers": ["AML", "STR_reporting", "PEP_screening"],
    },
    "ctrl_suitability_engine": {
        "name": "Suitability Assessment Engine",
        "description": "Automated suitability checks for investment recommendations",
        "covers": ["suitability", "KYP"],
    },
    "ctrl_best_execution": {
        "name": "Best Execution Monitoring",
        "description": "Order routing and execution quality monitoring",
        "covers": ["best_execution"],
    },
    "ctrl_complaint_system": {
        "name": "Client Complaint Management System",
        "description": "Intake, tracking, and resolution of client complaints",
        "covers": ["complaint_handling"],
    },
    "ctrl_privacy_framework": {
        "name": "Privacy and Data Protection Framework",
        "description": "PIPEDA compliance including consent management and breach response",
        "covers": ["privacy", "data_retention", "breach_notification"],
    },
    "ctrl_tax_reporting": {
        "name": "Tax Information Reporting System",
        "description": "Automated T5, TFSA, and RRSP reporting to CRA",
        "covers": ["T5_reporting", "TFSA_reporting"],
    },
    "ctrl_compliance_testing": {
        "name": "Periodic Compliance Testing Program",
        "description": "Regular testing of compliance controls and procedures",
        "covers": ["compliance_testing", "compliance_framework"],
    },
    "ctrl_record_keeping": {
        "name": "Record Keeping and Archival System",
        "description": "Centralized document retention and archival for regulatory records",
        "covers": ["record_keeping"],
    },
    "ctrl_capital_monitoring": {
        "name": "Capital Adequacy Monitoring",
        "description": "Real-time monitoring of capital ratios and regulatory capital requirements",
        "covers": ["capital_requirements"],
    },
    "ctrl_vendor_risk": {
        "name": "Third-Party/Vendor Risk Management Program",
        "description": "Due diligence and ongoing monitoring of outsourced service providers",
        "covers": ["outsourcing"],
    },
    "ctrl_margin_system": {
        "name": "Margin and Leverage Monitoring System",
        "description": "Automated margin calculations, alerts, and liquidation triggers",
        "covers": ["margin_requirements"],
    },
    "ctrl_crypto_custody": {
        "name": "Crypto Asset Custody and Cold Storage",
        "description": "Cold storage, multi-sig wallets, and segregated custody for crypto assets",
        "covers": ["crypto_custody"],
    },
    "ctrl_sanctions_screening": {
        "name": "Sanctions Screening and Watchlist Monitoring",
        "description": "Automated screening against OFAC, UN, and Canadian sanctions lists",
        "covers": ["sanctions"],
    },
}
