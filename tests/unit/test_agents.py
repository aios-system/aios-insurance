"""Tests for insurance AI agent definitions.

Validates that all 3 agents and their associated action types
are correctly defined and follow AIOS conventions.
"""

from __future__ import annotations

from aios.agents.models import AgentType
from aios.ontology.models.types import ActionRuleType

from insurance.agents.claims_advisor import get_claims_advisor_agent
from insurance.agents.claims_triage import get_claims_triage_agent, get_triage_claim_action
from insurance.agents.fraud_detection import get_flag_fraud_action, get_fraud_detection_agent
from insurance.config import TRIAGE_URGENT_THRESHOLD

# ---------------------------------------------------------------------------
# Claims Triage Agent
# ---------------------------------------------------------------------------


class TestClaimsTriageAgent:
    def test_is_rule_type(self):
        agent = get_claims_triage_agent()
        assert agent.agent_type == AgentType.RULE

    def test_subscribes_to_claim_filed(self):
        agent = get_claims_triage_agent()
        assert "claim.filed" in agent.subscriptions

    def test_has_triage_rules(self):
        agent = get_claims_triage_agent()
        assert len(agent.rules) == 4

    def test_triage_action_parameters(self):
        action = get_triage_claim_action()
        param_names = {p.name for p in action.parameters}
        assert "claim_id" in param_names
        assert "priority" in param_names
        assert "assigned_adjuster" in param_names
        assert "triage_reason" in param_names

    def test_triage_action_rule_types(self):
        action = get_triage_claim_action()
        rule_types = {r.rule_type for r in action.rules}
        assert ActionRuleType.MODIFY_OBJECT in rule_types
        assert ActionRuleType.NOTIFY in rule_types
        assert ActionRuleType.PUBLISH_EVENT in rule_types

    def test_urgent_rule_references_threshold(self):
        agent = get_claims_triage_agent()
        # The first rule is the urgent one (highest priority check)
        urgent_rule = agent.rules[0]
        assert str(TRIAGE_URGENT_THRESHOLD) in urgent_rule["check"]


# ---------------------------------------------------------------------------
# Fraud Detection Agent
# ---------------------------------------------------------------------------


class TestFraudDetectionAgent:
    def test_is_rule_type(self):
        agent = get_fraud_detection_agent()
        assert agent.agent_type == AgentType.RULE

    def test_subscribes_to_claim_events(self):
        agent = get_fraud_detection_agent()
        assert "claim.filed" in agent.subscriptions
        assert "claim.status_changed" in agent.subscriptions

    def test_has_fraud_rules(self):
        agent = get_fraud_detection_agent()
        assert len(agent.rules) == 4

    def test_flag_fraud_action_creates_investigation(self):
        action = get_flag_fraud_action()
        create_rules = [r for r in action.rules if r.rule_type == ActionRuleType.CREATE_OBJECT]
        assert len(create_rules) == 1
        assert create_rules[0].target_type == "Investigation"

    def test_flag_fraud_action_rule_types(self):
        action = get_flag_fraud_action()
        rule_types = {r.rule_type for r in action.rules}
        assert ActionRuleType.CREATE_OBJECT in rule_types
        assert ActionRuleType.NOTIFY in rule_types
        assert ActionRuleType.PUBLISH_EVENT in rule_types


# ---------------------------------------------------------------------------
# Claims Advisor Agent
# ---------------------------------------------------------------------------


class TestClaimsAdvisorAgent:
    def test_is_llm_type(self):
        agent = get_claims_advisor_agent()
        assert agent.agent_type == AgentType.LLM

    def test_subscribes_to_investigation_completed(self):
        agent = get_claims_advisor_agent()
        assert "investigation.completed" in agent.subscriptions

    def test_has_system_prompt(self):
        agent = get_claims_advisor_agent()
        assert len(agent.system_prompt) > 100
        prompt_lower = agent.system_prompt.lower()
        assert "claims advisor" in prompt_lower or "claims advisory" in prompt_lower

    def test_max_actions_limited(self):
        agent = get_claims_advisor_agent()
        assert agent.max_actions_per_run == 3

    def test_uses_claude_model(self):
        agent = get_claims_advisor_agent()
        assert "claude" in agent.model
