#!/usr/bin/env python3
"""Tests for ZoteroLocalMigrator (orchestrator) and its sub-handlers.

Tests cover:
- ZoteroLocalMigrator construction and delegation
- ZoteroImportHandler dry_run mode (Zotero DB required)
- ZoteroExportHandler export_for_import creates expected directory structure
- ZoteroDiffHandler.diff returns SyncDiff with correct fields

DB-dependent tests are skipped when ~/Zotero/zotero.sqlite is absent.
export_for_import tests use tmp_path so they are safe without a real library.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_LINUX_DB = Path("~/Zotero/zotero.sqlite").expanduser()

_DB_AVAILABLE = _LINUX_DB.exists()

# ---------------------------------------------------------------------------
# Helper: build a minimal fake MASTER directory tree
# ---------------------------------------------------------------------------


def _make_master_entry(
    master_dir: Path, entry_id: str, title: str, doi: str = ""
) -> Path:
    """Create a fake Scholar MASTER/<entry_id>/metadata.json for export tests."""
    entry = master_dir / entry_id
    entry.mkdir(parents=True, exist_ok=True)
    metadata = {
        "metadata": {
            "basic": {
                "title": title,
                "authors": ["Smith, John"],
                "year": 2023,
                "abstract": "Test abstract.",
            },
            "id": {"doi": doi},
            "publication": {
                "journal": "Test Journal",
                "volume": "1",
                "issue": "1",
                "pages": "1-10",
                "publisher": "Test Publisher",
            },
        }
    }
    (entry / "metadata.json").write_text(json.dumps(metadata))
    return entry


# ---------------------------------------------------------------------------
# ZoteroLocalMigrator – construction (no DB needed for structure check)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_migrator_construction():
    """ZoteroLocalMigrator builds all sub-handlers without raising."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator(project="test_project")
    assert m.project == "test_project"
    assert m.reader is not None
    assert m._importer is not None
    assert m._exporter is not None
    assert m._differ is not None


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_migrator_reader_db_path():
    """reader.db_path should be the auto-detected Linux DB."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator()
    assert m.reader.db_path == _LINUX_DB


# ---------------------------------------------------------------------------
# import_all dry_run – DB required
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_all_dry_run_returns_migration_report():
    """dry_run=True returns a MigrationReport without writing anything."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator
    from scitex.scholar.integration.zotero.migration_report import MigrationReport

    m = ZoteroLocalMigrator(project="test_dry_run")
    report = m.import_all(limit=3, dry_run=True)
    assert isinstance(report, MigrationReport)


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_all_dry_run_direction():
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator(project="test_dry_run_direction")
    report = m.import_all(limit=3, dry_run=True)
    assert report.direction == "zotero_to_scholar"


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_all_dry_run_items_have_would_import_status():
    """Each item in a dry-run report should have status 'would_import'."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator(project="test_dry_run_status")
    report = m.import_all(limit=5, dry_run=True)
    for item in report.items:
        assert item.status == "would_import", (
            f"Expected 'would_import', got '{item.status}' for {item.title!r}"
        )


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_all_dry_run_does_not_write_to_disk(tmp_path):
    """dry_run must not create any Scholar library entries on disk."""
    from unittest.mock import PropertyMock, patch

    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator(project="test_dry_run_no_write")
    pm = m._importer._library_manager.config.path_manager
    fake_master = tmp_path / "MASTER"
    with patch.object(
        type(pm), "library_dir", new_callable=PropertyMock, return_value=tmp_path
    ):
        m.import_all(limit=3, dry_run=True)
    assert not fake_master.exists() or len(list(fake_master.iterdir())) == 0


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_all_dry_run_total_items_matches_imported():
    """In dry_run, total_items should match items actually processed."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator

    m = ZoteroLocalMigrator(project="test_dry_run_counts")
    report = m.import_all(limit=5, dry_run=True)
    assert report.imported == len(report.items)


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_by_tags_dry_run_nonexistent_tag():
    """Importing a non-existent tag returns an empty report gracefully."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator
    from scitex.scholar.integration.zotero.migration_report import MigrationReport

    m = ZoteroLocalMigrator(project="test_tag_dry_run")
    report = m.import_by_tags(["NonExistentTag_XYZ_999"], dry_run=True)
    assert isinstance(report, MigrationReport)
    assert report.imported == 0
    assert len(report.items) == 0


# ---------------------------------------------------------------------------
# import_collection dry_run – DB required
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_import_collection_nonexistent_dry_run():
    """Importing a non-existent collection returns empty report without error."""
    from scitex.scholar.integration.zotero import ZoteroLocalMigrator
    from scitex.scholar.integration.zotero.migration_report import MigrationReport

    m = ZoteroLocalMigrator(project="test_coll_dry")
    report = m.import_collection("NoSuchCollection", dry_run=True)
    assert isinstance(report, MigrationReport)
    assert report.imported == 0


# ---------------------------------------------------------------------------
# ZoteroExportHandler.export_for_import – uses tmp_path, no real library needed
# ---------------------------------------------------------------------------


def test_export_for_import_creates_output_dir(tmp_path):
    """export_for_import creates the output directory."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    master_dir = library_dir / "MASTER"
    master_dir.mkdir(parents=True)
    _make_master_entry(master_dir, "ENTRY0001", "Test Paper A", "10.1/a")

    # Build a minimal fake LibraryManager
    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=True)

    assert output_dir.exists()


