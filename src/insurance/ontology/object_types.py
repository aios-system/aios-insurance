"""Insurance ObjectType definitions — 5 entity types for the insurance claims ontology.

Each ObjectType maps to a real-world entity in the claims lifecycle:
policies, claims, investigations, payments, and subrogation records.
"""

from __future__ import annotations

from aios.ontology.models.types import ObjectType, PropertyType


def get_object_types() -> list[ObjectType]:
    """Return all 5 insurance object type definitions."""
    return [
        _policy(),
        _claim(),
        _investigation(),
        _claim_payment(),
        _subrogation(),
    ]


def _policy() -> ObjectType:
    return ObjectType(
        api_name="Policy",
        description="An insurance policy held by a customer",
        properties=[
            PropertyType(
                name="policy_number", base_type="STRING", is_required=True, is_primary_key=True
            ),
            PropertyType(name="holder_name", base_type="STRING", is_required=True),
            PropertyType(name="holder_ssn", base_type="STRING", is_required=True),
            PropertyType(name="holder_email", base_type="STRING"),
            PropertyType(
                name="policy_type",
                base_type="STRING",
                constraints={"allowed_values": ["auto", "home", "life", "health", "commercial"]},
            ),
            PropertyType(name="effective_date", base_type="DATETIME", is_required=True),
            PropertyType(name="expiration_date", base_type="DATETIME"),
            PropertyType(name="premium_amount", base_type="FLOAT"),
            PropertyType(name="coverage_limit", base_type="FLOAT"),
            PropertyType(
                name="status",
                base_type="STRING",
                constraints={"allowed_values": ["active", "lapsed", "cancelled", "expired"]},
            ),
            PropertyType(name="created_at", base_type="DATETIME"),
        ],
    )


def _claim() -> ObjectType:
    return ObjectType(
        api_name="Claim",
        description="An insurance claim filed against a policy",
        properties=[
            PropertyType(
                name="claim_id", base_type="STRING", is_required=True, is_primary_key=True
            ),
            PropertyType(
                name="claim_type",
                base_type="STRING",
                is_required=True,
                constraints={
                    "allowed_values": [
                        "collision",
                        "liability",
                        "property",
                        "bodily_injury",
                        "comprehensive",
                    ]
                },
            ),
            PropertyType(name="date_of_loss", base_type="DATETIME", is_required=True),
            PropertyType(name="date_filed", base_type="DATETIME", is_required=True),
            PropertyType(name="description", base_type="STRING"),
            PropertyType(name="amount_claimed", base_type="FLOAT", is_required=True),
            PropertyType(name="amount_approved", base_type="FLOAT"),
            PropertyType(name="amount_paid", base_type="FLOAT"),
            PropertyType(
                name="status",
                base_type="STRING",
                constraints={
                    "allowed_values": [
                        "filed",
                        "triage",
                        "under_review",
                        "approved",
                        "denied",
                        "paid",
                        "appealed",
                        "closed",
                    ]
                },
            ),
            PropertyType(
                name="priority",
                base_type="STRING",
                constraints={"allowed_values": ["low", "medium", "high", "urgent"]},
            ),
            PropertyType(name="assigned_adjuster", base_type="STRING"),
            PropertyType(name="created_at", base_type="DATETIME"),
        ],
    )


def _investigation() -> ObjectType:
    return ObjectType(
        api_name="Investigation",
        description="A fraud or claims investigation tied to a claim",
        properties=[
            PropertyType(
                name="investigation_id",
                base_type="STRING",
                is_required=True,
                is_primary_key=True,
            ),
            PropertyType(name="investigator", base_type="STRING", is_required=True),
            PropertyType(
                name="investigation_type",
                base_type="STRING",
                is_required=True,
                constraints={"allowed_values": ["routine", "siu_referral", "fraud_suspected"]},
            ),
            PropertyType(name="findings", base_type="STRING"),
            PropertyType(
                name="recommendation",
                base_type="STRING",
                constraints={
                    "allowed_values": [
                        "approve",
                        "deny",
                        "refer_to_siu",
                        "request_more_info",
                    ]
                },
            ),
            PropertyType(
                name="status",
                base_type="STRING",
                constraints={"allowed_values": ["open", "in_progress", "completed", "escalated"]},
            ),
            PropertyType(name="started_at", base_type="DATETIME"),
            PropertyType(name="completed_at", base_type="DATETIME"),
            PropertyType(name="created_at", base_type="DATETIME"),
        ],
    )


def _claim_payment() -> ObjectType:
    return ObjectType(
        api_name="ClaimPayment",
        description="A payment disbursed for an approved insurance claim",
        properties=[
            PropertyType(
                name="payment_id", base_type="STRING", is_required=True, is_primary_key=True
            ),
            PropertyType(name="amount", base_type="FLOAT", is_required=True),
            PropertyType(
                name="payment_method",
                base_type="STRING",
                is_required=True,
                constraints={"allowed_values": ["check", "ach", "wire"]},
            ),
            PropertyType(name="payee", base_type="STRING", is_required=True),
            PropertyType(name="payment_date", base_type="DATETIME"),
            PropertyType(name="check_number", base_type="STRING"),
            PropertyType(
                name="status",
                base_type="STRING",
                constraints={"allowed_values": ["pending", "processed", "cleared", "voided"]},
            ),
            PropertyType(name="created_at", base_type="DATETIME"),
        ],
    )


def _subrogation() -> ObjectType:
    return ObjectType(
        api_name="Subrogation",
        description="A subrogation record for recovering payments from at-fault third parties",
        properties=[
            PropertyType(
                name="subrogation_id",
                base_type="STRING",
                is_required=True,
                is_primary_key=True,
            ),
            PropertyType(name="at_fault_party", base_type="STRING", is_required=True),
            PropertyType(name="at_fault_insurer", base_type="STRING"),
            PropertyType(name="amount_sought", base_type="FLOAT", is_required=True),
            PropertyType(name="amount_recovered", base_type="FLOAT"),
            PropertyType(
                name="status",
                base_type="STRING",
                constraints={
                    "allowed_values": [
                        "identified",
                        "demand_sent",
                        "negotiating",
                        "settled",
                        "litigating",
                        "closed",
                    ]
                },
            ),
            PropertyType(name="demand_sent_date", base_type="DATETIME"),
            PropertyType(name="created_at", base_type="DATETIME"),
        ],
    )
