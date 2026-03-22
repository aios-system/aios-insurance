"""Tests for insurance deployment configuration.

Validates spoke definitions, release channels, channel subscriptions,
and deployment constraints for production vs canary/staging.
"""

from __future__ import annotations

from aios.hub.channels import ChannelStage
from aios.hub.constraints.models import ConstraintType

from insurance.deployment.channels import (
    get_release_channels,
    get_spoke_channel_map,
    setup_channel_manager,
)
from insurance.deployment.constraints import (
    get_canary_staging_constraints,
    get_production_constraints,
)
from insurance.deployment.spokes import get_production_spokes, get_spokes

# ---------------------------------------------------------------------------
# Spokes
# ---------------------------------------------------------------------------


class TestSpokes:
    def test_total_spoke_count(self):
        """2 non-production + 6 production = 8."""
        spokes = get_spokes()
        assert len(spokes) == 8

    def test_production_count(self):
        assert len(get_production_spokes()) == 6

    def test_all_spokes_have_names(self):
        for s in get_spokes():
            assert s.name, "Spoke missing name"

    def test_production_spokes_are_production(self):
        for s in get_production_spokes():
            assert s.environment == "production"

    def test_staging_spoke_exists(self):
        staging = [s for s in get_spokes() if s.name == "staging-internal"]
        assert len(staging) == 1
        assert staging[0].environment == "staging"

    def test_canary_spoke_exists(self):
        canary = [s for s in get_spokes() if s.name == "region-pilot"]
        assert len(canary) == 1
        assert canary[0].environment == "canary"


# ---------------------------------------------------------------------------
# Release Channels
# ---------------------------------------------------------------------------


class TestReleaseChannels:
    def test_three_channels_defined(self):
        assert len(get_release_channels()) == 3

    def test_channel_names(self):
        names = {c.name for c in get_release_channels()}
        assert names == {"canary", "staging", "production"}

    def test_canary_is_root(self):
        canary = next(c for c in get_release_channels() if c.name == "canary")
        assert canary.stage == ChannelStage.CANARY
        assert canary.promote_from == ""

    def test_production_promotes_from_staging(self):
        production = next(c for c in get_release_channels() if c.name == "production")
        assert production.stage == ChannelStage.PRODUCTION
        assert production.promote_from == "staging"


# ---------------------------------------------------------------------------
# Spoke-Channel Mapping
# ---------------------------------------------------------------------------


class TestSpokeChannelMap:
    def test_pilot_maps_to_canary(self):
        mapping = get_spoke_channel_map()
        assert mapping["region-pilot"] == "canary"

    def test_staging_maps_to_staging(self):
        mapping = get_spoke_channel_map()
        assert mapping["staging-internal"] == "staging"

    def test_regions_map_to_production(self):
        mapping = get_spoke_channel_map()
        production_spokes = get_production_spokes()
        for spoke in production_spokes:
            assert mapping[spoke.name] == "production"


# ---------------------------------------------------------------------------
# Channel Manager
# ---------------------------------------------------------------------------


class TestChannelManager:
    def test_setup_registers_all_channels(self):
        manager = setup_channel_manager()
        assert len(manager.list_channels()) == 3

    def test_canary_has_one_subscriber(self):
        manager = setup_channel_manager()
        subs = manager.get_channel_subscribers("canary")
        assert len(subs) == 1
        assert subs[0].spoke_name == "region-pilot"

    def test_production_has_six_subscribers(self):
        manager = setup_channel_manager()
        subs = manager.get_channel_subscribers("production")
        assert len(subs) == 6

    def test_promote_canary_to_staging(self):
        manager = setup_channel_manager()
        # Publish to canary first
        manager.publish_to_channel("canary", "mf-1", "1.0.0")
        # Promote to staging
        result = manager.promote("canary", "staging")
        assert result.success
        staging = manager.get_channel("staging")
        assert staging.current_manifest_version == "1.0.0"


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------


class TestConstraints:
    def test_production_has_four_constraints(self):
        assert len(get_production_constraints()) == 4

    def test_production_has_maintenance_window(self):
        constraints = get_production_constraints()
        window = next(
            c for c in constraints if c.constraint_type == ConstraintType.MAINTENANCE_WINDOW
        )
        assert window.config["start_hour"] == 2
        assert window.config["end_hour"] == 5

    def test_production_requires_manual_approval(self):
        constraints = get_production_constraints()
        approval = [c for c in constraints if c.constraint_type == ConstraintType.MANUAL_APPROVAL]
        assert len(approval) == 1

    def test_canary_staging_has_two_constraints(self):
        assert len(get_canary_staging_constraints()) == 2

    def test_canary_staging_no_maintenance_window(self):
        constraints = get_canary_staging_constraints()
        windows = [c for c in constraints if c.constraint_type == ConstraintType.MAINTENANCE_WINDOW]
        assert len(windows) == 0

    def test_canary_staging_accepts_degraded_health(self):
        constraints = get_canary_staging_constraints()
        health = next(c for c in constraints if c.constraint_type == ConstraintType.HEALTH_CHECK)
        assert health.config["min_status"] == "DEGRADED"
