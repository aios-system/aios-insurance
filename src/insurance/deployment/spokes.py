"""Insurance spoke definitions — 8 regional deployment targets."""

from __future__ import annotations

from aios.hub.models import Spoke


def get_spokes() -> list[Spoke]:
    """Return all insurance spoke definitions."""
    return [
        Spoke(
            name="staging-internal",
            description="Internal staging environment",
            environment="staging",
            labels={"type": "staging"},
        ),
        Spoke(
            name="region-pilot",
            description="Pilot region for canary deployments",
            environment="canary",
            labels={"type": "region", "region": "pilot"},
        ),
        Spoke(
            name="region-northeast",
            description="Northeast US production",
            environment="production",
            labels={"type": "region", "region": "northeast"},
        ),
        Spoke(
            name="region-southeast",
            description="Southeast US production",
            environment="production",
            labels={"type": "region", "region": "southeast"},
        ),
        Spoke(
            name="region-midwest",
            description="Midwest US production",
            environment="production",
            labels={"type": "region", "region": "midwest"},
        ),
        Spoke(
            name="region-west",
            description="West US production",
            environment="production",
            labels={"type": "region", "region": "west"},
        ),
        Spoke(
            name="region-southwest",
            description="Southwest US production",
            environment="production",
            labels={"type": "region", "region": "southwest"},
        ),
        Spoke(
            name="region-northwest",
            description="Northwest US production",
            environment="production",
            labels={"type": "region", "region": "northwest"},
        ),
    ]


def get_production_spokes() -> list[Spoke]:
    """Return only production spoke definitions."""
    return [s for s in get_spokes() if s.environment == "production"]
