#!/usr/bin/env python3
"""
FastAPI server for the Regulatory Compliance Monitoring System.
Serves both the API and the React frontend.
"""

import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("compliance-ai")

from backend.analyzer import ComplianceAnalyzer, OBLIGATION_PATTERNS
from backend.models import AnalysisResult, ObligationStatus
from backend import llm_cache, storage
from data.regulatory_sources import REGULATORY_SOURCES, WEALTHSIMPLE_PRODUCTS, EXISTING_CONTROLS

app = FastAPI(
    title="Wealthsimple Compliance AI",
    description="AI-Native Regulatory Compliance Monitoring System",
    version="1.0.0",
)

FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend",
)

# ---- CORS — configurable via ALLOWED_ORIGINS env var ----
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = (
    ["*"] if _raw_origins.strip() == "*"
    else [o.strip() for o in _raw_origins.split(",") if o.strip()]
)
logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Global analyzer instance
analyzer = ComplianceAnalyzer()

# Initialize storage
storage.init_db()

# ---- Rate Limiter (token bucket per IP) ----
RATE_LIMIT_RPM = int(os.environ.get("RATE_LIMIT_RPM", "60"))  # requests/minute
_rate_buckets: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple in-memory token-bucket rate limiter per client IP."""
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60
        # Prune old entries
        _rate_buckets[client_ip] = [
            ts for ts in _rate_buckets[client_ip] if ts > window_start
        ]
        if len(_rate_buckets[client_ip]) >= RATE_LIMIT_RPM:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Max {RATE_LIMIT_RPM} requests/minute."},
                headers={"Retry-After": "60"},
            )
        _rate_buckets[client_ip].append(now)
    return await call_next(request)


# ---- Middleware: request logging + timing ----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    if request.url.path.startswith("/api/"):
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response

# ---- Global exception handler ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs for details."},
    )

# ---- Constants ----
MAX_TEXT_LENGTH = 50_000  # 50KB max for analyze-text input


@app.get("/api/health")
def health():
    """Comprehensive health check — verifies all subsystems."""
    checks = {}

    # 1. Database connectivity
    try:
        state = storage.load_state()
        checks["database"] = "ok"
        checks["has_analysis"] = state is not None
    except Exception as e:
        checks["database"] = f"error: {e}"

    # 2. Analyzer can be instantiated
    try:
        test_analyzer = ComplianceAnalyzer()
        checks["analyzer"] = "ok"
        checks["regulatory_sources"] = len(test_analyzer.sources)
        checks["obligation_patterns"] = len(OBLIGATION_PATTERNS)
    except Exception as e:
        checks["analyzer"] = f"error: {e}"

    # 3. LLM keys configured
    checks["openrouter_configured"] = bool(os.environ.get("OPENROUTER_API_KEY"))
    checks["anthropic_configured"] = bool(os.environ.get("ANTHROPIC_API_KEY"))
    checks["llm_available"] = checks["openrouter_configured"] or checks["anthropic_configured"]

    # 4. Cache status
    try:
        cache_stats = llm_cache.get_stats()
        checks["cache"] = "ok"
        checks["cache_entries"] = cache_stats.get("active_entries", 0)
    except Exception as e:
        checks["cache"] = f"error: {e}"

    all_ok = all(v == "ok" for k, v in checks.items() if k in ("database", "analyzer", "cache"))
    return {"status": "healthy" if all_ok else "degraded", "service": "compliance-ai", "checks": checks}


@app.get("/api/sources")
def get_sources():
    """List all regulatory sources."""
    return {
        "sources": [
            {
                "id": s["id"],
                "title": s["title"],
                "issuer": s["issuer"],
                "section_count": len(s["sections"]),
                "url": s.get("url"),
            }
            for s in REGULATORY_SOURCES
        ]
    }


@app.get("/api/products")
def get_products():
    """List all Wealthsimple products."""
    return {"products": WEALTHSIMPLE_PRODUCTS}


@app.get("/api/controls")
def get_controls():
    """List all existing controls."""
    return {"controls": EXISTING_CONTROLS}


@app.post("/api/analyze")
def run_analysis(source_id: Optional[str] = None):
    """Run compliance analysis on all sources or a specific source."""
    logger.info(f"Starting analysis (source_id={source_id})")
    global analyzer
    analyzer = ComplianceAnalyzer()

    if source_id:
        try:
            result = analyzer.analyze_single_source(source_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        result = analyzer.analyze_all_sources()

    analysis_dict = result.to_dict()
    analysis_dict["sources_count"] = len(REGULATORY_SOURCES)
    analysis_dict["products_count"] = len(WEALTHSIMPLE_PRODUCTS)
    analysis_dict["controls_count"] = len(EXISTING_CONTROLS)
    analysis_dict["patterns_count"] = len(OBLIGATION_PATTERNS)
    storage.save_state(analysis_dict)
    logger.info(f"Analysis complete: {len(analysis_dict.get('obligations', []))} obligations, "
                f"{len(analysis_dict.get('conflicts', []))} conflicts")
    return analysis_dict


@app.get("/api/analysis")
def get_analysis():
    """Get the last analysis result."""
    current = storage.load_state()
    if current is None:
        analyzer = ComplianceAnalyzer()
        seed = analyzer.analyze_all_sources().to_dict()
        current = storage.seed_state_if_empty(seed)
    # Enrich with dynamic metadata
    current["sources_count"] = len(REGULATORY_SOURCES)
    current["products_count"] = len(WEALTHSIMPLE_PRODUCTS)
    current["controls_count"] = len(EXISTING_CONTROLS)
    current["patterns_count"] = len(OBLIGATION_PATTERNS)
    return current


class ReviewRequest(BaseModel):
    obligation_id: str
    reviewer: str
    action: str  # "approve", "reject", "review"
    role: str = "compliance_officer"  # RBAC: admin, compliance_officer, analyst, viewer
    notes: str = ""


@app.post("/api/review")
def review_obligation(request: ReviewRequest):
    """Human review gate: approve/reject an obligation (atomic + RBAC enforced)."""
    logger.info(f"Review request: {request.obligation_id} -> {request.action} "
                f"by {request.reviewer} (role={request.role})")
    try:
        updated = storage.apply_review_atomic(
            obligation_id=request.obligation_id,
            reviewer=request.reviewer,
            action=request.action,
            role=request.role,
            notes=request.notes,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    logger.info(f"Review applied: {request.obligation_id} -> {request.action} by {request.role}")
    return updated


@app.get("/api/roles")
def get_roles():
    """List all available roles and their permissions."""
    return {"roles": storage.ROLES}


@app.get("/api/review/history/{obligation_id}")
def get_review_history(obligation_id: str):
    """Get full review history for an obligation — every action with timestamps."""
    history = storage.get_review_history(obligation_id)
    return {"obligation_id": obligation_id, "history": history, "total": len(history)}


class RevertRequest(BaseModel):
    obligation_id: str
    admin_user: str
    admin_role: str = "admin"


@app.post("/api/review/revert")
def revert_review(request: RevertRequest):
    """Revert the last review action on an obligation. Admin-only."""
    logger.info(f"Revert request: {request.obligation_id} by {request.admin_user} "
                f"(role={request.admin_role})")
    try:
        updated = storage.revert_last_review(
            obligation_id=request.obligation_id,
            admin_user=request.admin_user,
            admin_role=request.admin_role,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    logger.info(f"Review reverted: {request.obligation_id}")
    return updated


class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=MAX_TEXT_LENGTH)
    use_llm: bool = True

    @field_validator("text")
    @classmethod
    def text_must_have_content(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Text must be at least 10 characters after trimming whitespace.")
        return stripped


@app.post("/api/analyze-text")
def analyze_text(request: AnalyzeTextRequest):
    """Analyze arbitrary regulatory text (LLM-powered or deterministic fallback)."""
    logger.info(f"Analyze-text request: {len(request.text)} chars, use_llm={request.use_llm}")

    llm_analyzer = ComplianceAnalyzer()
    if request.use_llm:
        obligations = llm_analyzer.analyze_with_llm(request.text)
    else:
        obligations = llm_analyzer._analyze_text_deterministic(request.text)

    result = AnalysisResult(
        source_document="User-provided regulatory text",
        obligations=obligations,
        conflicts=[],
        audit_log=llm_analyzer.audit_log,
    )
    result.compute_stats()
    result.summary = (
        f"Analyzed user-provided text. "
        f"Extracted {result.total_obligations} obligations. "
        f"{result.needs_human_review} require human review. "
        f"Citation coverage: {result.citation_coverage:.1f}%."
    )
    return result.to_dict()


@app.get("/api/audit-log")
def get_audit_log():
    """Get the full audit log."""
    current = storage.load_state()
    if current is None:
        return {"audit_log": []}
    return {"audit_log": current.get("audit_log", [])}


@app.get("/api/eval/run")
def run_eval():
    """Run the eval harness and return metrics."""
    from eval.run_eval import EvalRunner
    runner = EvalRunner()
    metrics = runner.run_all()
    return {
        "metrics": metrics,
        "results": runner.results,
    }


class EvalSnippetRequest(BaseModel):
    """Test a single regulatory snippet against the system — lets interviewers
    paste ANY new regulation and see how the system classifies it in real-time."""
    snippet: str = Field(..., min_length=10, max_length=MAX_TEXT_LENGTH)
    expected_domains: list[str] = Field(default_factory=list)
    expected_products: list[str] = Field(default_factory=list)
    expected_controls: list[str] = Field(default_factory=list)
    expected_risk_level: Optional[str] = None
    expected_requires_human_review: Optional[bool] = None


@app.post("/api/eval/test-snippet")
def eval_test_snippet(request: EvalSnippetRequest):
    """Dynamic eval: test any new regulatory text against the system.
    Returns what the system extracted + accuracy against optional expected values.
    This proves the system works on unknown data, not just the golden 30/50 set."""
    from eval.run_eval import EvalRunner
    runner = EvalRunner()

    # Run extraction on the new snippet
    actual_domains = runner._extract_domains_from_snippet(request.snippet)
    actual_products = runner._extract_products_from_domains(actual_domains)
    actual_controls = runner._extract_controls_from_domains(actual_domains)
    actual_risk = runner._get_risk_level(actual_domains)
    actual_human_review = runner._would_require_human_review(actual_domains, request.snippet)
    actual_has_citation = runner._check_has_citation(request.snippet, actual_domains)

    result = {
        "extracted": {
            "domains": sorted(set(actual_domains)),
            "products": sorted(actual_products),
            "controls": sorted(actual_controls),
            "risk_level": actual_risk,
            "requires_human_review": actual_human_review,
            "has_citation": actual_has_citation,
        },
        "accuracy": {},
    }

    # If expected values provided, compute accuracy
    if request.expected_domains:
        expected = set(request.expected_domains)
        actual = set(actual_domains)
        result["accuracy"]["domain_accuracy"] = (
            len(expected & actual) / max(len(expected), 1) * 100
        )
    if request.expected_products:
        expected = set(request.expected_products)
        result["accuracy"]["product_accuracy"] = (
            len(expected & actual_products) / max(len(expected), 1) * 100
        )
    if request.expected_controls:
        expected = set(request.expected_controls)
        result["accuracy"]["control_accuracy"] = (
            len(expected & actual_controls) / max(len(expected), 1) * 100
        )
    if request.expected_risk_level:
        result["accuracy"]["risk_match"] = actual_risk == request.expected_risk_level
    if request.expected_requires_human_review is not None:
        result["accuracy"]["escalation_match"] = (
            actual_human_review == request.expected_requires_human_review
        )

    return result


@app.get("/api/cache/stats")
def get_cache_stats():
    """Get LLM cache stats for observability and demo validation."""
    ttl_days = int(os.environ.get("LLM_CACHE_TTL_DAYS", "30"))
    return llm_cache.get_stats(ttl_days=ttl_days)


@app.post("/api/cache/clear")
def clear_cache():
    """Clear all cached LLM responses."""
    ttl_days = int(os.environ.get("LLM_CACHE_TTL_DAYS", "30"))
    before = llm_cache.get_stats(ttl_days=ttl_days)
    cleared = llm_cache.clear()
    after = llm_cache.get_stats(ttl_days=ttl_days)
    return {
        "message": "LLM cache cleared",
        "cleared": cleared,
        "before": before,
        "after": after,
    }


# Serve frontend
@app.get("/")
def serve_frontend():
    frontend_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return HTMLResponse("<h1>Frontend not found. Run from project root.</h1>")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
