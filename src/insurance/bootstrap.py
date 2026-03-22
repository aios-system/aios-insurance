"""Insurance Master Bootstrap — registers all configuration with AIOS.

This is the single entry point for deploying the Insurance solution.
It registers ontology types, link types, and action types.

Usage:
    from insurance.bootstrap import bootstrap_insurance
    result = await bootstrap_insurance(session_factory)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from aios.ontology.store.action_type_repo import ActionTypeRepository
from aios.ontology.store.link_type_repo import LinkTypeRepository
from aios.ontology.store.object_type_repo import ObjectTypeRepository

from insurance.agents.claims_triage import get_triage_claim_action
from insurance.agents.fraud_detection import get_flag_fraud_action
from insurance.ontology.link_types import get_link_types
from insurance.ontology.object_types import get_object_types

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = structlog.get_logger()


async def bootstrap_insurance(
    session_factory: async_sessionmaker[AsyncSession],
) -> dict:
    """Register all Insurance configuration in the AIOS ontology.

    This function is idempotent — running it twice will skip
    already-registered types and return a summary.

    Returns:
        Summary dict with created/skipped counts.
    """
    ot_repo = ObjectTypeRepository(session_factory)
    lt_repo = LinkTypeRepository(session_factory)
    at_repo = ActionTypeRepository(session_factory)

    created_types: list[str] = []
    created_links: list[str] = []
    created_actions: list[str] = []
    skipped: list[str] = []

    # --- Object Types ---
    for obj_type in get_object_types():
        if await ot_repo.exists(obj_type.api_name):
            skipped.append(f"type:{obj_type.api_name}")
            continue
        await ot_repo.create(obj_type)
        created_types.append(obj_type.api_name)
        logger.info("insurance_type_registered", api_name=obj_type.api_name)

    # --- Link Types ---
    for link_type in get_link_types():
        try:
            await lt_repo.get_by_name(link_type.api_name)
            skipped.append(f"link:{link_type.api_name}")
        except Exception:
            await lt_repo.create(link_type)
            created_links.append(link_type.api_name)
            logger.info("insurance_link_registered", api_name=link_type.api_name)

    # --- Action Types ---
    action_types = [
        get_triage_claim_action(),
        get_flag_fraud_action(),
    ]
    for action_type in action_types:
        try:
            await at_repo.get_by_name(action_type.api_name)
            skipped.append(f"action:{action_type.api_name}")
        except Exception:
            await at_repo.create(action_type)
            created_actions.append(action_type.api_name)
            logger.info("insurance_action_registered", api_name=action_type.api_name)

    summary = {
        "created_types": created_types,
        "created_links": created_links,
        "created_actions": created_actions,
        "skipped": skipped,
        "total_created": len(created_types) + len(created_links) + len(created_actions),
        "total_skipped": len(skipped),
    }
    logger.info("insurance_bootstrap_complete", **summary)
    return summary
