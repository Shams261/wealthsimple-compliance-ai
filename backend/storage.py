"""SQLite-backed storage for analysis state, review history, and audit logs."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "compliance.db")
)

# ---- RBAC Role Definitions ----
ROLES = {
    "admin": {
        "can_approve": True,
        "can_reject": True,
        "can_revert": True,
        "description": "Full system access including undo/revert",
    },
    "compliance_officer": {
        "can_approve": True,
        "can_reject": True,
        "can_revert": False,
        "description": "Can approve/reject obligations",
    },
    "analyst": {
        "can_approve": False,
        "can_reject": False,
        "can_revert": False,
        "description": "Read-only access, can add review notes",
    },
    "viewer": {
        "can_approve": False,
        "can_reject": False,
        "can_revert": False,
        "description": "Read-only dashboard access",
    },
}


def validate_role(role: str) -> dict:
    """Validate and return role permissions. Raises ValueError if invalid."""
    if role not in ROLES:
        raise ValueError(
            f"Unknown role: '{role}'. Valid roles: {', '.join(ROLES.keys())}"
        )
    return ROLES[role]


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read/write
    conn.execute("PRAGMA busy_timeout=5000")  # Wait up to 5s if locked
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        # Review history — stores every review action with before/after state
        # for full auditability and revert capability
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                obligation_id TEXT NOT NULL,
                action TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                role TEXT NOT NULL,
                before_status TEXT NOT NULL,
                after_status TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                reverted INTEGER DEFAULT 0
            );
            """
        )
        conn.commit()


def load_state() -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute("SELECT data FROM analysis_state WHERE id = 1").fetchone()
        if not row:
            return None
        return json.loads(row["data"])


def save_state(data: dict) -> None:
    payload = json.dumps(data)
    updated_at = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO analysis_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (payload, updated_at),
        )
        conn.commit()


def seed_state_if_empty(seed_data: dict) -> dict:
    existing = load_state()
    if existing is not None:
        return existing
    save_state(seed_data)
    return seed_data


def _compute_stats(data: dict) -> dict:
    obligations = data.get("obligations", [])
    total = len(obligations)
    cited = sum(1 for o in obligations if o.get("citation"))
    needs_review = sum(
        1 for o in obligations if o.get("requires_human_review") and o.get("status") == "draft"
    )
    high_risk = sum(
        1
        for o in obligations
        if o.get("risk_level") in {"high", "critical"}
    )
    citation_coverage = (cited / total * 100) if total > 0 else 0.0
    return {
        "total_obligations": total,
        "auto_approved": sum(1 for o in obligations if not o.get("requires_human_review")),
        "needs_human_review": needs_review,
        "high_risk_count": high_risk,
        "citation_coverage": round(citation_coverage, 1),
    }


