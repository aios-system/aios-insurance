"""Insurance user markings — classification-based access control.

Markings determine what data each user role can see.
A user must have ALL required markings on a policy to bypass it.
"""

from __future__ import annotations

from aios.auth.object_policies import UserMarkings

from insurance.config import (
    MARKING_CLAIMS,
    MARKING_FINANCIAL,
    MARKING_MANAGEMENT,
    MARKING_PII,
    MARKING_RESTRICTED,
)


def get_user_markings() -> dict[str, UserMarkings]:
    """Return the insurance user markings map.

    Keys are user IDs. Values are UserMarkings with their classification labels.
    """
    return {
        "adjuster-williams": UserMarkings(
            user_id="adjuster-williams",
            markings=[MARKING_CLAIMS, MARKING_PII],
        ),
        "senior-adjuster-garcia": UserMarkings(
            user_id="senior-adjuster-garcia",
            markings=[MARKING_CLAIMS, MARKING_PII, MARKING_FINANCIAL],
        ),
        "siu-investigator-chen": UserMarkings(
            user_id="siu-investigator-chen",
            markings=[MARKING_CLAIMS, MARKING_RESTRICTED],
        ),
        "billing-clerk-patel": UserMarkings(
            user_id="billing-clerk-patel",
            markings=[MARKING_FINANCIAL],
        ),
        "manager-thompson": UserMarkings(
            user_id="manager-thompson",
            markings=[MARKING_CLAIMS, MARKING_PII, MARKING_FINANCIAL, MARKING_MANAGEMENT],
        ),
        "auditor-external": UserMarkings(
            user_id="auditor-external",
            markings=[MARKING_CLAIMS, MARKING_FINANCIAL],
        ),
    }


def get_markings_for_user(user_id: str) -> list[str]:
    """Get the markings list for a specific user."""
    markings_map = get_user_markings()
    user = markings_map.get(user_id)
    return user.markings if user else []
