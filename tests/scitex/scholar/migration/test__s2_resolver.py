#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: tests/scitex/scholar/migration/test__s2_resolver.py
# ----------------------------------------

"""
Tests for scitex.scholar.migration._s2_resolver.

Covers:
- bulk_resolve_dois: empty input, successful resolution, partial resolution (None
  results), chunking behavior when >500 IDs are supplied.
- bulk_resolve_metadata: empty input, successful resolution, custom fields.

The SemanticScholarEngine is imported lazily inside each function, so all mocks
target the full import path used at call time:
    scitex.scholar.metadata_engines.individual.SemanticScholarEngine.SemanticScholarEngine
"""

from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from scitex.scholar.migration._s2_resolver import (
    bulk_resolve_dois,
    bulk_resolve_metadata,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENGINE_PATH = (
    "scitex.scholar.metadata_engines.individual"
    ".SemanticScholarEngine.SemanticScholarEngine"
)


def _make_engine_mock(batch_results):
    """Return a mock SemanticScholarEngine class whose batch_resolve returns
    the given list."""
    engine_instance = MagicMock()
    engine_instance.batch_resolve.return_value = batch_results
    engine_class = MagicMock(return_value=engine_instance)
    return engine_class, engine_instance


# ---------------------------------------------------------------------------
# bulk_resolve_dois
# ---------------------------------------------------------------------------


class TestBulkResolveDoisEmptyInput:
    """bulk_resolve_dois returns an empty dict for empty inputs."""

    def test_empty_list_returns_empty_dict(self):
        """Passing an empty list must return {} without calling the engine."""
        result = bulk_resolve_dois([])
        assert result == {}

    def test_empty_list_with_api_key_returns_empty_dict(self):
        """api_key argument must not change behaviour for empty input."""
        result = bulk_resolve_dois([], api_key="some-key")
        assert result == {}


class TestBulkResolveDoisSuccessful:
    """bulk_resolve_dois maps all S2 IDs to their DOIs when the engine
    returns valid results."""

    def test_single_id_resolved(self):
        """A single S2 ID with a DOI in externalIds is resolved correctly."""
        s2_id = "abc123"
        engine_class, engine_instance = _make_engine_mock(
            [{"externalIds": {"DOI": "10.1234/test"}}]
        )

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois([s2_id])

        assert result == {s2_id: "10.1234/test"}
        engine_class.assert_called_once_with(api_key=None)
        engine_instance.batch_resolve.assert_called_once_with(
            [s2_id], fields="externalIds"
        )

    def test_multiple_ids_all_resolved(self):
        """Multiple IDs are all resolved and the mapping is order-preserving."""
        s2_ids = ["id1", "id2", "id3"]
        batch_results = [
            {"externalIds": {"DOI": "10.1/a"}},
            {"externalIds": {"DOI": "10.2/b"}},
            {"externalIds": {"DOI": "10.3/c"}},
        ]
        engine_class, _ = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        assert result == {"id1": "10.1/a", "id2": "10.2/b", "id3": "10.3/c"}

    def test_api_key_forwarded_to_engine(self):
        """The api_key argument is forwarded to SemanticScholarEngine()."""
        s2_id = "abc123"
        engine_class, _ = _make_engine_mock([{"externalIds": {"DOI": "10.1234/test"}}])

        with patch(_ENGINE_PATH, engine_class):
            bulk_resolve_dois([s2_id], api_key="my-key")

        engine_class.assert_called_once_with(api_key="my-key")

    def test_result_without_doi_key_maps_to_none(self):
        """A result whose externalIds dict lacks a 'DOI' key maps to None."""
        s2_id = "nodoiid"
        engine_class, _ = _make_engine_mock([{"externalIds": {"ArXiv": "2301.12345"}}])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois([s2_id])

        assert result == {s2_id: None}

    def test_empty_external_ids_dict_maps_to_none(self):
        """A result with an empty externalIds dict maps the S2 ID to None."""
        s2_id = "emptyids"
        engine_class, _ = _make_engine_mock([{"externalIds": {}}])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois([s2_id])

        assert result == {s2_id: None}

    def test_null_external_ids_maps_to_none(self):
        """A result where externalIds is None (or falsy) maps to None."""
        s2_id = "nullids"
        engine_class, _ = _make_engine_mock([{"externalIds": None}])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois([s2_id])

        assert result == {s2_id: None}


class TestBulkResolveDoisPartialResolution:
    """bulk_resolve_dois handles mixed None/dict results from batch_resolve."""

    def test_some_none_results(self):
        """IDs whose batch_resolve result is None map to None in the output."""
        s2_ids = ["resolved_id", "unresolved_id", "another_resolved"]
        batch_results = [
            {"externalIds": {"DOI": "10.1/resolved"}},
            None,
            {"externalIds": {"DOI": "10.3/other"}},
        ]
        engine_class, _ = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        assert result["resolved_id"] == "10.1/resolved"
        assert result["unresolved_id"] is None
        assert result["another_resolved"] == "10.3/other"

    def test_all_none_results(self):
        """When every result from batch_resolve is None, all values are None."""
        s2_ids = ["a", "b", "c"]
        engine_class, _ = _make_engine_mock([None, None, None])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        assert all(v is None for v in result.values())
        assert set(result.keys()) == set(s2_ids)

    def test_result_length_matches_input_length(self):
        """Output mapping has the same number of keys as the input list."""
        s2_ids = [f"id{i}" for i in range(10)]
        batch_results = [
            {"externalIds": {"DOI": f"10.{i}/x"}} if i % 2 == 0 else None
            for i in range(10)
        ]
        engine_class, _ = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        assert len(result) == 10


class TestBulkResolveDoisChunking:
    """bulk_resolve_dois must pass the full list to batch_resolve in one call.

    The chunking behaviour (if any) is the engine's responsibility.  Here we
    verify that batch_resolve is called exactly once with the full list,
    regardless of list size, so the resolver function itself does not split
    the input.
    """

    def test_large_input_calls_batch_resolve_once(self):
        """With >500 IDs the engine's batch_resolve is still called once,
        receiving the full list (resolver does not chunk internally)."""
        s2_ids = [f"id{i}" for i in range(501)]
        batch_results = [{"externalIds": {"DOI": f"10.{i}/x"}} for i in range(501)]
        engine_class, engine_instance = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        engine_instance.batch_resolve.assert_called_once()
        actual_ids_arg = engine_instance.batch_resolve.call_args[0][0]
        assert actual_ids_arg == s2_ids
        assert len(result) == 501


# ---------------------------------------------------------------------------
# bulk_resolve_metadata
# ---------------------------------------------------------------------------


class TestBulkResolveMetadataEmptyInput:
    """bulk_resolve_metadata returns an empty dict for empty inputs."""

    def test_empty_list_returns_empty_dict(self):
        """Passing an empty list must return {} without calling the engine."""
        result = bulk_resolve_metadata([])
        assert result == {}

    def test_empty_list_with_api_key_returns_empty_dict(self):
        """api_key and fields arguments must not change behaviour for empty
        input."""
        result = bulk_resolve_metadata([], api_key="key", fields="title")
        assert result == {}


class TestBulkResolveMetadataSuccessful:
    """bulk_resolve_metadata builds the mapping {s2_id: metadata_dict}."""

    def test_single_id_resolved(self):
        """A single S2 ID maps to its returned metadata dict."""
        s2_id = "paperId1"
        meta = {"title": "Test Paper", "year": 2023, "externalIds": {"DOI": "10.1/x"}}
        engine_class, engine_instance = _make_engine_mock([meta])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_metadata([s2_id])

        assert result == {s2_id: meta}
        engine_class.assert_called_once_with(api_key=None)
        engine_instance.batch_resolve.assert_called_once_with(
            [s2_id],
            fields="externalIds,title,year,authors,citationCount,venue",
        )

    def test_multiple_ids_returns_full_mapping(self):
        """Multiple IDs produce a mapping with one entry per ID."""
        s2_ids = ["id1", "id2"]
        metas = [
            {"title": "Paper A", "year": 2021},
            {"title": "Paper B", "year": 2022},
        ]
        engine_class, _ = _make_engine_mock(metas)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_metadata(s2_ids)

        assert result == {"id1": metas[0], "id2": metas[1]}

    def test_none_result_preserved_in_mapping(self):
        """If batch_resolve returns None for a paper, None is kept in the map."""
        s2_ids = ["found", "missing"]
        engine_class, _ = _make_engine_mock([{"title": "Found"}, None])

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_metadata(s2_ids)

        assert result["found"] == {"title": "Found"}
        assert result["missing"] is None

    def test_custom_fields_forwarded_to_batch_resolve(self):
        """A custom fields string is passed verbatim to batch_resolve."""
        s2_id = "someid"
        custom_fields = "title,year"
        engine_class, engine_instance = _make_engine_mock([{"title": "X"}])

        with patch(_ENGINE_PATH, engine_class):
            bulk_resolve_metadata([s2_id], fields=custom_fields)

        _, kwargs = engine_instance.batch_resolve.call_args
        # fields is positional in the current implementation
        positional = engine_instance.batch_resolve.call_args[0]
        assert custom_fields in positional or kwargs.get("fields") == custom_fields

    def test_api_key_forwarded_to_engine(self):
        """The api_key is forwarded to SemanticScholarEngine constructor."""
        engine_class, _ = _make_engine_mock([{"title": "T"}])

        with patch(_ENGINE_PATH, engine_class):
            bulk_resolve_metadata(["id1"], api_key="secret")

        engine_class.assert_called_once_with(api_key="secret")


class TestBulkResolveDoisTruncatedResults:
    """bulk_resolve_dois pads missing results when batch_resolve returns short."""

    def test_truncated_batch_pads_with_none(self):
        """If batch_resolve returns fewer items, missing ones become None."""
        s2_ids = ["id1", "id2", "id3"]
        # Only 1 result returned instead of 3
        batch_results = [{"externalIds": {"DOI": "10.1/a"}}]
        engine_class, _ = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_dois(s2_ids)

        assert len(result) == 3
        assert result["id1"] == "10.1/a"
        assert result["id2"] is None
        assert result["id3"] is None


class TestBulkResolveMetadataTruncatedResults:
    """bulk_resolve_metadata pads missing results when batch_resolve returns short."""

    def test_truncated_batch_pads_with_none(self):
        """If batch_resolve returns fewer items, missing ones become None."""
        s2_ids = ["id1", "id2"]
        batch_results = [{"title": "Paper 1"}]  # Only 1 result
        engine_class, _ = _make_engine_mock(batch_results)

        with patch(_ENGINE_PATH, engine_class):
            result = bulk_resolve_metadata(s2_ids)

        assert len(result) == 2
        assert result["id1"] == {"title": "Paper 1"}
        assert result["id2"] is None


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
