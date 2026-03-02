"""
Shared pytest fixtures for the Compliance AI test suite.
"""

import os
import sys

import pytest

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.analyzer import ComplianceAnalyzer, OBLIGATION_PATTERNS
from backend.models import (
    AnalysisResult, AuditLogEntry, Citation, ConfidenceLevel,
    ConflictDetection, EscalationReason, Obligation, ObligationStatus, RiskLevel,
)
from data.regulatory_sources import REGULATORY_SOURCES, WEALTHSIMPLE_PRODUCTS, EXISTING_CONTROLS


@pytest.fixture
def analyzer():
    """Fresh ComplianceAnalyzer instance."""
    return ComplianceAnalyzer()


@pytest.fixture
def sample_kyc_text():
    """Sample regulatory text containing KYC obligations."""
    return (
        "A registrant must take reasonable steps to ensure that, before it makes a "
        "recommendation to a client, it has sufficient information regarding the "
        "client's investment needs, objectives, financial circumstances, and risk "
        "tolerance. The registrant must verify the identity of each client using "
        "know your client procedures."
    )


@pytest.fixture
def sample_aml_text():
    """Sample regulatory text containing AML obligations."""
    return (
        "Reporting entities must file a suspicious transaction report with FINTRAC "
        "when there are reasonable grounds to suspect that a transaction is related "
        "to money laundering or terrorist financing. All transactions over $10,000 "
        "must be reported."
    )


@pytest.fixture
def sample_multi_domain_text():
    """Sample text that should trigger multiple domain matches."""
    return (
        "The firm must implement know your client procedures to verify the identity "
        "of all clients, assess suitability of all investment recommendations, and "
        "maintain books and records for a minimum of 7 years."
    )


@pytest.fixture
def temp_db(tmp_path):
    """Provide a temporary database path and ensure clean state."""
    import backend.storage as storage
    original_path = storage.DB_PATH
    test_db = str(tmp_path / "test_compliance.db")
    storage.DB_PATH = test_db
    storage.init_db()
    yield test_db
    storage.DB_PATH = original_path


@pytest.fixture
def seeded_db(temp_db):
    """Database pre-seeded with a sample analysis state."""
    import backend.storage as storage
    analyzer = ComplianceAnalyzer()
    result = analyzer.analyze_all_sources()
    data = result.to_dict()
    storage.save_state(data)
    return data


@pytest.fixture
def tmp_cache(tmp_path):
    """Point LLM cache at a temp JSON file so tests never touch real cache."""
    from backend import llm_cache
    original_path = llm_cache._CACHE_FILE
    llm_cache._CACHE_FILE = str(tmp_path / "test_cache.json")
    yield llm_cache._CACHE_FILE
    llm_cache._CACHE_FILE = original_path
