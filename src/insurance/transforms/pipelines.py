"""Insurance transform pipelines — claims data processing.

Two core pipelines:
1. Claims Status Summary — active-claims roll-up every 15 minutes
2. Fraud Risk Analysis — hourly anomaly detection on recent claims
"""

from __future__ import annotations

from aios.data_platform.transforms import TransformPipeline, TransformStep, TransformType


def get_transform_pipelines() -> list[TransformPipeline]:
    """Return all insurance transform pipeline definitions."""
    return [
        _claims_status_pipeline(),
        _fraud_risk_pipeline(),
    ]


def _claims_status_pipeline() -> TransformPipeline:
    """Claims Status Summary pipeline.

    Runs every 15 minutes. Filters out closed claims, aggregates by status,
    and sorts by claim count descending for the adjuster dashboard.
    """
    return TransformPipeline(
        name="claims-status-summary",
        description="Aggregate active claims by status for adjuster dashboard",
        schedule="*/15 * * * *",
        steps=[
            TransformStep(
                name="filter-active-claims",
                transform_type=TransformType.FILTER,
                config={"field": "status", "operator": "neq", "value": "closed"},
            ),
            TransformStep(
                name="aggregate-by-status",
                transform_type=TransformType.AGGREGATE,
                config={
                    "group_by": ["status"],
                    "aggregations": [
                        {"field": "claim_id", "fn": "count", "output": "count"},
                        {"field": "amount_claimed", "fn": "sum", "output": "amount_claimed"},
                    ],
                },
            ),
            TransformStep(
                name="sort-by-count-desc",
                transform_type=TransformType.SORT,
                config={"field": "count", "descending": True},
            ),
        ],
    )


def _fraud_risk_pipeline() -> TransformPipeline:
    """Fraud Risk Analysis pipeline.

    Runs hourly. Narrows to claims filed in the last 30 days, derives a
    frequency score and an amount-anomaly flag, then retains only flagged
    claims for SIU review.
    """
    return TransformPipeline(
        name="fraud-risk-analysis",
        description="Identify high-risk claims using frequency and amount anomaly signals",
        schedule="0 * * * *",
        steps=[
            TransformStep(
                name="recent-claims-only",
                transform_type=TransformType.FILTER,
                config={"field": "date_filed", "operator": "within_days", "value": 30},
            ),
            TransformStep(
                name="derive-frequency-score",
                transform_type=TransformType.DERIVE,
                config={
                    "name": "frequency_score",
                    "expression": "{claims_per_policy_12mo} / 12",
                },
            ),
            TransformStep(
                name="derive-amount-anomaly-flag",
                transform_type=TransformType.DERIVE,
                config={
                    "name": "amount_anomaly_flag",
                    # policy_cap = 2 * policy_average, pre-computed by the data source
                    "expression": "{amount_claimed} > {policy_cap}",
                },
            ),
            TransformStep(
                name="filter-flagged-claims",
                transform_type=TransformType.FILTER,
                config={"field": "amount_anomaly_flag", "operator": "eq", "value": True},
            ),
        ],
    )
