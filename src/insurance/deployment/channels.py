"""Insurance release channels — staged deployment pipeline.

3 channels: canary → staging → production
"""

from __future__ import annotations

from aios.hub.channels import (
    ChannelStage,
    ReleaseChannel,
    ReleaseChannelManager,
)

from insurance.config import (
    CANARY_BAKE_MINUTES,
    PRODUCTION_BAKE_MINUTES,
    STAGING_BAKE_MINUTES,
)
from insurance.deployment.spokes import get_spokes


def get_release_channels() -> list[ReleaseChannel]:
    """Return all 3 insurance release channels."""
    return [
        ReleaseChannel(
            name="canary",
            stage=ChannelStage.CANARY,
            description="Canary channel — pilot region only",
            bake_time_minutes=CANARY_BAKE_MINUTES,
            min_healthy_spokes=1,
        ),
        ReleaseChannel(
            name="staging",
            stage=ChannelStage.STAGING,
            description="Internal staging",
            promote_from="canary",
            bake_time_minutes=STAGING_BAKE_MINUTES,
            min_healthy_spokes=1,
        ),
        ReleaseChannel(
            name="production",
            stage=ChannelStage.PRODUCTION,
            description="Regional production channel (maintenance window required)",
            promote_from="staging",
            bake_time_minutes=PRODUCTION_BAKE_MINUTES,
            min_healthy_spokes=3,
        ),
    ]


def get_spoke_channel_map() -> dict[str, str]:
    """Return a mapping of spoke name → channel name."""
    mapping: dict[str, str] = {}
    for spoke in get_spokes():
        if spoke.name == "region-pilot":
            mapping[spoke.name] = "canary"
        elif spoke.name == "staging-internal":
            mapping[spoke.name] = "staging"
        elif spoke.environment == "production":
            mapping[spoke.name] = "production"
    return mapping


def setup_channel_manager() -> ReleaseChannelManager:
    """Create and configure a ReleaseChannelManager with insurance channels and subscriptions."""
    manager = ReleaseChannelManager()

    # Register channels
    for channel in get_release_channels():
        manager.register_channel(channel)

    # Subscribe spokes to their channels
    spoke_map = get_spoke_channel_map()
    for spoke in get_spokes():
        channel_name = spoke_map.get(spoke.name)
        if channel_name:
            manager.subscribe_spoke(spoke.id, spoke.name, channel_name)

    return manager
