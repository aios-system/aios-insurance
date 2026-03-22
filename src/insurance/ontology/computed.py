"""Insurance computed property definitions.

Computed properties are evaluated at query time from stored values.
They are NOT persisted — they're derived on-the-fly.
"""

from __future__ import annotations

from aios.ontology.engine.computed import ComputedPropertyDef


def get_claim_computed_properties() -> list[ComputedPropertyDef]:
    """Computed properties for the Claim object type."""
    return [
        ComputedPropertyDef(
            name="outstanding_balance",
            display_name="Outstanding Balance",
            expression="{amount_claimed} - {amount_paid}",
            output_type="FLOAT",
        ),
        ComputedPropertyDef(
            name="days_since_filed",
            display_name="Days Since Filed",
            expression="days_since({date_filed})",
            output_type="INTEGER",
        ),
    ]


def get_subrogation_computed_properties() -> list[ComputedPropertyDef]:
    """Computed properties for the Subrogation object type."""
    return [
        ComputedPropertyDef(
            name="recovery_rate",
            display_name="Recovery Rate",
            expression="{amount_recovered} / {amount_sought}",
            output_type="FLOAT",
        ),
    ]


def get_all_computed_properties() -> dict[str, list[ComputedPropertyDef]]:
    """Return all computed properties keyed by object type api_name."""
    return {
        "Claim": get_claim_computed_properties(),
        "Subrogation": get_subrogation_computed_properties(),
    }
