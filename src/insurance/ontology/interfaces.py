"""Insurance ontology interfaces — polymorphic type contracts.

Interfaces allow querying across different object types that share
common properties. All 5 insurance types carry a lifecycle status field,
so they all implement HasStatus.
"""

from __future__ import annotations

from aios.ontology.models.interfaces import OntologyInterface
from aios.ontology.models.types import PropertyType


def get_interfaces() -> list[OntologyInterface]:
    """Return all insurance interface definitions."""
    return [
        _has_status(),
    ]


def get_interface_implementations() -> dict[str, list[str]]:
    """Return a map of interface api_name -> list of implementing ObjectType api_names."""
    return {
        "HasStatus": [
            "Policy",
            "Claim",
            "Investigation",
            "ClaimPayment",
            "Subrogation",
        ],
    }


def _has_status() -> OntologyInterface:
    return OntologyInterface(
        api_name="HasStatus",
        description="Entities with a lifecycle status field",
        properties=[
            PropertyType(name="status", base_type="STRING"),
        ],
    )
