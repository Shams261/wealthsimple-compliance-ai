"""
Tests for backend/storage.py — SQLite persistence, RBAC, review history, and revert.
"""

import pytest
import backend.storage as storage


class TestDatabaseInit:
    def test_init_creates_tables(self, temp_db):
        """init_db should create analysis_state and review_history tables."""
        conn = storage._connect()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row["name"] for row in tables}
        assert "analysis_state" in table_names
        assert "review_history" in table_names
        conn.close()


class TestStateManagement:
    def test_save_and_load_state(self, temp_db):
        data = {"obligations": [], "stats": {"total_obligations": 0}}
        storage.save_state(data)
        loaded = storage.load_state()
        assert loaded is not None
        assert loaded["stats"]["total_obligations"] == 0

    def test_load_state_returns_none_when_empty(self, temp_db):
        result = storage.load_state()
        assert result is None

    def test_seed_state_if_empty(self, temp_db):
        seed = {"obligations": [{"id": "test-1", "status": "draft"}]}
        result = storage.seed_state_if_empty(seed)
        assert result["obligations"][0]["id"] == "test-1"

    def test_seed_does_not_overwrite(self, temp_db):
        original = {"obligations": [{"id": "original"}]}
        storage.save_state(original)
        new_seed = {"obligations": [{"id": "new-seed"}]}
        result = storage.seed_state_if_empty(new_seed)
        assert result["obligations"][0]["id"] == "original"


class TestRBAC:
    """Test Role-Based Access Control enforcement."""

    def test_valid_roles(self):
        assert "admin" in storage.ROLES
        assert "compliance_officer" in storage.ROLES
        assert "analyst" in storage.ROLES
        assert "viewer" in storage.ROLES

    def test_admin_has_all_permissions(self):
        perms = storage.ROLES["admin"]
        assert perms["can_approve"] is True
        assert perms["can_reject"] is True
        assert perms["can_revert"] is True

    def test_analyst_is_read_only(self):
        perms = storage.ROLES["analyst"]
        assert perms["can_approve"] is False
        assert perms["can_reject"] is False
        assert perms["can_revert"] is False

    def test_compliance_officer_cannot_revert(self):
        perms = storage.ROLES["compliance_officer"]
        assert perms["can_approve"] is True
        assert perms["can_revert"] is False

    def test_invalid_role_raises(self):
        with pytest.raises(ValueError, match="Unknown role"):
            storage.validate_role("superadmin")

    def test_analyst_cannot_approve(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        with pytest.raises(PermissionError, match="does not have permission"):
            storage.apply_review_atomic(
                obligation_id=ob_id,
                reviewer="analyst@ws.com",
                action="approve",
                role="analyst",
            )

    def test_viewer_cannot_reject(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        with pytest.raises(PermissionError, match="does not have permission"):
            storage.apply_review_atomic(
                obligation_id=ob_id,
                reviewer="viewer@ws.com",
                action="reject",
                role="viewer",
            )


class TestAtomicReview:
    def test_approve_obligation(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        updated = storage.apply_review_atomic(
            obligation_id=ob_id,
            reviewer="officer@ws.com",
            action="approve",
            role="compliance_officer",
            notes="Verified against NI 31-103",
        )
        # Find the obligation in the updated state
        ob = next(o for o in updated["obligations"] if o["id"] == ob_id)
        assert ob["status"] == "approved"
        assert ob["reviewed_by"] == "officer@ws.com"

    def test_reject_obligation(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        updated = storage.apply_review_atomic(
            obligation_id=ob_id,
            reviewer="officer@ws.com",
            action="reject",
            role="compliance_officer",
        )
        ob = next(o for o in updated["obligations"] if o["id"] == ob_id)
        assert ob["status"] == "rejected"

    def test_unknown_obligation_raises(self, seeded_db):
        with pytest.raises(KeyError, match="not found"):
            storage.apply_review_atomic(
                obligation_id="nonexistent-id",
                reviewer="officer@ws.com",
                action="approve",
                role="compliance_officer",
            )

    def test_invalid_action_raises(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        with pytest.raises(ValueError, match="Unknown action"):
            storage.apply_review_atomic(
                obligation_id=ob_id,
                reviewer="officer@ws.com",
                action="delete",
                role="compliance_officer",
            )


class TestReviewHistory:
    def test_history_recorded_after_review(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        storage.apply_review_atomic(
            obligation_id=ob_id,
            reviewer="officer@ws.com",
            action="approve",
            role="compliance_officer",
            notes="Approved after review",
        )
        history = storage.get_review_history(ob_id)
        assert len(history) == 1
        assert history[0]["action"] == "approve"
        assert history[0]["reviewer"] == "officer@ws.com"
        assert history[0]["role"] == "compliance_officer"

    def test_multiple_reviews_tracked(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        storage.apply_review_atomic(
            obligation_id=ob_id, reviewer="a@ws.com", action="approve", role="admin"
        )
        storage.apply_review_atomic(
            obligation_id=ob_id, reviewer="b@ws.com", action="reject", role="admin"
        )
        history = storage.get_review_history(ob_id)
        assert len(history) == 2


class TestRevert:
    def test_revert_restores_previous_status(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        storage.apply_review_atomic(
            obligation_id=ob_id, reviewer="officer@ws.com",
            action="approve", role="compliance_officer"
        )
        updated = storage.revert_last_review(
            obligation_id=ob_id, admin_user="admin@ws.com", admin_role="admin"
        )
        ob = next(o for o in updated["obligations"] if o["id"] == ob_id)
        assert ob["status"] == "draft"

    def test_non_admin_cannot_revert(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        storage.apply_review_atomic(
            obligation_id=ob_id, reviewer="officer@ws.com",
            action="approve", role="compliance_officer"
        )
        with pytest.raises(PermissionError, match="does not have permission"):
            storage.revert_last_review(
                obligation_id=ob_id,
                admin_user="officer@ws.com",
                admin_role="compliance_officer",
            )

    def test_revert_without_review_raises(self, seeded_db):
        ob_id = seeded_db["obligations"][0]["id"]
        with pytest.raises(KeyError, match="No revertable review"):
            storage.revert_last_review(
                obligation_id=ob_id, admin_user="admin@ws.com", admin_role="admin"
            )