def test_export_for_import_creates_pdfs_subdir(tmp_path):
    """export_for_import always creates a pdfs/ sub-directory."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    master_dir = library_dir / "MASTER"
    master_dir.mkdir(parents=True)
    _make_master_entry(master_dir, "ENTRY0002", "Test Paper B")

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out2"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert pkg.pdf_dir.exists()


def test_export_for_import_bibtex_created(tmp_path):
    """A papers.bib file should appear when there is at least one paper."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    master_dir = library_dir / "MASTER"
    master_dir.mkdir(parents=True)
    _make_master_entry(master_dir, "ENTRY0003", "My Paper C", "10.9/c")

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out3"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert pkg.bibtex_path.exists()
    content = pkg.bibtex_path.read_text(encoding="utf-8")
    assert "@" in content  # at least one BibTeX entry


def test_export_for_import_returns_export_package(tmp_path):
    """Return type must be ExportPackage."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler
    from scitex.scholar.integration.zotero.migration_report import ExportPackage

    library_dir = tmp_path / "scholar_library"
    master_dir = library_dir / "MASTER"
    master_dir.mkdir(parents=True)

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out4"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert isinstance(pkg, ExportPackage)


def test_export_for_import_empty_master_returns_zero_counts(tmp_path):
    """When MASTER is empty, total_papers and total_pdfs are 0."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    (library_dir / "MASTER").mkdir(parents=True)

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out5"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert pkg.total_papers == 0
    assert pkg.total_pdfs == 0


def test_export_for_import_missing_master_returns_zero_counts(tmp_path):
    """When MASTER dir does not exist, export gracefully returns empty package."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    # Note: do NOT create MASTER directory

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out6"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert pkg.total_papers == 0
    assert pkg.total_pdfs == 0


def test_export_for_import_pdf_copied(tmp_path):
    """PDF files present in MASTER entry should be copied to pdfs/ dir."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    master_dir = library_dir / "MASTER"
    master_dir.mkdir(parents=True)
    entry = _make_master_entry(master_dir, "ENTRY0007", "Paper With PDF", "10.7/p")
    # Place a fake PDF in the entry directory
    fake_pdf = entry / "paper.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_with_pdf"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=True)

    assert pkg.total_pdfs >= 1
    pdf_files = list(pkg.pdf_dir.glob("*.pdf"))
    assert len(pdf_files) >= 1


def test_export_for_import_instructions_mention_zotero(tmp_path):
    """The instructions string should mention Zotero."""
    from scitex.scholar.integration.zotero._export_handler import ZoteroExportHandler

    library_dir = tmp_path / "scholar_library"
    (library_dir / "MASTER").mkdir(parents=True)

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    output_dir = tmp_path / "export_out8"
    handler = ZoteroExportHandler(library_manager=fake_lm, project="proj")
    pkg = handler.export_for_import(output_dir=output_dir, include_pdfs=False)

    assert "Zotero" in pkg.instructions or "zotero" in pkg.instructions.lower()


