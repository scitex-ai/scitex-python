#!/usr/bin/env python3
"""Tests for migration_report dataclasses.

All tests here are pure unit tests — no Zotero database required.
They exercise MigratedItem, MigrationError, MigrationReport,
ExportPackage, SyncDiffItem, and SyncDiff.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# MigratedItem
# ---------------------------------------------------------------------------


def test_migrated_item_fields():
    from scitex.scholar.integration.zotero.migration_report import MigratedItem

    item = MigratedItem(
        zotero_key="ABCD1234",
        scholar_id="00000001",
        title="A Test Paper",
        doi="10.1000/xyz",
        pdf_migrated=True,
        status="imported",
    )
    assert item.zotero_key == "ABCD1234"
    assert item.scholar_id == "00000001"
    assert item.pdf_migrated is True
    assert item.status == "imported"
    assert item.error is None  # default


def test_migrated_item_error_field():
    from scitex.scholar.integration.zotero.migration_report import MigratedItem

    item = MigratedItem(
        zotero_key="ABCD1234",
        scholar_id=None,
        title="Broken Paper",
        doi=None,
        pdf_migrated=False,
        status="failed",
        error="Connection refused",
    )
    assert item.error == "Connection refused"
    assert item.status == "failed"


# ---------------------------------------------------------------------------
# MigrationError
# ---------------------------------------------------------------------------


def test_migration_error_fields():
    from scitex.scholar.integration.zotero.migration_report import MigrationError

    err = MigrationError(
        zotero_key="ZZZZZZZZ",
        title="Some Title",
        error="Timeout",
    )
    assert err.zotero_key == "ZZZZZZZZ"
    assert err.error == "Timeout"


# ---------------------------------------------------------------------------
# MigrationReport
# ---------------------------------------------------------------------------


def test_migration_report_defaults():
    from scitex.scholar.integration.zotero.migration_report import MigrationReport

    r = MigrationReport(direction="zotero_to_scholar")
    assert r.total_items == 0
    assert r.imported == 0
    assert r.skipped == 0
    assert r.failed == 0
    assert r.pdfs_copied == 0
    assert r.pdfs_missing == 0
    assert r.errors == []
    assert r.items == []


def test_migration_report_summary_contains_direction():
    from scitex.scholar.integration.zotero.migration_report import MigrationReport

    r = MigrationReport(direction="zotero_to_scholar", total_items=5, imported=3)
    s = r.summary()
    assert "zotero_to_scholar" in s
    assert "5" in s
    assert "3" in s


def test_migration_report_summary_shows_errors():
    from scitex.scholar.integration.zotero.migration_report import (
        MigrationError,
        MigrationReport,
    )

    r = MigrationReport(direction="zotero_to_scholar", total_items=2, failed=1)
    r.errors.append(MigrationError("KEY1", "Paper A", "bad error"))
    s = r.summary()
    assert "Errors" in s or "error" in s.lower()
    assert "Paper A" in s or "bad error" in s


def test_migration_report_summary_truncates_long_error_list():
    """More than 5 errors should be summarised with '... and N more'."""
    from scitex.scholar.integration.zotero.migration_report import (
        MigrationError,
        MigrationReport,
    )

    r = MigrationReport(direction="zotero_to_scholar", total_items=10, failed=10)
    for i in range(10):
        r.errors.append(MigrationError(f"KEY{i}", f"Paper {i}", "err"))
    s = r.summary()
    assert "more" in s


def test_migration_report_to_dict_structure():
    from scitex.scholar.integration.zotero.migration_report import (
        MigratedItem,
        MigrationReport,
    )

    r = MigrationReport(direction="scholar_to_zotero", total_items=1, imported=1)
    r.items.append(
        MigratedItem(
            zotero_key="K1",
            scholar_id="S1",
            title="T",
            doi="10.1/x",
            pdf_migrated=False,
            status="imported",
        )
    )
    d = r.to_dict()
    assert d["direction"] == "scholar_to_zotero"
    assert d["total_items"] == 1
    assert len(d["items"]) == 1
    assert d["items"][0]["zotero_key"] == "K1"
    assert d["items"][0]["scholar_id"] == "S1"


def test_migration_report_to_dict_items_keys():
    """to_dict items must have the documented keys."""
    from scitex.scholar.integration.zotero.migration_report import (
        MigratedItem,
        MigrationReport,
    )

    expected_keys = {
        "zotero_key",
        "scholar_id",
        "title",
        "doi",
        "pdf_migrated",
        "status",
    }
    r = MigrationReport(direction="zotero_to_scholar")
    r.items.append(MigratedItem("K", "S", "T", None, False, "skipped"))
    d = r.to_dict()
    assert set(d["items"][0].keys()) == expected_keys


# ---------------------------------------------------------------------------
# ExportPackage
# ---------------------------------------------------------------------------


def test_export_package_fields(tmp_path):
    from scitex.scholar.integration.zotero.migration_report import ExportPackage

    bib = tmp_path / "papers.bib"
    pdf_dir = tmp_path / "pdfs"
    pkg = ExportPackage(
        bibtex_path=bib,
        pdf_dir=pdf_dir,
        total_papers=10,
        total_pdfs=7,
        instructions="Open Zotero and import.",
    )
    assert pkg.total_papers == 10
    assert pkg.total_pdfs == 7
    assert pkg.bibtex_path == bib


def test_export_package_summary_contains_counts(tmp_path):
    from scitex.scholar.integration.zotero.migration_report import ExportPackage

    pkg = ExportPackage(
        bibtex_path=tmp_path / "papers.bib",
        pdf_dir=tmp_path / "pdfs",
        total_papers=3,
        total_pdfs=2,
    )
    s = pkg.summary()
    assert "3" in s
    assert "2" in s


def test_export_package_summary_shows_paths(tmp_path):
    from scitex.scholar.integration.zotero.migration_report import ExportPackage

    bib = tmp_path / "papers.bib"
    pdfs = tmp_path / "pdfs"
    pkg = ExportPackage(bibtex_path=bib, pdf_dir=pdfs, total_papers=1, total_pdfs=0)
    s = pkg.summary()
    assert str(bib) in s
    assert str(pdfs) in s


def test_export_package_default_instructions_empty():
    from scitex.scholar.integration.zotero.migration_report import ExportPackage

    pkg = ExportPackage(
        bibtex_path=Path("/tmp/p.bib"),
        pdf_dir=Path("/tmp/pdfs"),
        total_papers=0,
        total_pdfs=0,
    )
    # default instructions is an empty string
    assert pkg.instructions == ""


# ---------------------------------------------------------------------------
# SyncDiffItem
# ---------------------------------------------------------------------------


def test_sync_diff_item_defaults():
    from scitex.scholar.integration.zotero.migration_report import SyncDiffItem

    item = SyncDiffItem(title="Some Paper", doi="10.1/x")
    assert item.zotero_key is None
    assert item.scholar_id is None
    assert item.has_pdf_zotero is False
    assert item.has_pdf_scholar is False


def test_sync_diff_item_full():
    from scitex.scholar.integration.zotero.migration_report import SyncDiffItem

    item = SyncDiffItem(
        title="Paper",
        doi="10.1/x",
        zotero_key="ZKEY",
        scholar_id="SKEY",
        has_pdf_zotero=True,
        has_pdf_scholar=True,
    )
    assert item.has_pdf_zotero is True
    assert item.scholar_id == "SKEY"


# ---------------------------------------------------------------------------
# SyncDiff
# ---------------------------------------------------------------------------


def test_sync_diff_defaults():
    from scitex.scholar.integration.zotero.migration_report import SyncDiff

    d = SyncDiff()
    assert d.only_in_zotero == []
    assert d.only_in_scholar == []
    assert d.in_both == []


def test_sync_diff_summary_format():
    from scitex.scholar.integration.zotero.migration_report import (
        SyncDiff,
        SyncDiffItem,
    )

    d = SyncDiff()
    d.only_in_zotero.append(SyncDiffItem("A", None))
    d.only_in_scholar.append(SyncDiffItem("B", None))
    d.only_in_scholar.append(SyncDiffItem("C", None))
    d.in_both.append(SyncDiffItem("D", "10.1/d"))
    s = d.summary()
    assert "1" in s  # only_in_zotero count
    assert "2" in s  # only_in_scholar count


def test_sync_diff_summary_mentions_sections():
    from scitex.scholar.integration.zotero.migration_report import SyncDiff

    d = SyncDiff()
    s = d.summary()
    assert "Zotero" in s
    assert "Scholar" in s
    assert "both" in s.lower()


def test_sync_diff_independent_lists():
    """Mutation of one list must not affect others."""
    from scitex.scholar.integration.zotero.migration_report import (
        SyncDiff,
        SyncDiffItem,
    )

    d1 = SyncDiff()
    d2 = SyncDiff()
    d1.only_in_zotero.append(SyncDiffItem("X", None))
    assert len(d2.only_in_zotero) == 0


# EOF
