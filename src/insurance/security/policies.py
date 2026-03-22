"""Insurance security policies — marking-based access control for claims data.

5 policies covering PII protection, financial amounts, investigation access,
claims financial isolation, and SIU row filtering.
"""

from __future__ import annotations

from aios.auth.object_policies import (
    MaskingStrategy,
    ObjectSecurityPolicy,
    PolicyType,
)

from insurance.config import MARKING_FINANCIAL, MARKING_PII, MARKING_RESTRICTED


def get_security_policies() -> list[ObjectSecurityPolicy]:
    """Return all 5 insurance security policies."""
    return [
        _pii_protection(),
        _financial_amounts(),
        _investigation_restricted(),
        _claims_financial_isolation(),
        _siu_row_filter(),
    ]


def _pii_protection() -> ObjectSecurityPolicy:
    """Protect policyholder PII — redacted for users without PII marking."""
    return ObjectSecurityPolicy(
        name="pii-protection",
        description="Redact policyholder identifying information for users without PII marking",
        object_type="Policy",
        policy_type=PolicyType.COLUMN_MASK,
        required_markings=[MARKING_PII],
        masked_properties=["holder_name", "holder_ssn", "holder_email"],
        masking_strategy=MaskingStrategy.REDACT,
    )


def _financial_amounts() -> ObjectSecurityPolicy:
    """Hide payment amounts from non-financial users."""
    return ObjectSecurityPolicy(
        name="financial-amounts",
        description="Hide claim payment amounts and check numbers from non-financial staff",
        object_type="ClaimPayment",
        policy_type=PolicyType.COLUMN_MASK,
        required_markings=[MARKING_FINANCIAL],
        masked_properties=["amount", "check_number"],
        masking_strategy=MaskingStrategy.HIDE,
    )


def _investigation_restricted() -> ObjectSecurityPolicy:
    """Redact investigation findings from users without RESTRICTED marking."""
    return ObjectSecurityPolicy(
        name="investigation-restricted",
        description="Redact investigation findings and recommendations for non-SIU users",
        object_type="Investigation",
        policy_type=PolicyType.COLUMN_MASK,
        required_markings=[MARKING_RESTRICTED],
        masked_properties=["findings", "recommendation"],
        masking_strategy=MaskingStrategy.REDACT,
    )


def _claims_financial_isolation() -> ObjectSecurityPolicy:
    """Hide claim dollar amounts from non-financial users."""
    return ObjectSecurityPolicy(
        name="claims-financial-isolation",
        description="Hide claim financial amounts from users without FINANCIAL marking",
        object_type="Claim",
        policy_type=PolicyType.COLUMN_MASK,
        required_markings=[MARKING_FINANCIAL],
        masked_properties=["amount_claimed", "amount_approved", "amount_paid"],
        masking_strategy=MaskingStrategy.HIDE,
    )


def _siu_row_filter() -> ObjectSecurityPolicy:
    """Only show fraud-suspected investigations to SIU users."""
    return ObjectSecurityPolicy(
        name="siu-row-filter",
        description="Only show fraud-suspected investigations to users with RESTRICTED marking",
        object_type="Investigation",
        policy_type=PolicyType.ROW_FILTER,
        required_markings=[MARKING_RESTRICTED],
        row_filter_conditions=[
            {"field": "investigation_type", "operator": "eq", "value": "fraud_suspected"}
        ],
    )
