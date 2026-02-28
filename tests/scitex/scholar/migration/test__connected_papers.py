#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: tests/scitex/scholar/migration/test__connected_papers.py
# ----------------------------------------

"""
Tests for scitex.scholar.migration._connected_papers.

Covers:
- from_connected_papers:
    - missing connectedpapers package (ImportError)
    - invalid output_format argument
    - dry_run mode (no CitationGraph/Papers objects created)
    - successful import as citation_graph
    - successful import as papers
    - empty graph (no nodes) edge case
    - exception inside try block propagates as {success: False}

- to_connected_papers:
    - successful export writes bibtex and json files
    - export with empty node list produces empty bibtex
    - exception is caught and returned as {success: False, error}

Mock strategy
-------------
- `connectedpapers` module: patched via sys.modules so the lazy `import
  connectedpapers` inside the function body sees the mock.
- `scitex.scholar.migration._s2_resolver.bulk_resolve_dois`
- `scitex.scholar.migration._s2_resolver.bulk_resolve_metadata`
- `scitex.scholar.to_bibtex` imported inside to_connected_papers
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from scitex.scholar.migration._connected_papers import (
    from_connected_papers,
    to_connected_papers,
)

# ---------------------------------------------------------------------------
# Patch targets
# ---------------------------------------------------------------------------

_BULK_RESOLVE_DOIS = "scitex.scholar.migration._s2_resolver.bulk_resolve_dois"
_BULK_RESOLVE_METADATA = "scitex.scholar.migration._s2_resolver.bulk_resolve_metadata"
_TO_BIBTEX = "scitex.scholar.to_bibtex"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cp_module(nodes=None, edges=None):
    """Build a minimal fake `connectedpapers` module.

    Returns (module, client_class_mock).
    The client returned by Client() has a `get_graph_sync()` method that
    returns a response object whose `.graph.nodes` and `.graph.edges` are
    set to the supplied dicts.
    """
    if nodes is None:
        nodes = {"s2id1": MagicMock(title="Paper One")}
    if edges is None:
        edges = {}

    cp_graph = MagicMock()
    cp_graph.nodes = nodes
    cp_graph.edges = edges

    graph_response = MagicMock()
    graph_response.graph = cp_graph

    client_instance = MagicMock()
    client_instance.get_graph_sync.return_value = graph_response

    client_class = MagicMock(return_value=client_instance)

    cp_module = ModuleType("connectedpapers")
    cp_module.Client = client_class

    return cp_module, client_class


def _default_doi_map(nodes):
    """Produce a simple doi_map where every node gets a DOI."""
    return {s2_id: f"10.1/{s2_id}" for s2_id in nodes}


def _default_metadata_map(nodes):
    """Produce a simple metadata_map for every node."""
    return {
        s2_id: {
            "title": f"Title {s2_id}",
            "year": 2023,
            "authors": [{"name": "Author A"}],
            "venue": "Journal X",
            "citationCount": 5,
            "externalIds": {"DOI": f"10.1/{s2_id}"},
        }
        for s2_id in nodes
    }


# ---------------------------------------------------------------------------
# from_connected_papers — missing package
# ---------------------------------------------------------------------------


class TestFromConnectedPapersMissingPackage:
    """When connectedpapers is not installed the function returns success=False."""

    def test_import_error_returns_failure(self):
        """ImportError on `import connectedpapers` must produce success=False
        with a helpful installation instruction in the error message."""
        # Remove connectedpapers from sys.modules so the lazy import fails.
        sys.modules.pop("connectedpapers", None)

        with patch.dict(sys.modules, {"connectedpapers": None}):
            result = from_connected_papers("someid")

        assert result["success"] is False
        assert "connectedpapers" in result["error"].lower()
        assert "pip install" in result["error"]


# ---------------------------------------------------------------------------
# from_connected_papers — invalid output_format
# ---------------------------------------------------------------------------


class TestFromConnectedPapersInvalidOutputFormat:
    """An unrecognised output_format returns success=False immediately."""

    def test_invalid_format_returns_failure(self):
        """output_format='bibtex' is not a valid choice and must be rejected."""
        cp_module, _ = _make_cp_module()

        with patch.dict(sys.modules, {"connectedpapers": cp_module}):
            result = from_connected_papers("someid", output_format="bibtex")

        assert result["success"] is False
        assert "output_format" in result["error"]

    def test_empty_format_string_returns_failure(self):
        """An empty string for output_format must also be rejected."""
        cp_module, _ = _make_cp_module()

        with patch.dict(sys.modules, {"connectedpapers": cp_module}):
            result = from_connected_papers("someid", output_format="")

        assert result["success"] is False

    def test_valid_formats_are_accepted(self):
        """Both 'citation_graph' and 'papers' pass format validation."""
        nodes = {"s2id1": MagicMock(title="P")}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)

        for fmt in ("citation_graph", "papers"):
            with (
                patch.dict(sys.modules, {"connectedpapers": cp_module}),
                patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
                patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
                patch(
                    "scitex.scholar.migration._connected_papers._build_citation_graph",
                    return_value=MagicMock(),
                ),
                patch(
                    "scitex.scholar.migration._connected_papers._build_papers",
                    return_value=MagicMock(),
                ),
            ):
                result = from_connected_papers("s2id1", output_format=fmt)
            assert result["success"] is True, f"format={fmt!r} unexpectedly failed"


# ---------------------------------------------------------------------------
# from_connected_papers — dry_run
# ---------------------------------------------------------------------------


class TestFromConnectedPapersDryRun:
    """dry_run=True returns stats without building CitationGraph or Papers."""

    def test_dry_run_returns_stats_only(self):
        """dry_run must return success=True, stats dict, and dry_run=True,
        without any 'graph' or 'papers' key."""
        nodes = {"s2a": MagicMock(), "s2b": MagicMock()}
        doi_map = _default_doi_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes, edges={"e1": MagicMock()})

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
        ):
            result = from_connected_papers("s2a", dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert "stats" in result
        assert result["stats"]["node_count"] == 2
        assert result["stats"]["edge_count"] == 1
        assert "graph" not in result
        assert "papers" not in result

    def test_dry_run_does_not_call_bulk_resolve_metadata(self):
        """dry_run must not call bulk_resolve_metadata (expensive operation)."""
        nodes = {"s2a": MagicMock()}
        doi_map = _default_doi_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA) as mock_meta,
        ):
            from_connected_papers("s2a", dry_run=True)

        mock_meta.assert_not_called()

    def test_dry_run_resolved_count_in_stats(self):
        """stats['resolved_dois'] reflects how many nodes had DOIs resolved."""
        nodes = {"id1": MagicMock(), "id2": MagicMock(), "id3": MagicMock()}
        # Only two of the three have DOIs
        doi_map = {"id1": "10.1/a", "id2": None, "id3": "10.3/c"}
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
        ):
            result = from_connected_papers("id1", dry_run=True)

        assert result["stats"]["resolved_dois"] == 2
        assert result["stats"]["unresolved_count"] == 1


# ---------------------------------------------------------------------------
# from_connected_papers — empty graph
# ---------------------------------------------------------------------------


class TestFromConnectedPapersEmptyGraph:
    """A CP graph with no nodes returns success=True with a warning."""

    def test_empty_nodes_returns_success_with_warning(self):
        """When the graph has no nodes the function still succeeds but includes
        a warning message and zero stats."""
        cp_module, _ = _make_cp_module(nodes={}, edges={})

        with patch.dict(sys.modules, {"connectedpapers": cp_module}):
            result = from_connected_papers("seed_id")

        assert result["success"] is True
        assert result["stats"]["node_count"] == 0
        assert result["stats"]["resolved_dois"] == 0
        assert len(result["warnings"]) > 0


# ---------------------------------------------------------------------------
# from_connected_papers — successful citation_graph import
# ---------------------------------------------------------------------------


class TestFromConnectedPapersCitationGraph:
    """Successful import as citation_graph format."""

    def test_returns_success_with_graph_key(self):
        """Result must contain 'success': True and a 'graph' key."""
        nodes = {"s2id1": MagicMock(title="Paper One")}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)
        fake_graph = MagicMock()

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_citation_graph",
                return_value=fake_graph,
            ),
        ):
            result = from_connected_papers("s2id1", output_format="citation_graph")

        assert result["success"] is True
        assert result["dry_run"] is False
        assert result["graph"] is fake_graph
        assert "papers" not in result

    def test_stats_reflect_graph_structure(self):
        """stats.node_count and stats.edge_count match the graph data."""
        nodes = {"a": MagicMock(), "b": MagicMock()}
        edges = {"e1": MagicMock(), "e2": MagicMock(), "e3": MagicMock()}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes, edges=edges)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_citation_graph",
                return_value=MagicMock(),
            ),
        ):
            result = from_connected_papers("a", output_format="citation_graph")

        assert result["stats"]["node_count"] == 2
        assert result["stats"]["edge_count"] == 3

    def test_unresolved_ids_produce_warning(self):
        """When some IDs cannot be resolved to DOIs a warning is appended."""
        nodes = {"id1": MagicMock(), "id2": MagicMock()}
        # id2 has no DOI
        doi_map = {"id1": "10.1/a", "id2": None}
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_citation_graph",
                return_value=MagicMock(),
            ),
        ):
            result = from_connected_papers("id1", output_format="citation_graph")

        assert any("could not be resolved" in w for w in result["warnings"])

    def test_bulk_resolve_dois_called_with_all_node_ids(self):
        """bulk_resolve_dois must receive the full list of node S2 IDs."""
        nodes = {"n1": MagicMock(), "n2": MagicMock(), "n3": MagicMock()}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map) as mock_dois,
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_citation_graph",
                return_value=MagicMock(),
            ),
        ):
            from_connected_papers("n1", output_format="citation_graph")

        called_ids = set(mock_dois.call_args[0][0])
        assert called_ids == set(nodes.keys())

    def test_cp_api_key_forwarded_to_client(self):
        """cp_api_key must be forwarded when constructing the CP Client."""
        nodes = {"x": MagicMock()}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, client_class = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_citation_graph",
                return_value=MagicMock(),
            ),
        ):
            from_connected_papers("x", cp_api_key="cp-secret")

        client_class.assert_called_once_with(api_key="cp-secret")


# ---------------------------------------------------------------------------
# from_connected_papers — successful papers import
# ---------------------------------------------------------------------------


class TestFromConnectedPapersPapersFormat:
    """Successful import as papers format."""

    def test_returns_success_with_papers_key(self):
        """Result must contain 'success': True and a 'papers' key."""
        nodes = {"s2id1": MagicMock(title="Paper One")}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)
        fake_papers = MagicMock()

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_papers",
                return_value=fake_papers,
            ),
        ):
            result = from_connected_papers("s2id1", output_format="papers")

        assert result["success"] is True
        assert result["papers"] is fake_papers
        assert "graph" not in result

    def test_build_papers_called_with_correct_maps(self):
        """_build_papers must receive doi_map and metadata_map as positional
        args."""
        nodes = {"s2id1": MagicMock()}
        doi_map = _default_doi_map(nodes)
        meta_map = _default_metadata_map(nodes)
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, return_value=doi_map),
            patch(_BULK_RESOLVE_METADATA, return_value=meta_map),
            patch(
                "scitex.scholar.migration._connected_papers._build_papers",
                return_value=MagicMock(),
            ) as mock_build,
        ):
            from_connected_papers("s2id1", output_format="papers")

        call_args = mock_build.call_args[0]
        assert call_args[0] is doi_map
        assert call_args[1] is meta_map


# ---------------------------------------------------------------------------
# from_connected_papers — exception handling
# ---------------------------------------------------------------------------


class TestFromConnectedPapersExceptions:
    """Unexpected exceptions are caught and returned as failure dicts."""

    def test_exception_in_client_call_returns_failure(self):
        """If get_graph_sync raises, success must be False."""
        cp_module = ModuleType("connectedpapers")
        client_instance = MagicMock()
        client_instance.get_graph_sync.side_effect = RuntimeError("network error")
        cp_module.Client = MagicMock(return_value=client_instance)

        with patch.dict(sys.modules, {"connectedpapers": cp_module}):
            result = from_connected_papers("some_id")

        assert result["success"] is False
        assert "network error" in result["error"]

    def test_exception_in_bulk_resolve_returns_failure(self):
        """If bulk_resolve_dois raises, success must be False."""
        nodes = {"id1": MagicMock()}
        cp_module, _ = _make_cp_module(nodes=nodes)

        with (
            patch.dict(sys.modules, {"connectedpapers": cp_module}),
            patch(_BULK_RESOLVE_DOIS, side_effect=ValueError("resolver error")),
        ):
            result = from_connected_papers("id1")

        assert result["success"] is False
        assert "resolver error" in result["error"]


# ---------------------------------------------------------------------------
# to_connected_papers
# ---------------------------------------------------------------------------


class TestToConnectedPapersSuccessful:
    """to_connected_papers writes bibtex and json output files."""

    def _make_graph_mock(self, nodes):
        """Build a fake CitationGraph with the given node mock list."""
        graph = MagicMock()
        graph.nodes = nodes
        graph.to_dict.return_value = {"seed": "doi1", "nodes": [], "edges": []}
        return graph

    def _make_node_mock(
        self, doi=None, title="T", year=2023, authors=None, journal="J"
    ):
        node = MagicMock()
        node.doi = doi
        node.title = title
        node.year = year
        node.authors = authors or ["Author A"]
        node.journal = journal
        return node

    def test_successful_export_returns_success_true(self, tmp_path):
        """A valid CitationGraph is exported successfully."""
        node = self._make_node_mock(doi="10.1/a")
        graph = self._make_graph_mock([node])
        fake_bib = "@article{key, title={T}}"

        with patch(_TO_BIBTEX, return_value=fake_bib):
            result = to_connected_papers(graph, output=str(tmp_path))

        assert result["success"] is True

    def test_bibtex_file_is_created(self, tmp_path):
        """The bibtex output file must be written to the output directory."""
        node = self._make_node_mock(doi="10.1/a")
        graph = self._make_graph_mock([node])

        with patch(_TO_BIBTEX, return_value="@article{k,title={T}}"):
            result = to_connected_papers(graph, output=str(tmp_path))

        bibtex_path = Path(result["bibtex_path"])
        assert bibtex_path.exists()
        assert bibtex_path.suffix == ".bib"

    def test_json_file_is_created(self, tmp_path):
        """The json output file must be written to the output directory."""
        node = self._make_node_mock(doi="10.1/a")
        graph = self._make_graph_mock([node])

        with patch(_TO_BIBTEX, return_value="@article{k,title={T}}"):
            result = to_connected_papers(graph, output=str(tmp_path))

        json_path = Path(result["json_path"])
        assert json_path.exists()
        assert json_path.suffix == ".json"

    def test_paper_count_matches_node_count(self, tmp_path):
        """paper_count in the result equals the number of nodes in the graph."""
        nodes = [
            self._make_node_mock(doi="10.1/a"),
            self._make_node_mock(doi="10.2/b"),
            self._make_node_mock(doi="10.3/c"),
        ]
        graph = self._make_graph_mock(nodes)

        with patch(_TO_BIBTEX, return_value="@article{k,title={T}}"):
            result = to_connected_papers(graph, output=str(tmp_path))

        assert result["paper_count"] == 3

    def test_bibtex_entries_count_only_nodes_with_doi(self, tmp_path):
        """bibtex_entries counts only nodes that have a DOI."""
        nodes = [
            self._make_node_mock(doi="10.1/a"),
            self._make_node_mock(doi=None),  # no DOI — must be skipped
            self._make_node_mock(doi="10.3/c"),
        ]
        graph = self._make_graph_mock(nodes)

        with patch(_TO_BIBTEX, return_value="@article{k,title={T}}"):
            result = to_connected_papers(graph, output=str(tmp_path))

        assert result["bibtex_entries"] == 2

    def test_to_bibtex_called_for_each_doi_node(self, tmp_path):
        """to_bibtex is called once per node that has a non-None doi."""
        nodes = [
            self._make_node_mock(doi="10.1/a"),
            self._make_node_mock(doi=None),
            self._make_node_mock(doi="10.2/b"),
        ]
        graph = self._make_graph_mock(nodes)

        with patch(_TO_BIBTEX, return_value="@article{k,title={T}}") as mock_bib:
            to_connected_papers(graph, output=str(tmp_path))

        assert mock_bib.call_count == 2

    def test_output_defaults_to_cwd(self, monkeypatch, tmp_path):
        """When output=None the files are placed in the current directory."""
        monkeypatch.chdir(tmp_path)
        node = self._make_node_mock(doi="10.1/a")
        graph = self._make_graph_mock([node])

        with patch(_TO_BIBTEX, return_value="@article{k}"):
            result = to_connected_papers(graph)

        assert Path(result["bibtex_path"]).parent == tmp_path


class TestToConnectedPapersEmptyGraph:
    """to_connected_papers handles a graph with no nodes."""

    def test_empty_node_list_creates_empty_bib(self, tmp_path):
        """An empty graph produces an empty .bib file."""
        graph = MagicMock()
        graph.nodes = []
        graph.to_dict.return_value = {"seed": "", "nodes": [], "edges": []}

        with patch(_TO_BIBTEX, return_value="@article{k}") as mock_bib:
            result = to_connected_papers(graph, output=str(tmp_path))

        assert result["success"] is True
        assert result["bibtex_entries"] == 0
        mock_bib.assert_not_called()
        bib_content = Path(result["bibtex_path"]).read_text(encoding="utf-8")
        assert bib_content == ""


class TestToConnectedPapersExceptions:
    """Exceptions during export are captured as failure dicts."""

    def test_exception_returns_failure(self, tmp_path):
        """If graph.to_dict raises, success must be False."""
        graph = MagicMock()
        graph.nodes = []
        graph.to_dict.side_effect = RuntimeError("serialisation error")

        result = to_connected_papers(graph, output=str(tmp_path))

        assert result["success"] is False
        assert "serialisation error" in result["error"]


class TestToConnectedPapersIntegration:
    """Integration test: to_bibtex is NOT mocked — verifies real call works."""

    def _make_node(self, doi, title="Title", year=2023, authors=None, journal="J"):
        node = MagicMock()
        node.doi = doi
        node.title = title
        node.year = year
        node.authors = authors or ["Alice Smith"]
        node.journal = journal
        return node

    def test_real_to_bibtex_produces_valid_entry(self, tmp_path):
        """to_connected_papers builds a correct paper dict for to_bibtex."""
        node = self._make_node("10.1234/test", title="Test Paper", year=2024)
        graph = MagicMock()
        graph.nodes = [node]
        graph.to_dict.return_value = {"nodes": [], "edges": []}

        result = to_connected_papers(graph, output=str(tmp_path))

        assert result["success"] is True
        assert result["bibtex_entries"] == 1
        bib_content = Path(result["bibtex_path"]).read_text(encoding="utf-8")
        assert "@article{" in bib_content
        assert "10.1234/test" in bib_content


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
