"""Tests for insurance security policies and markings.

Validates that the 5 security policies correctly protect claims data
based on user markings.
"""

from __future__ import annotations

from aios.auth.object_policies import (
    apply_all_policies,
    apply_column_mask,
    apply_row_filter,
)

from insurance.security.markings import get_markings_for_user, get_user_markings
from insurance.security.policies import get_security_policies

# ---------------------------------------------------------------------------
# Markings
# ---------------------------------------------------------------------------


class TestMarkings:
    def test_six_users_defined(self):
        assert len(get_user_markings()) == 6

    def test_adjuster_has_claims_and_pii(self):
        markings = get_markings_for_user("adjuster-williams")
        assert "CLAIMS" in markings
        assert "PII" in markings

    def test_senior_adjuster_has_financial(self):
        markings = get_markings_for_user("senior-adjuster-garcia")
        assert "CLAIMS" in markings
        assert "PII" in markings
        assert "FINANCIAL" in markings

    def test_siu_has_restricted(self):
        markings = get_markings_for_user("siu-investigator-chen")
        assert "CLAIMS" in markings
        assert "RESTRICTED" in markings

    def test_billing_only_financial(self):
        markings = get_markings_for_user("billing-clerk-patel")
        assert markings == ["FINANCIAL"]

    def test_unknown_user_empty(self):
        markings = get_markings_for_user("nonexistent-user")
        assert markings == []


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


class TestPolicies:
    def test_five_policies_defined(self):
        assert len(get_security_policies()) == 5

    def test_all_policies_have_names(self):
        for p in get_security_policies():
            assert p.name, "Policy missing name"

    def test_all_policies_target_valid_types(self):
        valid = {"Policy", "Claim", "Investigation", "ClaimPayment"}
        for p in get_security_policies():
            assert p.object_type in valid, (
                f"Policy '{p.name}' targets unknown type '{p.object_type}'"
            )

    def test_all_policies_have_required_markings(self):
        """Policies with empty required_markings are auto-bypassed — all ours must have markings."""
        for p in get_security_policies():
            assert len(p.required_markings) > 0, (
                f"Policy '{p.name}' has empty required_markings (would be auto-bypassed)"
            )


# ---------------------------------------------------------------------------
# Policy Application — Column Masking
# ---------------------------------------------------------------------------


class TestColumnMasking:
    def _policy_obj(self):
        return {
            "properties": {
                "policy_number": "POL-001",
                "holder_name": "John Doe",
                "holder_ssn": "123-45-6789",
                "holder_email": "john@example.com",
                "policy_type": "auto",
                "status": "active",
            }
        }

    def _claim_obj(self):
        return {
            "properties": {
                "claim_id": "CLM-001",
                "policy_number": "POL-001",
                "amount_claimed": 5000.0,
                "amount_approved": 4500.0,
                "amount_paid": 4500.0,
                "status": "paid",
            }
        }

    def _payment_obj(self):
        return {
            "properties": {
                "payment_id": "PAY-001",
                "claim_id": "CLM-001",
                "amount": 4500.0,
                "check_number": "CHK-98765",
                "payment_date": "2026-03-01",
            }
        }

    def test_adjuster_sees_pii(self):
        """Adjuster with PII marking should see policyholder name, SSN, and email."""
        policies = [p for p in get_security_policies() if p.object_type == "Policy"]
        markings = get_markings_for_user("adjuster-williams")
        result = apply_column_mask(self._policy_obj(), policies, markings)
        assert result["properties"]["holder_name"] == "John Doe"
        assert result["properties"]["holder_ssn"] == "123-45-6789"
        assert result["properties"]["holder_email"] == "john@example.com"

    def test_billing_cannot_see_pii(self):
        """Billing clerk without PII marking should have PII fields redacted."""
        policies = [p for p in get_security_policies() if p.object_type == "Policy"]
        markings = get_markings_for_user("billing-clerk-patel")
        result = apply_column_mask(self._policy_obj(), policies, markings)
        assert result["properties"]["holder_name"] == "***REDACTED***"
        assert result["properties"]["holder_ssn"] == "***REDACTED***"
        assert result["properties"]["holder_email"] == "***REDACTED***"

    def test_senior_adjuster_sees_financial(self):
        """Senior adjuster with FINANCIAL marking should see claim amounts."""
        policies = [p for p in get_security_policies() if p.object_type == "Claim"]
        markings = get_markings_for_user("senior-adjuster-garcia")
        result = apply_column_mask(self._claim_obj(), policies, markings)
        assert result["properties"]["amount_claimed"] == 5000.0
        assert result["properties"]["amount_approved"] == 4500.0
        assert result["properties"]["amount_paid"] == 4500.0

    def test_billing_sees_payment_amounts(self):
        """Billing clerk with FINANCIAL marking should see ClaimPayment amounts."""
        policies = [p for p in get_security_policies() if p.object_type == "ClaimPayment"]
        markings = get_markings_for_user("billing-clerk-patel")
        result = apply_column_mask(self._payment_obj(), policies, markings)
        assert result["properties"]["amount"] == 4500.0
        assert result["properties"]["check_number"] == "CHK-98765"

    def test_adjuster_cannot_see_financial(self):
        """Adjuster without FINANCIAL marking should have claim amounts hidden (None)."""
        policies = [p for p in get_security_policies() if p.object_type == "Claim"]
        markings = get_markings_for_user("adjuster-williams")
        result = apply_column_mask(self._claim_obj(), policies, markings)
        assert result["properties"]["amount_claimed"] is None
        assert result["properties"]["amount_approved"] is None
        assert result["properties"]["amount_paid"] is None


