"""Insurance data lineage graph — audit trail for regulatory compliance.

Maps the data flow from source systems (Guidewire, Duck Creek, ISO) through
bronze/silver/gold layers to the adjuster, management, and SIU dashboards.
"""

from __future__ import annotations

from aios.data_platform.lineage.models import (
    LineageEdge,
    LineageEdgeType,
    LineageNode,
    LineageNodeType,
)
from aios.data_platform.lineage.tracker import LineageTracker


def build_insurance_lineage() -> LineageTracker:
    """Build and return the insurance data lineage graph.

    Graph structure (13 nodes, 12 edges):

        guidewire-claims (DATA_SOURCE) → raw_claims (DATASET, bronze)
        duck-creek-policy (DATA_SOURCE) → raw_policies (DATASET, bronze)
        iso-claimsearch (DATA_SOURCE) → raw_fraud_checks (DATASET, bronze)

        raw_claims → enriched_claims (DATASET, silver)
        raw_policies → clean_policies (DATASET, silver)
        raw_fraud_checks → fraud_scores (DATASET, silver)

        clean_policies → claims_with_risk (DATASET, gold)
        enriched_claims → claims_with_risk (DATASET, gold)
        fraud_scores → claims_with_risk (DATASET, gold)

        claims_with_risk → adjuster_dashboard (SERVING_ENDPOINT)
        claims_with_risk → management_dashboard (SERVING_ENDPOINT)
        claims_with_risk → siu_dashboard (SERVING_ENDPOINT)
    """
    tracker = LineageTracker()

    # --- Data Sources ---
    tracker.add_node(
        LineageNode(
            id="guidewire-claims",
            name="guidewire-claims",
            node_type=LineageNodeType.DATA_SOURCE,
            metadata={"system": "Guidewire", "type": "PostgreSQL"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="duck-creek-policy",
            name="duck-creek-policy",
            node_type=LineageNodeType.DATA_SOURCE,
            metadata={"system": "Duck Creek", "type": "SQL Server"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="iso-claimsearch",
            name="iso-claimsearch",
            node_type=LineageNodeType.DATA_SOURCE,
            metadata={"system": "ISO", "type": "REST API"},
        )
    )

    # --- Bronze Layer (raw datasets) ---
    tracker.add_node(
        LineageNode(
            id="raw-claims",
            name="raw_claims",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "bronze"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="raw-policies",
            name="raw_policies",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "bronze"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="raw-fraud-checks",
            name="raw_fraud_checks",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "bronze"},
        )
    )

    # --- Silver Layer (cleaned/enriched) ---
    tracker.add_node(
        LineageNode(
            id="enriched-claims",
            name="enriched_claims",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "silver"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="clean-policies",
            name="clean_policies",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "silver"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="fraud-scores",
            name="fraud_scores",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "silver"},
        )
    )

    # --- Gold Layer ---
    tracker.add_node(
        LineageNode(
            id="claims-with-risk",
            name="claims_with_risk",
            node_type=LineageNodeType.DATASET,
            metadata={"layer": "gold"},
        )
    )

    # --- Serving Endpoints ---
    tracker.add_node(
        LineageNode(
            id="adjuster-dashboard",
            name="adjuster_dashboard",
            node_type=LineageNodeType.SERVING_ENDPOINT,
            metadata={"url": "/dashboards/adjuster"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="management-dashboard",
            name="management_dashboard",
            node_type=LineageNodeType.SERVING_ENDPOINT,
            metadata={"url": "/dashboards/management"},
        )
    )
    tracker.add_node(
        LineageNode(
            id="siu-dashboard",
            name="siu_dashboard",
            node_type=LineageNodeType.SERVING_ENDPOINT,
            metadata={"url": "/dashboards/siu"},
        )
    )

    # --- Edges: Sources → Bronze ---
    tracker.add_edge(
        LineageEdge(
            source_node_id="guidewire-claims",
            target_node_id="raw-claims",
            edge_type=LineageEdgeType.PRODUCES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="duck-creek-policy",
            target_node_id="raw-policies",
            edge_type=LineageEdgeType.PRODUCES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="iso-claimsearch",
            target_node_id="raw-fraud-checks",
            edge_type=LineageEdgeType.PRODUCES,
        )
    )

    # --- Edges: Bronze → Silver ---
    tracker.add_edge(
        LineageEdge(
            source_node_id="raw-policies",
            target_node_id="clean-policies",
            edge_type=LineageEdgeType.DERIVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="raw-claims",
            target_node_id="enriched-claims",
            edge_type=LineageEdgeType.DERIVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="raw-fraud-checks",
            target_node_id="fraud-scores",
            edge_type=LineageEdgeType.DERIVES,
        )
    )

    # --- Edges: Silver → Gold ---
    tracker.add_edge(
        LineageEdge(
            source_node_id="clean-policies",
            target_node_id="claims-with-risk",
            edge_type=LineageEdgeType.DERIVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="enriched-claims",
            target_node_id="claims-with-risk",
            edge_type=LineageEdgeType.DERIVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="fraud-scores",
            target_node_id="claims-with-risk",
            edge_type=LineageEdgeType.DERIVES,
        )
    )

    # --- Edges: Gold → Serving ---
    tracker.add_edge(
        LineageEdge(
            source_node_id="claims-with-risk",
            target_node_id="adjuster-dashboard",
            edge_type=LineageEdgeType.SERVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="claims-with-risk",
            target_node_id="management-dashboard",
            edge_type=LineageEdgeType.SERVES,
        )
    )
    tracker.add_edge(
        LineageEdge(
            source_node_id="claims-with-risk",
            target_node_id="siu-dashboard",
            edge_type=LineageEdgeType.SERVES,
        )
    )

    return tracker
