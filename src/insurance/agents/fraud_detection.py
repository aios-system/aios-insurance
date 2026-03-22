"""Insurance Fraud Detection Agent — rule-based risk flagging.

Rule agent that watches for claim.filed and claim.status_changed events,
evaluates multiple fraud indicators, and flags suspicious claims for SIU review.
"""

from __future__ import annotations

from aios.agents.models import AgentDefinition, AgentType
from aios.ontology.models.types import (
    ActionParameterDef,
    ActionRule,
    ActionRuleType,
    ActionType,
)

from insurance.config import (
    FRAUD_HIGH_VALUE_THRESHOLD,
    FRAUD_MULTI_CLAIM_DAYS,
    FRAUD_PROXIMITY_DAYS,
)


def get_fraud_detection_agent() -> AgentDefinition:
    """Return the fraud detection agent definition."""
    return AgentDefinition(
        name="fraud-detection",
        description=(
            "Detect potential fraud indicators on incoming and updated claims "
            "and route suspicious claims to SIU for investigation"
        ),
        agent_type=AgentType.RULE,
        subscriptions=["claim.filed", "claim.status_changed"],
        rules=[
            {
                "condition": {
                    "event_type": ["claim.filed", "claim.status_changed"],
                },
                "check": f"amount_claimed > {FRAUD_HIGH_VALUE_THRESHOLD}",
                "action": "flag_fraud_risk",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "risk_score": 0.75,
                    "risk_factors": (f"High-value claim exceeds ${FRAUD_HIGH_VALUE_THRESHOLD:,}"),
                    "recommended_action": "siu_review",
                },
            },
            {
                "condition": {
                    "event_type": ["claim.filed", "claim.status_changed"],
                },
                "check": f"multi_claim_count > 1 within {FRAUD_MULTI_CLAIM_DAYS} days",
                "action": "flag_fraud_risk",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "risk_score": 0.65,
                    "risk_factors": (f"Multiple claims filed within {FRAUD_MULTI_CLAIM_DAYS} days"),
                    "recommended_action": "claims_history_review",
                },
            },
            {
                "condition": {
                    "event_type": ["claim.filed", "claim.status_changed"],
                },
                "check": (
                    f"days_between(date_of_loss, policy_effective_date)"
                    f" < {FRAUD_PROXIMITY_DAYS}"
                    f" OR days_between(policy_expiration_date, date_of_loss)"
                    f" < {FRAUD_PROXIMITY_DAYS}"
                ),
                "action": "flag_fraud_risk",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "risk_score": 0.70,
                    "risk_factors": (
                        f"Date of loss within {FRAUD_PROXIMITY_DAYS} days of"
                        " policy effective or expiration date"
                    ),
                    "recommended_action": "policy_timing_review",
                },
            },
            {
                "condition": {
                    "event_type": ["claim.filed", "claim.status_changed"],
                },
                "check": "claim_type NOT IN covered_types_for_policy_type",
                "action": "flag_fraud_risk",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "risk_score": 0.80,
                    "risk_factors": "Claim type inconsistent with policy type",
                    "recommended_action": "coverage_verification",
                },
            },
        ],
        max_actions_per_run=3,
    )


def get_flag_fraud_action() -> ActionType:
    """Return the action type for flagging a fraud risk."""
    return ActionType(
        api_name="flag_fraud_risk",
        description=(
            "Create an SIU investigation record and alert fraud analysts "
            "for a claim with elevated fraud risk indicators"
        ),
        object_type="Investigation",
        parameters=[
            ActionParameterDef(name="claim_id", base_type="STRING", is_required=True),
            ActionParameterDef(name="risk_score", base_type="FLOAT", is_required=True),
            ActionParameterDef(name="risk_factors", base_type="STRING", is_required=True),
            ActionParameterDef(name="recommended_action", base_type="STRING", is_required=True),
        ],
        rules=[
            ActionRule(
                rule_type=ActionRuleType.CREATE_OBJECT,
                target_type="Investigation",
                field_mappings={
                    "investigation_type": "siu_referral",
                    "status": "open",
                },
            ),
            ActionRule(
                rule_type=ActionRuleType.NOTIFY,
                notification_channel="siu-alerts",
                notification_template=(
                    "FRAUD ALERT: Claim {claim_id} scored {risk_score}. Factors: {risk_factors}"
                ),
            ),
            ActionRule(
                rule_type=ActionRuleType.PUBLISH_EVENT,
                event_subject="claim.fraud_flagged",
            ),
        ],
    )
