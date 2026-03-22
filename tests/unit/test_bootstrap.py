"""Tests for Insurance master bootstrap.

Validates that bootstrap_insurance() correctly registers all types,
link types, and action types with the AIOS ontology.
"""

from __future__ import annotations

from insurance.bootstrap import bootstrap_insurance

# ---------------------------------------------------------------------------
# Bootstrap Integration Tests
# ---------------------------------------------------------------------------


class TestBootstrap:
    async def test_creates_all_object_types(self, session_factory):
        result = await bootstrap_insurance(session_factory)
        assert len(result["created_types"]) == 5

    async def test_creates_all_link_types(self, session_factory):
        result = await bootstrap_insurance(session_factory)
        assert len(result["created_links"]) == 5

    async def test_creates_all_action_types(self, session_factory):
        result = await bootstrap_insurance(session_factory)
        assert len(result["created_actions"]) == 2
        action_names = set(result["created_actions"])
        assert "triage_claim" in action_names
        assert "flag_fraud_risk" in action_names

    async def test_total_created(self, session_factory):
        result = await bootstrap_insurance(session_factory)
        assert result["total_created"] == 12  # 5 + 5 + 2

    async def test_idempotent(self, session_factory):
        """Running bootstrap twice should skip already-registered items."""
        first = await bootstrap_insurance(session_factory)
        assert first["total_created"] == 12
        assert first["total_skipped"] == 0

        second = await bootstrap_insurance(session_factory)
        assert second["total_created"] == 0
        assert second["total_skipped"] == 12
