"""Insurance LinkType definitions — 5 relationships between entity types.

These links encode the relationships in the claims lifecycle:
policies generate claims, claims spawn investigations and payments,
and investigations can trigger subrogation.
"""

from __future__ import annotations

from aios.ontology.models.types import Cardinality, LinkType


def get_link_types() -> list[LinkType]:
    """Return all 5 insurance link type definitions."""
    return [
        LinkType(
            api_name="policy_has_claim",
            description="Policy has one or more filed claims",
            source_type="Policy",
            target_type="Claim",
            cardinality=Cardinality.ONE_TO_MANY,
        ),
        LinkType(
            api_name="claim_has_investigation",
            description="Claim has one or more investigations",
            source_type="Claim",
            target_type="Investigation",
            cardinality=Cardinality.ONE_TO_MANY,
        ),
        LinkType(
            api_name="claim_has_payment",
            description="Claim has one or more disbursed payments",
            source_type="Claim",
            target_type="ClaimPayment",
            cardinality=Cardinality.ONE_TO_MANY,
        ),
        LinkType(
            api_name="claim_has_subrogation",
            description="Claim has an associated subrogation record",
            source_type="Claim",
            target_type="Subrogation",
            cardinality=Cardinality.ONE_TO_ONE,
        ),
        LinkType(
            api_name="investigation_triggers_subrogation",
            description="Investigation that led to a subrogation action",
            source_type="Investigation",
            target_type="Subrogation",
            cardinality=Cardinality.ONE_TO_ONE,
        ),
    ]