# ---------------------------------------------------------------------------
# ZoteroDiffHandler.diff – DB required
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_diff_returns_sync_diff(tmp_path):
    """diff() returns a SyncDiff instance."""
    from scitex.scholar.integration.zotero import ZoteroLocalReader
    from scitex.scholar.integration.zotero._diff_handler import ZoteroDiffHandler
    from scitex.scholar.integration.zotero.migration_report import SyncDiff

    reader = ZoteroLocalReader()
    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = tmp_path / "empty_library"

    handler = ZoteroDiffHandler(reader=reader, library_manager=fake_lm)
    result = handler.diff()
    assert isinstance(result, SyncDiff)


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_diff_only_in_zotero_not_empty(tmp_path):
    """When Scholar library is empty, all Zotero items end up in only_in_zotero."""
    from scitex.scholar.integration.zotero import ZoteroLocalReader
    from scitex.scholar.integration.zotero._diff_handler import ZoteroDiffHandler

    reader = ZoteroLocalReader()
    # Point library at an empty tmp dir (no MASTER)
    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = tmp_path / "empty_lib"

    handler = ZoteroDiffHandler(reader=reader, library_manager=fake_lm)
    result = handler.diff()

    assert len(result.only_in_zotero) >= 1


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_diff_in_both_after_adding_matching_entry(tmp_path):
    """An entry that matches a Zotero item by DOI appears in in_both."""
    from scitex.scholar.integration.zotero import ZoteroLocalReader
    from scitex.scholar.integration.zotero._diff_handler import ZoteroDiffHandler

    reader = ZoteroLocalReader()
    # Find one Zotero item that has a DOI
    all_papers = reader.read_all(limit=50)
    doi_paper = None
    for p in all_papers:
        doi = getattr(p.metadata.id, "doi", None)
        if doi:
            doi_paper = p
            break

    if doi_paper is None:
        pytest.skip("No Zotero items with DOI found in the test database")

    doi = doi_paper.metadata.id.doi
    title = doi_paper.metadata.basic.title or "Untitled"

    # Build a fake MASTER entry with the same DOI
    library_dir = tmp_path / "scholar_lib"
    master_dir = library_dir / "MASTER"
    _make_master_entry(master_dir, "MATCHED0001", title, doi)

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    handler = ZoteroDiffHandler(reader=reader, library_manager=fake_lm)
    result = handler.diff()

    assert len(result.in_both) >= 1


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_diff_sync_diff_items_have_required_fields(tmp_path):
    """SyncDiffItem instances in the result have title and correct field types."""
    from scitex.scholar.integration.zotero import ZoteroLocalReader
    from scitex.scholar.integration.zotero._diff_handler import ZoteroDiffHandler

    reader = ZoteroLocalReader()
    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = tmp_path / "empty_lib2"

    handler = ZoteroDiffHandler(reader=reader, library_manager=fake_lm)
    result = handler.diff()

    for item in result.only_in_zotero:
        assert isinstance(item.title, str)
        # doi may be None or str
        assert item.doi is None or isinstance(item.doi, str)


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_diff_only_in_scholar_for_extra_entry(tmp_path):
    """A Scholar entry with no matching Zotero item lands in only_in_scholar."""
    from scitex.scholar.integration.zotero import ZoteroLocalReader
    from scitex.scholar.integration.zotero._diff_handler import ZoteroDiffHandler

    reader = ZoteroLocalReader()
    library_dir = tmp_path / "scholar_lib2"
    master_dir = library_dir / "MASTER"
    # Use a DOI that is almost certainly not in the real DB
    _make_master_entry(
        master_dir,
        "XUNIQUE001",
        "A Totally Unique Paper That Does Not Exist In Zotero",
        "10.99999/absolutely-unique-doi-xyz-999999",
    )

    fake_lm = MagicMock()
    fake_lm.config.path_manager.library_dir = library_dir

    handler = ZoteroDiffHandler(reader=reader, library_manager=fake_lm)
    result = handler.diff()

    scholar_ids = [item.scholar_id for item in result.only_in_scholar]
    assert "XUNIQUE001" in scholar_ids


@pytest.mark.skipif(
    not _DB_AVAILABLE,
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
def test_migrator_diff_returns_sync_diff(tmp_path):
    """ZoteroLocalMigrator.diff() delegates to ZoteroDiffHandler correctly."""
    from unittest.mock import PropertyMock, patch

    from scitex.scholar.integration.zotero import ZoteroLocalMigrator
    from scitex.scholar.integration.zotero.migration_report import SyncDiff

    m = ZoteroLocalMigrator(project="test_diff_delegation")
    pm = m._differ._library_manager.config.path_manager
    with patch.object(
        type(pm), "library_dir", new_callable=PropertyMock, return_value=tmp_path
    ):
        result = m.diff()
    assert isinstance(result, SyncDiff)


# EOF