def apply_review_atomic(
    obligation_id: str,
    reviewer: str,
    action: str,
    role: str = "compliance_officer",
    notes: str = "",
) -> dict:
    """
    Atomically load state, apply review, and save — prevents TOCTOU
    race conditions when two reviewers act concurrently.

    Enforces RBAC: only roles with can_approve/can_reject may act.
    Records full review history for audit and revert capability.
    """
    if action not in ("approve", "reject", "review"):
        raise ValueError(f"Unknown action: {action}")

    # RBAC check
    permissions = validate_role(role)
    if action == "approve" and not permissions["can_approve"]:
        raise PermissionError(
            f"Role '{role}' does not have permission to approve obligations. "
            f"Required role: compliance_officer or admin."
        )
    if action == "reject" and not permissions["can_reject"]:
        raise PermissionError(
            f"Role '{role}' does not have permission to reject obligations. "
            f"Required role: compliance_officer or admin."
        )

    now_iso = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        # Single transaction: read → modify → write
        row = conn.execute("SELECT data FROM analysis_state WHERE id = 1").fetchone()
        if not row:
            raise KeyError("No analysis state found. Run analysis first.")

        data = json.loads(row["data"])
        obligations = data.get("obligations", [])

        match = None
        for ob in obligations:
            if ob.get("id") == obligation_id:
                match = ob
                break

        if match is None:
            raise KeyError(f"Obligation {obligation_id} not found")

        before_status = match.get("status", "draft")

        if action == "approve":
            match["status"] = "approved"
        elif action == "reject":
            match["status"] = "rejected"
        elif action == "review":
            match["status"] = "reviewed"

        after_status = match["status"]

        match["reviewed_by"] = reviewer
        match["reviewed_at"] = now_iso
        match["review_notes"] = notes

        # Record in review_history table for revert capability
        conn.execute(
            """INSERT INTO review_history
               (obligation_id, action, reviewer, role, before_status, after_status, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (obligation_id, action, reviewer, role, before_status, after_status, notes, now_iso),
        )

        audit_log = data.get("audit_log", [])
        audit_log.append(
            {
                "id": str(uuid4())[:8],
                "timestamp": now_iso,
                "action": f"obligation_{action}d",
                "actor": f"{reviewer} ({role})",
                "entity_type": "obligation",
                "entity_id": obligation_id,
                "before_state": {"status": before_status},
                "after_state": {"status": after_status},
                "notes": notes or f"Obligation {action}d by {role}",
            }
        )
        data["audit_log"] = audit_log
        data["stats"] = _compute_stats(data)

        # Write back atomically within the same connection/transaction
        conn.execute(
            "UPDATE analysis_state SET data = ?, updated_at = ? WHERE id = 1",
            (json.dumps(data), now_iso),
        )
        conn.commit()

    return data


def get_review_history(obligation_id: str) -> list[dict]:
    """Get full review history for an obligation — every action with timestamps."""
    with _connect() as conn:
        rows = conn.execute(
            """SELECT id, obligation_id, action, reviewer, role,
                      before_status, after_status, notes, created_at, reverted
               FROM review_history
               WHERE obligation_id = ?
               ORDER BY created_at DESC""",
            (obligation_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def revert_last_review(obligation_id: str, admin_user: str, admin_role: str = "admin") -> dict:
    """
    Revert the last review action on an obligation.
    Only admin role can revert. Restores the obligation to its previous status.
    Returns the updated analysis state.
    """
    permissions = validate_role(admin_role)
    if not permissions["can_revert"]:
        raise PermissionError(
            f"Role '{admin_role}' does not have permission to revert reviews. "
            f"Required role: admin."
        )

    now_iso = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        # Find the latest non-reverted review for this obligation
        last_review = conn.execute(
            """SELECT id, before_status, after_status, action, reviewer, role
               FROM review_history
               WHERE obligation_id = ? AND reverted = 0
               ORDER BY created_at DESC LIMIT 1""",
            (obligation_id,),
        ).fetchone()

        if not last_review:
            raise KeyError(
                f"No revertable review found for obligation {obligation_id}. "
                f"Either no review was done or it was already reverted."
            )

        # Load current state
        row = conn.execute("SELECT data FROM analysis_state WHERE id = 1").fetchone()
        if not row:
            raise KeyError("No analysis state found.")

        data = json.loads(row["data"])

        # Find the obligation and restore previous status
        match = None
        for ob in data.get("obligations", []):
            if ob.get("id") == obligation_id:
                match = ob
                break

        if match is None:
            raise KeyError(f"Obligation {obligation_id} not found in current state")

        reverted_from = match.get("status")
        restored_to = last_review["before_status"]

        match["status"] = restored_to
        match["reviewed_by"] = None
        match["reviewed_at"] = None
        match["review_notes"] = None

        # Mark the review as reverted
        conn.execute(
            "UPDATE review_history SET reverted = 1 WHERE id = ?",
            (last_review["id"],),
        )

        # Record the revert in review_history
        conn.execute(
            """INSERT INTO review_history
               (obligation_id, action, reviewer, role, before_status, after_status, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (obligation_id, "revert", admin_user, admin_role, reverted_from, restored_to,
             f"Reverted {last_review['action']} by {last_review['reviewer']} ({last_review['role']})",
             now_iso),
        )

        # Add to audit log
        audit_log = data.get("audit_log", [])
        audit_log.append(
            {
                "id": str(uuid4())[:8],
                "timestamp": now_iso,
                "action": "obligation_reverted",
                "actor": f"{admin_user} ({admin_role})",
                "entity_type": "obligation",
                "entity_id": obligation_id,
                "before_state": {"status": reverted_from},
                "after_state": {"status": restored_to},
                "notes": f"Reverted: {last_review['action']} by {last_review['reviewer']} undone",
            }
        )
        data["audit_log"] = audit_log
        data["stats"] = _compute_stats(data)

        conn.execute(
            "UPDATE analysis_state SET data = ?, updated_at = ? WHERE id = 1",
            (json.dumps(data), now_iso),
        )
        conn.commit()

    return data


# Backward compatibility alias
def apply_review(data, obligation_id, reviewer, action, notes=""):
    """Legacy wrapper — prefer apply_review_atomic for concurrent safety."""
    return apply_review_atomic(obligation_id, reviewer, action, notes=notes)
