#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex.db._sqlite3._SQLite3Mixins._BlobMixin.save_blob/load_blob.

Motivated by real-world validation on NeuroVista: 2.56M pickle cache files
were consolidated into a single SQLite blob store via
`scitex.db.SQLite3.save_blob(table, data, key)` at ~1,870 records/sec with
zero API-level errors.

These tests cover the observed contract:
- round-trip save/load for common Python types (dict, list, str, int, ndarray)
- compress_by_default behavior and 1 KB threshold
- INSERT OR REPLACE semantics (re-running is safe, values overwrite)
- context-manager lifecycle (enter/exit, idempotent re-open)
- metadata storage
- KeyError on missing key
- load_blob without key returns dict of all rows
"""

from __future__ import annotations

import pickle
import sqlite3 as _sqlite3

import numpy as np
import pytest

from scitex.db import SQLite3


# ----------------------------------------------------------------------------
# Round-trip fundamentals
# ----------------------------------------------------------------------------


def test_save_blob_dict_roundtrip(tmp_path):
    """save_blob / load_blob should round-trip a plain dict intact."""
    db_path = tmp_path / "blob_dict.db"
    payload = {"a": 1, "b": [1, 2, 3], "c": "hello"}

    with SQLite3(str(db_path)) as db:
        db.save_blob("t", payload, key="k1")

    with SQLite3(str(db_path)) as db:
        loaded = db.load_blob("t", key="k1")

    assert loaded == payload


def test_save_blob_list_roundtrip(tmp_path):
    db_path = tmp_path / "blob_list.db"
    payload = [1, 2.5, "x", None, True]

    with SQLite3(str(db_path)) as db:
        db.save_blob("t", payload, key="k1")
        loaded = db.load_blob("t", key="k1")

    assert loaded == payload


def test_save_blob_string_roundtrip(tmp_path):
    db_path = tmp_path / "blob_str.db"
    with SQLite3(str(db_path)) as db:
        db.save_blob("t", "hello world", key="k1")
        assert db.load_blob("t", key="k1") == "hello world"


def test_save_blob_int_roundtrip(tmp_path):
    db_path = tmp_path / "blob_int.db"
    with SQLite3(str(db_path)) as db:
        db.save_blob("t", 42, key="k1")
        assert db.load_blob("t", key="k1") == 42


# ----------------------------------------------------------------------------
# Numpy array handling (special-cased via data_type "ndarray:<dtype>:<shape>")
# ----------------------------------------------------------------------------


def test_save_blob_ndarray_dtype_shape_preserved(tmp_path):
    db_path = tmp_path / "blob_nd.db"
    arr = np.arange(12, dtype=np.float64).reshape(3, 4)

    with SQLite3(str(db_path)) as db:
        db.save_blob("t", arr, key="arr1")
        loaded = db.load_blob("t", key="arr1")

    assert isinstance(loaded, np.ndarray)
    assert loaded.dtype == arr.dtype
    assert loaded.shape == arr.shape
    np.testing.assert_array_equal(loaded, arr)


def test_save_blob_ndarray_various_dtypes(tmp_path):
    db_path = tmp_path / "blob_dtypes.db"
    cases = {
        "f32": np.arange(6, dtype=np.float32).reshape(2, 3),
        "i64": np.array([1, 2, 3], dtype=np.int64),
        "u8": np.zeros((4,), dtype=np.uint8),
        "bool_": np.array([True, False, True]),
    }
    with SQLite3(str(db_path)) as db:
        for k, v in cases.items():
            db.save_blob("t", v, key=k)
        for k, v in cases.items():
            out = db.load_blob("t", key=k)
            assert out.dtype == v.dtype
            np.testing.assert_array_equal(out, v)


# ----------------------------------------------------------------------------
# Real-world shape: the GMM cache dict used by the NeuroVista pipeline
# ----------------------------------------------------------------------------


def test_save_blob_gmm_cache_shape(tmp_path):
    """Mirror of the actual scitex.db use case from NeuroVista GMM ingest."""
    db_path = tmp_path / "gmm_cache.db"
    payload = {
        "means": np.array([0.1, 0.9], dtype=np.float64),
        "sigmas": np.array([0.05, 0.05], dtype=np.float64),
        "weights": np.array([0.7, 0.3], dtype=np.float64),
        "ashmans_d": 0.8473006672540366,
        "weight_ratio": 3.363115657538119,
        "bhattacharyya_coeff": 0.6387041636281181,
        "bimodality_coeff": 0.1479683821112239,
    }
    content_hash = "0000015cbd494f1ec22e8e465cb42544"

    with SQLite3(str(db_path), compress_by_default=True) as db:
        db.save_blob("gmm_cache", payload, key=content_hash)
        loaded = db.load_blob("gmm_cache", key=content_hash)

    for k, v in payload.items():
        if isinstance(v, np.ndarray):
            np.testing.assert_array_equal(loaded[k], v)
        else:
            assert loaded[k] == v


# ----------------------------------------------------------------------------
# Compression semantics
# ----------------------------------------------------------------------------


def test_compression_threshold_small_payload_not_compressed(tmp_path):
    """Payloads <= 1 KB are stored uncompressed even with compress=True."""
    db_path = tmp_path / "small.db"
    small = {"x": 1}  # pickle bytes << 1 KB

    with SQLite3(str(db_path), compress_by_default=True) as db:
        db.save_blob("t", small, key="k1")
        row = db.execute(
            "SELECT compressed FROM t WHERE key = ?", ("k1",)
        ).fetchone()

    assert row[0] == 0, "expected compressed=0 for small payload"


def test_compression_large_payload_is_compressed(tmp_path):
    """Payloads > 1 KB get zlib-compressed when compress_by_default is True."""
    db_path = tmp_path / "large.db"
    large_arr = np.arange(2000, dtype=np.float64)  # ~16 KB

    with SQLite3(str(db_path), compress_by_default=True) as db:
        db.save_blob("t", large_arr, key="k1")
        row = db.execute(
            "SELECT compressed FROM t WHERE key = ?", ("k1",)
        ).fetchone()

    assert row[0] == 1, "expected compressed=1 for large payload"


def test_compression_default_off(tmp_path):
    """Without compress_by_default=True, large payloads are NOT compressed."""
    db_path = tmp_path / "nocompr.db"
    large_arr = np.arange(2000, dtype=np.float64)

    with SQLite3(str(db_path)) as db:
        db.save_blob("t", large_arr, key="k1")
        row = db.execute(
            "SELECT compressed FROM t WHERE key = ?", ("k1",)
        ).fetchone()

    assert row[0] == 0


def test_compression_explicit_override(tmp_path):
    """Explicit compress=True on a per-call basis overrides db default off."""
    db_path = tmp_path / "override.db"
    large_arr = np.arange(2000, dtype=np.float64)

    with SQLite3(str(db_path)) as db:  # default off
        db.save_blob("t", large_arr, key="explicit_on", compress=True)
        db.save_blob("t", large_arr, key="explicit_off", compress=False)
        rows = dict(
            db.execute(
                "SELECT key, compressed FROM t WHERE key IN ('explicit_on','explicit_off')"
            ).fetchall()
        )

    assert rows["explicit_on"] == 1
    assert rows["explicit_off"] == 0


def test_compression_roundtrip_matches_original(tmp_path):
    """Compressed blobs must decompress back to the exact original value."""
    db_path = tmp_path / "cr.db"
    arr = np.random.default_rng(42).standard_normal(2000)

    with SQLite3(str(db_path), compress_by_default=True) as db:
        db.save_blob("t", arr, key="k")
        loaded = db.load_blob("t", key="k")

    np.testing.assert_array_equal(loaded, arr)


# ----------------------------------------------------------------------------
# INSERT OR REPLACE semantics — re-running is idempotent
# ----------------------------------------------------------------------------


def test_save_blob_insert_or_replace_overwrites_not_appends(tmp_path):
    db_path = tmp_path / "replace.db"
    with SQLite3(str(db_path)) as db:
        db.save_blob("t", {"v": 1}, key="k")
        db.save_blob("t", {"v": 2}, key="k")  # same key
        count = db.execute("SELECT COUNT(*) FROM t WHERE key = ?", ("k",)).fetchone()[0]
        loaded = db.load_blob("t", key="k")

    assert count == 1
    assert loaded == {"v": 2}


def test_save_blob_resume_safe(tmp_path):
    """Simulate a retried ingest: re-saving all entries is a no-op semantically."""
    db_path = tmp_path / "resume.db"
    items = [("a", {"x": 1}), ("b", {"x": 2}), ("c", {"x": 3})]

    with SQLite3(str(db_path)) as db:
        for k, v in items:
            db.save_blob("t", v, key=k)
        # Re-run
        for k, v in items:
            db.save_blob("t", v, key=k)
        total = db.execute("SELECT COUNT(*) FROM t").fetchone()[0]

    assert total == len(items)


# ----------------------------------------------------------------------------
# load_blob semantics
# ----------------------------------------------------------------------------


def test_load_blob_key_not_found_raises(tmp_path):
    db_path = tmp_path / "missing.db"
    with SQLite3(str(db_path)) as db:
        db.save_blob("t", {"v": 1}, key="present")
        with pytest.raises(KeyError):
            db.load_blob("t", key="absent")


def test_load_blob_without_key_returns_all(tmp_path):
    db_path = tmp_path / "all.db"
    payload = {"a": {"v": 1}, "b": {"v": 2}, "c": {"v": 3}}

    with SQLite3(str(db_path)) as db:
        for k, v in payload.items():
            db.save_blob("t", v, key=k)
        loaded = db.load_blob("t")  # no key → all rows

    assert isinstance(loaded, dict)
    assert set(loaded.keys()) == set(payload.keys())
    for k in payload:
        assert loaded[k] == payload[k]


# ----------------------------------------------------------------------------
# Schema + metadata
# ----------------------------------------------------------------------------


def test_save_blob_auto_creates_schema(tmp_path):
    """Calling save_blob on a nonexistent table must auto-create it."""
    db_path = tmp_path / "schema.db"
    with SQLite3(str(db_path)) as db:
        db.save_blob("fresh_table", {"x": 1}, key="k")
        cols = [
            row[1]
            for row in db.execute("PRAGMA table_info(fresh_table)").fetchall()
        ]

    expected = {
        "key",
        "timestamp",
        "pid",
        "hostname",
        "data",
        "compressed",
        "data_type",
        "metadata",
    }
    assert expected.issubset(set(cols))


def test_save_blob_records_metadata(tmp_path):
    import json

    db_path = tmp_path / "meta.db"
    meta = {"source": "unit_test", "run": 7}
    with SQLite3(str(db_path)) as db:
        db.save_blob("t", {"v": 1}, key="k", metadata=meta)
        row = db.execute("SELECT metadata FROM t WHERE key = ?", ("k",)).fetchone()

    assert row[0] is not None
    stored = json.loads(row[0])
    assert stored["source"] == "unit_test"
    assert stored["run"] == 7


def test_save_blob_compression_metadata_has_sizes(tmp_path):
    import json

    db_path = tmp_path / "meta_sz.db"
    large_arr = np.arange(5000, dtype=np.float64)

    with SQLite3(str(db_path), compress_by_default=True) as db:
        db.save_blob("t", large_arr, key="k")
        row = db.execute("SELECT metadata FROM t WHERE key = ?", ("k",)).fetchone()

    stored = json.loads(row[0])
    assert "original_size" in stored
    assert "compressed_size" in stored
    assert stored["compressed_size"] <= stored["original_size"]


# ----------------------------------------------------------------------------
# Context manager
# ----------------------------------------------------------------------------


def test_context_manager_persists_across_reopen(tmp_path):
    """Data written in one `with` block survives a new open on the same path."""
    db_path = tmp_path / "persist.db"

    with SQLite3(str(db_path)) as db:
        db.save_blob("t", {"v": 1}, key="k1")

    # new connection, same path
    with SQLite3(str(db_path)) as db2:
        loaded = db2.load_blob("t", key="k1")

    assert loaded == {"v": 1}


# ----------------------------------------------------------------------------
# Bulk-ingest smoke test (scaled-down mirror of the NeuroVista use case)
# ----------------------------------------------------------------------------


def test_bulk_ingest_smoke(tmp_path):
    """1000 records should ingest and read back cleanly."""
    db_path = tmp_path / "bulk.db"
    n = 1000

    with SQLite3(str(db_path), compress_by_default=True) as db:
        for i in range(n):
            payload = {"i": i, "v": float(i) * 0.5}
            db.save_blob("t", payload, key=f"k{i:04d}")

    with SQLite3(str(db_path)) as db:
        count = db.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        assert count == n
        # spot-check three keys
        for i in (0, 500, 999):
            loaded = db.load_blob("t", key=f"k{i:04d}")
            assert loaded == {"i": i, "v": float(i) * 0.5}


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
