"""Insurance deployment constraints — safety gates for production deployments.

Production requires maintenance window and manual approval.
Canary/staging uses lighter constraints (no window, no manual approval).
"""

from __future__ import annotations

from aios.hub.constraints.models import ConstraintType, DeploymentConstraint

from insurance.config import MAINTENANCE_WINDOW_END, MAINTENANCE_WINDOW_START


def get_production_constraints() -> list[DeploymentConstraint]:
    """Return deployment constraints for production spokes."""
    return [
        DeploymentConstraint(
            name="health-gate",
            description="Spoke must report HEALTHY status",
            constraint_type=ConstraintType.HEALTH_CHECK,
            config={"min_status": "HEALTHY"},
        ),
        DeploymentConstraint(
            name="no-concurrent",
            description="No other deployment in progress",
            constraint_type=ConstraintType.NO_CONCURRENT_DEPLOY,
        ),
        DeploymentConstraint(
            name="night-only",
            description=(
                f"Production: deploy only between "
                f"{MAINTENANCE_WINDOW_START}:00-{MAINTENANCE_WINDOW_END}:00 UTC"
            ),
            constraint_type=ConstraintType.MAINTENANCE_WINDOW,
            config={
                "start_hour": MAINTENANCE_WINDOW_START,
                "end_hour": MAINTENANCE_WINDOW_END,
            },
        ),
        DeploymentConstraint(
            name="ops-signoff",
            description="Requires manual approval from operations team",
            constraint_type=ConstraintType.MANUAL_APPROVAL,
        ),
    ]


def get_canary_staging_constraints() -> list[DeploymentConstraint]:
    """Return deployment constraints for canary and staging spokes.

    Lighter than production: no maintenance window, no manual approval.
    """
    return [
        DeploymentConstraint(
            name="health-gate",
            description="Spoke must be at least DEGRADED",
            constraint_type=ConstraintType.HEALTH_CHECK,
            config={"min_status": "DEGRADED"},
        ),
        DeploymentConstraint(
            name="no-concurrent",
            description="No other deployment in progress",
            constraint_type=ConstraintType.NO_CONCURRENT_DEPLOY,
        ),
    ]
