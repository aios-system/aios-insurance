"""Tests for insurance data lineage graph.

Validates the data flow from source systems through transform layers
to serving endpoints — critical for regulatory audit compliance.
"""

from __future__ import annotations

from aios.data_platform.lineage.models import LineageNodeType

from insurance.lineage.graph import build_insurance_lineage

# ---------------------------------------------------------------------------
# Graph Structure
# ---------------------------------------------------------------------------


class TestLineageGraph:
    def test_has_three_data_sources(self):
        tracker = build_insurance_lineage()
        sources = [n for n in tracker._nodes.values() if n.node_type == LineageNodeType.DATA_SOURCE]
        assert len(sources) == 3
        names = {n.name for n in sources}
        assert "guidewire-claims" in names
        assert "duck-creek-policy" in names
        assert "iso-claimsearch" in names

    def test_has_three_serving_endpoints(self):
        tracker = build_insurance_lineage()
        endpoints = [
            n for n in tracker._nodes.values() if n.node_type == LineageNodeType.SERVING_ENDPOINT
        ]
        assert len(endpoints) == 3
        names = {n.name for n in endpoints}
        assert "adjuster_dashboard" in names
        assert "management_dashboard" in names
        assert "siu_dashboard" in names

    def test_total_node_count(self):
        """3 sources + 3 bronze + 3 silver + 1 gold + 3 serving = 13."""
        tracker = build_insurance_lineage()
        assert len(tracker._nodes) == 13

    def test_total_edge_count(self):
        """3 source→bronze + 3 bronze→silver + 3 silver→gold + 3 gold→serving = 12."""
        tracker = build_insurance_lineage()
        assert len(tracker._edges) == 12

    def test_guidewire_produces_raw_claims(self):
        tracker = build_insurance_lineage()
        graph = tracker.get_descendants("guidewire-claims", max_depth=1)
        node_ids = {n.id for n in graph.nodes}
        assert "raw-claims" in node_ids

    def test_can_trace_adjuster_dashboard_to_sources(self):
        """Trace adjuster dashboard back to guidewire and iso sources."""
        tracker = build_insurance_lineage()
        graph = tracker.get_ancestors("adjuster-dashboard")
        ancestor_ids = {n.id for n in graph.nodes}
        assert "guidewire-claims" in ancestor_ids
        assert "iso-claimsearch" in ancestor_ids

    def test_can_trace_siu_dashboard_to_fraud_data(self):
        """SIU dashboard should trace back through fraud scores to iso-claimsearch."""
        tracker = build_insurance_lineage()
        graph = tracker.get_ancestors("siu-dashboard")
        ancestor_ids = {n.id for n in graph.nodes}
        assert "iso-claimsearch" in ancestor_ids
        assert "fraud-scores" in ancestor_ids

    def test_get_roots_returns_sources(self):
        """Root nodes (no parents) should be the 3 data sources."""
        tracker = build_insurance_lineage()
        roots = tracker.get_roots()
        assert len(roots) == 3
        root_ids = {r.id for r in roots}
        assert "guidewire-claims" in root_ids
        assert "duck-creek-policy" in root_ids
        assert "iso-claimsearch" in root_ids

    def test_get_leaves_returns_endpoints(self):
        """Leaf nodes (no children) should be the 3 serving endpoints."""
        tracker = build_insurance_lineage()
        leaves = tracker.get_leaves()
        assert len(leaves) == 3
        leaf_ids = {leaf.id for leaf in leaves}
        assert "adjuster-dashboard" in leaf_ids
        assert "management-dashboard" in leaf_ids
        assert "siu-dashboard" in leaf_ids
