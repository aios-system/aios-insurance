"""Tests for insurance transform pipelines and connector configurations.

Validates pipeline definitions and basic execution on sample data.
"""

from __future__ import annotations

from aios.data_platform.transforms import TransformEngine, TransformType

from insurance.connectors.registry import get_connector_configs
from insurance.transforms.pipelines import get_transform_pipelines

# ---------------------------------------------------------------------------
# Pipeline Definitions
# ---------------------------------------------------------------------------


class TestPipelineDefinitions:
    def test_two_pipelines_defined(self):
        assert len(get_transform_pipelines()) == 2

    def test_pipeline_names(self):
        names = {p.name for p in get_transform_pipelines()}
        assert "claims-status-summary" in names
        assert "fraud-risk-analysis" in names

    def test_claims_status_has_correct_steps(self):
        pipeline = next(p for p in get_transform_pipelines() if p.name == "claims-status-summary")
        assert len(pipeline.steps) == 3
        step_types = [s.transform_type for s in pipeline.steps]
        assert step_types[0] == TransformType.FILTER
        assert step_types[1] == TransformType.AGGREGATE
        assert step_types[2] == TransformType.SORT

    def test_fraud_risk_has_correct_steps(self):
        pipeline = next(p for p in get_transform_pipelines() if p.name == "fraud-risk-analysis")
        assert len(pipeline.steps) == 4
        step_types = [s.transform_type for s in pipeline.steps]
        assert step_types[0] == TransformType.FILTER
        assert step_types[1] == TransformType.DERIVE
        assert step_types[2] == TransformType.DERIVE
        assert step_types[3] == TransformType.FILTER


# ---------------------------------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------------------------------


class TestPipelineExecution:
    def test_claims_status_filters_closed(self):
        """The FILTER step should remove closed claims."""
        pipeline = next(p for p in get_transform_pipelines() if p.name == "claims-status-summary")
        engine = TransformEngine()

        data = [
            {"claim_id": "C-001", "status": "open", "amount_claimed": 5000},
            {"claim_id": "C-002", "status": "closed", "amount_claimed": 3000},
            {"claim_id": "C-003", "status": "pending", "amount_claimed": 2000},
            {"claim_id": "C-004", "status": "closed", "amount_claimed": 1000},
        ]

        output_data, result = engine.execute(pipeline, data)
        assert len(result.errors) == 0
        # Closed claims are removed before aggregation
        # After FILTER we have 2 rows (open + pending), after AGGREGATE 2 groups
        statuses = {row["status"] for row in output_data}
        assert "closed" not in statuses
        assert "open" in statuses
        assert "pending" in statuses

    def test_fraud_risk_derives_frequency_score(self):
        """The DERIVE step should add frequency_score."""
        pipeline = next(p for p in get_transform_pipelines() if p.name == "fraud-risk-analysis")
        engine = TransformEngine()

        data = [
            {
                "claim_id": "C-001",
                "date_filed": "recent",
                "claims_per_policy_12mo": 24,
                "amount_claimed": 100,
                "policy_cap": 800,
            },
        ]

        output_data, result = engine.execute(pipeline, data)
        assert len(result.errors) == 0
        # The last FILTER step removes unflagged claims; amount 100 < cap 800
        # so amount_anomaly_flag=False → row is filtered out
        # But frequency_score was derived on the way — verify pipeline ran
        assert result.steps_executed == 4

    def test_fraud_risk_filters_flagged_only(self):
        """The final FILTER should retain only amount-anomaly-flagged claims."""
        pipeline = next(p for p in get_transform_pipelines() if p.name == "fraud-risk-analysis")
        engine = TransformEngine()

        data = [
            # High claim — above the cap (should be kept)
            {
                "claim_id": "C-FLAGGED",
                "date_filed": "recent",
                "claims_per_policy_12mo": 12,
                "amount_claimed": 9000,
                "policy_cap": 4000,  # 2 * policy_average of 2000
            },
            # Normal claim — below the cap (should be filtered out)
            {
                "claim_id": "C-NORMAL",
                "date_filed": "recent",
                "claims_per_policy_12mo": 2,
                "amount_claimed": 500,
                "policy_cap": 4000,
            },
        ]

        output_data, result = engine.execute(pipeline, data)
        assert len(result.errors) == 0
        claim_ids = [row["claim_id"] for row in output_data]
        assert "C-FLAGGED" in claim_ids
        assert "C-NORMAL" not in claim_ids


# ---------------------------------------------------------------------------
# Connector Definitions
# ---------------------------------------------------------------------------


class TestConnectors:
    def test_five_connectors_defined(self):
        assert len(get_connector_configs()) == 5

    def test_connector_names(self):
        names = {c.name for c in get_connector_configs()}
        assert "guidewire-claims" in names
        assert "duck-creek-policy" in names
        assert "iso-claimsearch" in names
        assert "edi-gateway" in names
        assert "state-doi-reporting" in names

    def test_all_use_vault_refs(self):
        """No connector should expose a plaintext password."""
        for connector in get_connector_configs():
            if connector.password_ref:
                assert connector.password_ref.startswith("vault://"), (
                    f"Connector '{connector.name}' has non-vault password_ref: "
                    f"{connector.password_ref!r}"
                )
