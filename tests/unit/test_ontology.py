"""Tests for insurance ontology definitions.

Validates that all 5 object types and 5 link types are correctly
defined and follow AIOS conventions.
"""

from __future__ import annotations

import pytest
from aios.ontology.engine.computed import compute_properties

from insurance.ontology.computed import (
    get_all_computed_properties,
    get_claim_computed_properties,
    get_subrogation_computed_properties,
)
from insurance.ontology.interfaces import get_interface_implementations, get_interfaces
from insurance.ontology.link_types import get_link_types
from insurance.ontology.object_types import get_object_types

# ---------------------------------------------------------------------------
# Object Types
# ---------------------------------------------------------------------------


class TestObjectTypes:
    def test_count(self):
        assert len(get_object_types()) == 5

    def test_all_have_api_names(self):
        for ot in get_object_types():
            assert ot.api_name, f"Object type missing api_name: {ot}"

    def test_all_have_primary_keys(self):
        for ot in get_object_types():
            pk = ot.primary_key_property
            assert pk is not None, f"{ot.api_name} missing primary key"

    def test_expected_types_present(self):
        names = {ot.api_name for ot in get_object_types()}
        expected = {"Policy", "Claim", "Investigation", "ClaimPayment", "Subrogation"}
        assert names == expected

    def test_policy_has_required_properties(self):
        policy = next(ot for ot in get_object_types() if ot.api_name == "Policy")
        required = {p.name for p in policy.required_properties}
        assert "policy_number" in required
        assert "holder_name" in required
        assert "holder_ssn" in required
        assert "effective_date" in required

    def test_policy_type_constraints(self):
        policy = next(ot for ot in get_object_types() if ot.api_name == "Policy")
        policy_type = policy.get_property("policy_type")
        assert policy_type is not None
        allowed = policy_type.constraints["allowed_values"]
        assert "auto" in allowed
        assert "home" in allowed
        assert "life" in allowed
        assert "health" in allowed
        assert "commercial" in allowed

    def test_claim_status_constraints(self):
        claim = next(ot for ot in get_object_types() if ot.api_name == "Claim")
        status = claim.get_property("status")
        assert status is not None
        allowed = status.constraints["allowed_values"]
        assert "filed" in allowed
        assert "triage" in allowed
        assert "under_review" in allowed
        assert "approved" in allowed
        assert "denied" in allowed
        assert "paid" in allowed
        assert "appealed" in allowed
        assert "closed" in allowed

    def test_claim_has_financial_fields(self):
        claim = next(ot for ot in get_object_types() if ot.api_name == "Claim")
        assert claim.get_property("amount_claimed") is not None
        assert claim.get_property("amount_approved") is not None
        assert claim.get_property("amount_paid") is not None

    def test_investigation_type_constraints(self):
        inv = next(ot for ot in get_object_types() if ot.api_name == "Investigation")
        inv_type = inv.get_property("investigation_type")
        assert inv_type is not None
        allowed = inv_type.constraints["allowed_values"]
        assert "routine" in allowed
        assert "siu_referral" in allowed
        assert "fraud_suspected" in allowed

    def test_payment_method_constraints(self):
        payment = next(ot for ot in get_object_types() if ot.api_name == "ClaimPayment")
        method = payment.get_property("payment_method")
        assert method is not None
        allowed = method.constraints["allowed_values"]
        assert "check" in allowed
        assert "ach" in allowed
        assert "wire" in allowed

    def test_subrogation_status_constraints(self):
        sub = next(ot for ot in get_object_types() if ot.api_name == "Subrogation")
        status = sub.get_property("status")
        assert status is not None
        allowed = status.constraints["allowed_values"]
        assert "identified" in allowed
        assert "demand_sent" in allowed
        assert "negotiating" in allowed
        assert "settled" in allowed
        assert "litigating" in allowed
        assert "closed" in allowed


# ---------------------------------------------------------------------------
# Link Types
# ---------------------------------------------------------------------------


class TestLinkTypes:
    def test_count(self):
        assert len(get_link_types()) == 5

    def test_all_have_api_names(self):
        for lt in get_link_types():
            assert lt.api_name, f"Link type missing api_name: {lt}"

    def test_all_reference_valid_types(self):
        valid_types = {ot.api_name for ot in get_object_types()}
        for lt in get_link_types():
            assert lt.source_type in valid_types, (
                f"Link {lt.api_name} source_type '{lt.source_type}' not a valid ObjectType"
            )
            assert lt.target_type in valid_types, (
                f"Link {lt.api_name} target_type '{lt.target_type}' not a valid ObjectType"
            )

    def test_policy_claim_link(self):
        link = next(lt for lt in get_link_types() if lt.api_name == "policy_has_claim")
        assert link.source_type == "Policy"
        assert link.target_type == "Claim"
        assert link.cardinality.value == "ONE_TO_MANY"

    def test_claim_subrogation_link(self):
        link = next(lt for lt in get_link_types() if lt.api_name == "claim_has_subrogation")
        assert link.cardinality.value == "ONE_TO_ONE"

    def test_investigation_subrogation_link(self):
        link = next(
            lt for lt in get_link_types() if lt.api_name == "investigation_triggers_subrogation"
        )
        assert link.cardinality.value == "ONE_TO_ONE"


# ---------------------------------------------------------------------------
# Computed Properties
# ---------------------------------------------------------------------------


class TestComputedProperties:
    def test_claim_has_computed_defs(self):
        defs = get_claim_computed_properties()
        assert len(defs) == 2
        names = {d.name for d in defs}
        assert "outstanding_balance" in names
        assert "days_since_filed" in names

    def test_subrogation_has_recovery_rate(self):
        defs = get_subrogation_computed_properties()
        assert len(defs) == 1
        assert defs[0].name == "recovery_rate"

    def test_all_computed_properties_keyed_by_type(self):
        all_defs = get_all_computed_properties()
        assert "Claim" in all_defs
        assert "Subrogation" in all_defs

    def test_outstanding_balance_evaluation(self):
        defs = get_claim_computed_properties()
        balance_def = next(d for d in defs if d.name == "outstanding_balance")
        result = compute_properties(
            {"amount_claimed": 50000.0, "amount_paid": 30000.0},
            [balance_def],
        )
        assert result["outstanding_balance"] == 20000.0

    def test_recovery_rate_evaluation(self):
        defs = get_subrogation_computed_properties()
        result = compute_properties(
            {"amount_recovered": 15000.0, "amount_sought": 25000.0},
            defs,
        )
        assert result["recovery_rate"] == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------


class TestInterfaces:
    def test_interface_count(self):
        assert len(get_interfaces()) == 1

    def test_has_status_interface(self):
        ifaces = get_interfaces()
        has_status = next(i for i in ifaces if i.api_name == "HasStatus")
        assert len(has_status.properties) == 1
        assert has_status.properties[0].name == "status"

    def test_implementations_reference_valid_types(self):
        valid_types = {ot.api_name for ot in get_object_types()}
        impls = get_interface_implementations()
        for iface_name, implementing_types in impls.items():
            for type_name in implementing_types:
                assert type_name in valid_types, (
                    f"Interface {iface_name} references unknown type '{type_name}'"
                )

    def test_all_types_implement_has_status(self):
        impls = get_interface_implementations()
        has_status_types = set(impls["HasStatus"])
        expected = {"Policy", "Claim", "Investigation", "ClaimPayment", "Subrogation"}
        assert has_status_types == expected
