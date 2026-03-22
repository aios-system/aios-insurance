"""Insurance Claims Advisor Agent — LLM-powered settlement recommendations.

An AI agent that reviews completed investigation findings and claim details
to recommend settlement amounts, denial rationale, or further investigation steps.
All recommendations require human adjuster approval before execution.
"""

from __future__ import annotations

from aios.agents.models import AgentDefinition, AgentType

CLAIMS_ADVISOR_SYSTEM_PROMPT = (
    "You are a claims advisory agent for an insurance company. You analyze investigation"
    " findings and claim details to recommend settlement amounts, denial rationale, or"
    " further investigation steps. Always cite specific policy terms and investigation"
    " findings in your recommendations. Never auto-approve claims above $50,000."
)


def get_claims_advisor_agent() -> AgentDefinition:
    """Return the claims advisor LLM agent definition."""
    return AgentDefinition(
        name="claims-advisor",
        description=(
            "AI assistant for claims advisory — reviews investigation findings "
            "and recommends settlement amounts or denial rationale"
        ),
        agent_type=AgentType.LLM,
        subscriptions=["investigation.completed"],
        system_prompt=CLAIMS_ADVISOR_SYSTEM_PROMPT,
        model="claude-sonnet-4-20250514",
        max_actions_per_run=3,
    )
