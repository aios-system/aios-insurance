"""Insurance Claims Triage Agent — rule-based priority assignment.

Rule agent that watches for claim.filed events, evaluates claim amount
and type, and assigns a triage priority for adjuster routing.
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
    TRIAGE_HIGH_THRESHOLD,
    TRIAGE_MEDIUM_THRESHOLD,
    TRIAGE_URGENT_THRESHOLD,
    URGENT_BODILY_INJURY_ADJUSTER,
)


def get_claims_triage_agent() -> AgentDefinition:
    """Return the claims triage agent definition."""
    return AgentDefinition(
        name="claims-triage",
        description="Assign priority triage to incoming claims based on amount and type",
        agent_type=AgentType.RULE,
        subscriptions=["claim.filed"],
        rules=[
            {
                "condition": {
                    "event_type": "claim.filed",
                },
                "check": (
                    f"amount_claimed > {TRIAGE_URGENT_THRESHOLD} AND claim_type == 'bodily_injury'"
                ),
                "action": "triage_claim",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "priority": "urgent",
                    "assigned_adjuster": URGENT_BODILY_INJURY_ADJUSTER,
                    "triage_reason": (f"Bodily injury claim exceeds ${TRIAGE_URGENT_THRESHOLD:,}"),
                },
            },
            {
                "condition": {
                    "event_type": "claim.filed",
                },
                "check": f"amount_claimed > {TRIAGE_HIGH_THRESHOLD}",
                "action": "triage_claim",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "priority": "high",
                    "assigned_adjuster": "",
                    "triage_reason": (f"Claim amount exceeds ${TRIAGE_HIGH_THRESHOLD:,}"),
                },
            },
            {
                "condition": {
                    "event_type": "claim.filed",
                },
                "check": f"amount_claimed > {TRIAGE_MEDIUM_THRESHOLD}",
                "action": "triage_claim",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "priority": "medium",
                    "assigned_adjuster": "",
                    "triage_reason": (f"Claim amount exceeds ${TRIAGE_MEDIUM_THRESHOLD:,}"),
                },
            },
            {
                "condition": {
                    "event_type": "claim.filed",
                },
                "check": "otherwise",
                "action": "triage_claim",
                "parameters": {
                    "claim_id": "{claim_id}",
                    "priority": "low",
                    "assigned_adjuster": "",
                    "triage_reason": "Standard claim — low priority",
                },
            },
        ],
        max_actions_per_run=5,
    )


def get_triage_claim_action() -> ActionType:
    """Return the action type for triaging a claim."""
    return ActionType(
        api_name="triage_claim",
        description="Assign a priority level to a claim and route to an adjuster",
        object_type="Claim",
        parameters=[
            ActionParameterDef(name="claim_id", base_type="STRING", is_required=True),
            ActionParameterDef(name="priority", base_type="STRING", is_required=True),
            ActionParameterDef(name="assigned_adjuster", base_type="STRING", is_required=False),
            ActionParameterDef(name="triage_reason", base_type="STRING", is_required=True),
        ],
        rules=[
            ActionRule(
                rule_type=ActionRuleType.MODIFY_OBJECT,
                target_type="Claim",
                field_mappings={
                    "priority": "{priority}",
                    "assigned_adjuster": "{assigned_adjuster}",
                },
            ),
            ActionRule(
                rule_type=ActionRuleType.NOTIFY,
                notification_channel="claims-intake",
                notification_template=(
                    "TRIAGE: Claim {claim_id} assigned priority {priority}. {triage_reason}"
                ),
            ),
            ActionRule(
                rule_type=ActionRuleType.PUBLISH_EVENT,
                event_subject="claim.triaged",
            ),
        ],
    )