# ---------------------------------------------------------------------------
# Policy Application — Row Filtering
# ---------------------------------------------------------------------------


class TestRowFiltering:
    def _fraud_investigation(self):
        return {
            "properties": {
                "investigation_id": "INV-001",
                "claim_id": "CLM-001",
                "investigation_type": "fraud_suspected",
                "findings": "Suspicious activity detected",
                "recommendation": "Deny claim",
            }
        }

    def _routine_investigation(self):
        return {
            "properties": {
                "investigation_id": "INV-002",
                "claim_id": "CLM-002",
                "investigation_type": "routine",
                "findings": "All documents verified",
                "recommendation": "Approve claim",
            }
        }

    def test_siu_sees_fraud_investigations(self):
        """SIU investigator with RESTRICTED marking sees all investigations (filter bypassed)."""
        row_filter_policies = [
            p
            for p in get_security_policies()
            if p.object_type == "Investigation" and p.policy_type.value == "ROW_FILTER"
        ]
        markings = get_markings_for_user("siu-investigator-chen")
        investigations = [self._fraud_investigation(), self._routine_investigation()]
        for policy in row_filter_policies:
            investigations = apply_row_filter(investigations, policy, markings)
        assert len(investigations) == 2

    def test_non_siu_filtered(self):
        """Adjuster without RESTRICTED marking sees only fraud_suspected investigations."""
        row_filter_policies = [
            p
            for p in get_security_policies()
            if p.object_type == "Investigation" and p.policy_type.value == "ROW_FILTER"
        ]
        markings = get_markings_for_user("adjuster-williams")
        investigations = [self._fraud_investigation(), self._routine_investigation()]
        for policy in row_filter_policies:
            investigations = apply_row_filter(investigations, policy, markings)
        assert len(investigations) == 1
        assert investigations[0]["properties"]["investigation_type"] == "fraud_suspected"


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_apply_all_policies(self):
        """Apply all policies to Policy objects as billing-clerk-patel (FINANCIAL only).

        PII fields should be redacted; objects are still returned.
        """
        policy_objects = [
            {
                "properties": {
                    "policy_number": "POL-001",
                    "holder_name": "John Doe",
                    "holder_ssn": "123-45-6789",
                    "holder_email": "john@example.com",
                    "policy_type": "auto",
                    "status": "active",
                }
            },
            {
                "properties": {
                    "policy_number": "POL-002",
                    "holder_name": "Jane Smith",
                    "holder_ssn": "987-65-4321",
                    "holder_email": "jane@example.com",
                    "policy_type": "home",
                    "status": "active",
                }
            },
        ]
        policies = [p for p in get_security_policies() if p.object_type == "Policy"]
        markings = get_markings_for_user("billing-clerk-patel")
        result = apply_all_policies(policy_objects, policies, markings)
        # Both Policy objects should be returned (no row filter on Policy)
        assert len(result) == 2
        # PII fields should be redacted for billing-clerk-patel (no PII marking)
        for obj in result:
            assert obj["properties"]["holder_name"] == "***REDACTED***"
            assert obj["properties"]["holder_ssn"] == "***REDACTED***"
            assert obj["properties"]["holder_email"] == "***REDACTED***"
