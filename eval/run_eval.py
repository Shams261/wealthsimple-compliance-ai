#!/usr/bin/env python3
"""
Eval Harness for Regulatory Compliance Monitoring System.

Runs 70 regulatory snippets through the analyzer and measures:
  1. Obligation extraction accuracy (did we find the right domains?)
  2. Correct product mapping rate
  3. Correct control mapping rate
  4. Citation coverage (% of obligations with evidence)
  5. Correct escalation rate (human review flagging accuracy)
  6. Risk level accuracy

Prints a detailed metrics report. This is the proof that the system isn't hand-wavy.
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import (
    Citation, Obligation, RiskLevel, ConfidenceLevel, EscalationReason
)
from backend.analyzer import ComplianceAnalyzer
from eval.test_cases import EVAL_TEST_CASES


class EvalRunner:
    """
    Eval runner that sends snippets through the REAL analyzer pipeline
    (_analyze_text_deterministic) and compares actual Obligation objects
    against expected values.  No logic is duplicated from the analyzer —
    this is a true black-box evaluation.
    """

    def __init__(self):
        self.analyzer = ComplianceAnalyzer()
        self.results = []

    # ------------------------------------------------------------------
    # Helpers that read from real Obligation objects, NOT from patterns
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_domains_from_obligations(obligations: list) -> set:
        """Parse domain tags from obligation descriptions produced by the analyzer."""
        import re
        domains = set()
        for ob in obligations:
            m = re.match(r"\[([A-Z_]+)\]", ob.description)
            if m:
                domains.add(m.group(1).lower())
        return domains

    @staticmethod
    def _extract_products_from_obligations(obligations: list) -> set:
        """Collect product IDs from real mapped_products on Obligation objects."""
        products = set()
        for ob in obligations:
            for p in ob.mapped_products:
                products.add(p["id"])
        return products

    @staticmethod
    def _extract_controls_from_obligations(obligations: list) -> set:
        """Collect control IDs from real mapped_controls on Obligation objects."""
        controls = set()
        for ob in obligations:
            for c in ob.mapped_controls:
                controls.add(c["id"])
        return controls

    @staticmethod
    def _get_highest_risk(obligations: list) -> str:
        """Return the highest risk level string across all obligations."""
        risk_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_risk = "low"
        for ob in obligations:
            level = ob.risk_level.value
            if risk_priority.get(level, 0) > risk_priority.get(max_risk, 0):
                max_risk = level
        return max_risk

    @staticmethod
    def _any_requires_human_review(obligations: list) -> bool:
        """Check if ANY obligation in the set was flagged for human review."""
        return any(ob.requires_human_review for ob in obligations)

    @staticmethod
    def _any_has_citation(obligations: list) -> bool:
        """Check if ANY obligation has a non-None citation."""
        return any(ob.citation is not None for ob in obligations)

    def evaluate_single(self, test_case: dict) -> dict:
        """
        Evaluate a single test case by running the snippet through the
        real analyzer pipeline and comparing the produced Obligation
        objects against expected values.
        """
        tc_id = test_case["id"]
        snippet = test_case["snippet"]
        expected = test_case["expected"]

        # ---- Run the REAL analyzer pipeline ----
        obligations = self.analyzer._analyze_text_deterministic(snippet)

        # ---- Extract actuals from real Obligation objects ----
        actual_domains = self._extract_domains_from_obligations(obligations)
        actual_products = self._extract_products_from_obligations(obligations)
        actual_controls = self._extract_controls_from_obligations(obligations)
        actual_has_citation = self._any_has_citation(obligations)
        actual_risk = self._get_highest_risk(obligations) if obligations else "low"
        actual_human_review = self._any_requires_human_review(obligations)

        # ---- Compare against expected ----
        expected_domains = set(expected["domains"])
        # Normalize to lowercase for comparison
        expected_domains_lower = {d.lower() for d in expected_domains}
        domain_match = len(expected_domains_lower & actual_domains) / max(len(expected_domains_lower), 1)

        expected_products = set(expected["products"])
        product_match = len(expected_products & actual_products) / max(len(expected_products), 1)

        expected_controls = set(expected["controls"])
        if len(expected_controls) == 0 and len(actual_controls) == 0:
            control_match = 1.0
        elif len(expected_controls) == 0:
            control_match = 0.0
        else:
            control_match = len(expected_controls & actual_controls) / max(len(expected_controls), 1)

        citation_match = 1.0 if actual_has_citation == expected["has_citation"] else 0.0
        risk_match = 1.0 if actual_risk == expected["risk_level"] else 0.0
        escalation_match = 1.0 if actual_human_review == expected["requires_human_review"] else 0.0

        result = {
            "id": tc_id,
            "source": test_case["source"],
            "domain_accuracy": domain_match,
            "product_mapping_accuracy": product_match,
            "control_mapping_accuracy": control_match,
            "citation_coverage": citation_match,
            "risk_level_accuracy": risk_match,
            "escalation_accuracy": escalation_match,
            "expected_domains": sorted(expected_domains_lower),
            "actual_domains": sorted(actual_domains),
            "domain_correct": domain_match == 1.0,
            "risk_correct": risk_match == 1.0,
            "escalation_correct": escalation_match == 1.0,
        }

        return result

    def run_all(self) -> dict:
        """Run all eval test cases and compute aggregate metrics."""
        self.results = []
        for tc in EVAL_TEST_CASES:
            result = self.evaluate_single(tc)
            self.results.append(result)

        # Aggregate
        n = len(self.results)
        metrics = {
            "total_test_cases": n,
            "obligation_extraction_accuracy": sum(r["domain_accuracy"] for r in self.results) / n * 100,
            "product_mapping_accuracy": sum(r["product_mapping_accuracy"] for r in self.results) / n * 100,
            "control_mapping_accuracy": sum(r["control_mapping_accuracy"] for r in self.results) / n * 100,
            "citation_coverage": sum(r["citation_coverage"] for r in self.results) / n * 100,
            "risk_level_accuracy": sum(r["risk_level_accuracy"] for r in self.results) / n * 100,
            "escalation_accuracy": sum(r["escalation_accuracy"] for r in self.results) / n * 100,
            "perfect_domain_matches": sum(1 for r in self.results if r["domain_correct"]),
            "perfect_risk_matches": sum(1 for r in self.results if r["risk_correct"]),
            "perfect_escalation_matches": sum(1 for r in self.results if r["escalation_correct"]),
        }

        return metrics

    def print_report(self):
        """Print a detailed eval report."""
        metrics = self.run_all()

        print("=" * 72)
        print("  REGULATORY COMPLIANCE AI — EVAL HARNESS REPORT")
        print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 72)
        print()

        # Summary metrics
        print("┌─────────────────────────────────────────┬──────────┐")
        print("│ METRIC                                  │ SCORE    │")
        print("├─────────────────────────────────────────┼──────────┤")
        print(f"│ Obligation Extraction Accuracy          │ {metrics['obligation_extraction_accuracy']:6.1f}%  │")
        print(f"│ Product Mapping Accuracy                │ {metrics['product_mapping_accuracy']:6.1f}%  │")
        print(f"│ Control Mapping Accuracy                │ {metrics['control_mapping_accuracy']:6.1f}%  │")
        print(f"│ Citation Coverage                       │ {metrics['citation_coverage']:6.1f}%  │")
        print(f"│ Risk Level Accuracy                     │ {metrics['risk_level_accuracy']:6.1f}%  │")
        print(f"│ Escalation (Human Review) Accuracy      │ {metrics['escalation_accuracy']:6.1f}%  │")
        print("├─────────────────────────────────────────┼──────────┤")
        print(f"│ Perfect Domain Matches                  │ {metrics['perfect_domain_matches']:3d}/{metrics['total_test_cases']:2d}   │")
        print(f"│ Perfect Risk Matches                    │ {metrics['perfect_risk_matches']:3d}/{metrics['total_test_cases']:2d}   │")
        print(f"│ Perfect Escalation Matches              │ {metrics['perfect_escalation_matches']:3d}/{metrics['total_test_cases']:2d}   │")
        print("└─────────────────────────────────────────┴──────────┘")
        print()

        # Per-case details
        print("─" * 72)
        print("  PER-CASE RESULTS")
        print("─" * 72)
        print()

        for r in self.results:
            status = "✓" if r["domain_correct"] and r["risk_correct"] and r["escalation_correct"] else "✗"
            print(f"  {status} {r['id']} | {r['source'][:45]:<45}")
            if not r["domain_correct"]:
                print(f"      Domain: expected {r['expected_domains']}, got {r['actual_domains']}")
            if not r["risk_correct"]:
                print(f"      Risk: MISMATCH")
            if not r["escalation_correct"]:
                print(f"      Escalation: MISMATCH")
            print(f"      Scores: domain={r['domain_accuracy']:.0%} product={r['product_mapping_accuracy']:.0%} "
                  f"control={r['control_mapping_accuracy']:.0%} citation={r['citation_coverage']:.0%}")
            print()

        # Failures summary
        failures = [r for r in self.results if not (r["domain_correct"] and r["risk_correct"] and r["escalation_correct"])]
        if failures:
            print(f"  ⚠ {len(failures)} test case(s) with mismatches")
        else:
            print("  ✓ All test cases passed!")

        print()
        print("=" * 72)
        print("  END OF EVAL REPORT")
        print("=" * 72)

        return metrics

    def export_json(self, filepath: str):
        """Export results as JSON for CI/CD integration."""
        metrics = self.run_all()
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "results": self.results,
        }
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults exported to {filepath}")


def main():
    runner = EvalRunner()
    metrics = runner.print_report()

    # Also run the full analyzer and show its output
    print("\n")
    print("=" * 72)
    print("  FULL SYSTEM ANALYSIS (all regulatory sources)")
    print("=" * 72)
    print()

    analyzer = ComplianceAnalyzer()
    result = analyzer.analyze_all_sources()
    data = result.to_dict()

    print(f"  Summary: {data['summary']}")
    print()
    print(f"  Total obligations extracted: {data['stats']['total_obligations']}")
    print(f"  Auto-approved (no human review): {data['stats']['auto_approved']}")
    print(f"  Needs human review: {data['stats']['needs_human_review']}")
    print(f"  High/Critical risk: {data['stats']['high_risk_count']}")
    print(f"  Citation coverage: {data['stats']['citation_coverage']}%")
    print(f"  Policy conflicts detected: {len(data['conflicts'])}")
    print(f"  Audit log entries: {len(data['audit_log'])}")
    print()

    # Show conflicts
    if data["conflicts"]:
        print("  CONFLICTS DETECTED:")
        for c in data["conflicts"]:
            print(f"    ⚠ [{c['conflict_type']}] {c['description'][:80]}...")
            if c["source_a"]:
                print(f"      Source A: {c['source_a']['source_document'][:50]}")
            if c["source_b"]:
                print(f"      Source B: {c['source_b']['source_document'][:50]}")
            print()

    # Show obligations requiring human review
    human_review = [o for o in data["obligations"] if o["requires_human_review"]]
    print(f"  OBLIGATIONS REQUIRING HUMAN REVIEW ({len(human_review)}):")
    for o in human_review[:5]:
        print(f"    ● {o['description'][:65]}")
        print(f"      Risk: {o['risk_level']} | Status: {o['status']} | Escalation: {', '.join(o['escalation_reasons'])}")
        if o["citation"]:
            excerpt = o["citation"]["excerpt"][:80]
            print(f"      Citation: \"{excerpt}...\"")
        else:
            print(f"      Citation: ⚠ MISSING — needs human review")
        print()

    if len(human_review) > 5:
        print(f"    ... and {len(human_review) - 5} more\n")

    # Export
    export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eval_results.json")
    runner.export_json(export_path)

    return metrics


if __name__ == "__main__":
    main()
