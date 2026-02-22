#!/usr/bin/env python3
"""Tests for ZoteroAttachmentResolver and ResolvedAttachment.

Unit tests (path resolution logic, path traversal guard) do not require
a live Zotero database.  Integration tests that call
list_attachments_for_items() with a real connection are skipped when the
local database is absent.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

_LINUX_DB = Path("~/Zotero/zotero.sqlite").expanduser()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def base_dir(tmp_path):
    """Fake Zotero data directory with a storage/ sub-tree."""
    storage = tmp_path / "storage"
    storage.mkdir()
    return tmp_path


@pytest.fixture()
def resolver(base_dir):
    from scitex.scholar.integration.zotero.attachment_resolver import (
        ZoteroAttachmentResolver,
    )

    return ZoteroAttachmentResolver(base_dir)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_resolver_stores_base_dir(base_dir):
    from scitex.scholar.integration.zotero.attachment_resolver import (
        ZoteroAttachmentResolver,
    )

    r = ZoteroAttachmentResolver(base_dir)
    assert r.base_dir == base_dir


def test_resolver_storage_dir_is_base_slash_storage(base_dir):
    from scitex.scholar.integration.zotero.attachment_resolver import (
        ZoteroAttachmentResolver,
    )

    r = ZoteroAttachmentResolver(base_dir)
    assert r.storage_dir == base_dir / "storage"


# ---------------------------------------------------------------------------
# resolve() – linkMode 3 (embedded note) always returns None
# ---------------------------------------------------------------------------


def test_resolve_link_mode_3_returns_none(resolver):
    result = resolver.resolve("storage:somefile.pdf", "ABCD1234", link_mode=3)
    assert result is None


def test_resolve_none_path_returns_none(resolver):
    result = resolver.resolve(None, "ABCD1234", link_mode=0)
    assert result is None


def test_resolve_empty_path_returns_none(resolver):
    result = resolver.resolve("", "ABCD1234", link_mode=0)
    assert result is None


# ---------------------------------------------------------------------------
# resolve() – linkMode 0/1 (storage: prefix)
# ---------------------------------------------------------------------------


def test_resolve_storage_prefix_existing_file(resolver, base_dir):
    """A real file under storage/<key>/ resolves correctly."""
    item_key = "TESTKEY1"
    key_dir = base_dir / "storage" / item_key
    key_dir.mkdir(parents=True)
    pdf = key_dir / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    result = resolver.resolve("storage:paper.pdf", item_key, link_mode=0)
    assert result == pdf.resolve()


def test_resolve_storage_prefix_missing_file_returns_none(resolver):
    """If the file does not exist on disk, resolve() returns None."""
    result = resolver.resolve("storage:missing.pdf", "NOKEY999", link_mode=0)
    assert result is None


# ---------------------------------------------------------------------------
# resolve() – path traversal guard
# ---------------------------------------------------------------------------


def test_resolve_path_traversal_is_blocked(resolver):
    """'storage:../../etc/passwd' must be rejected even if the path exists."""
    result = resolver.resolve("storage:../../etc/passwd", "ANYKEY11", link_mode=0)
    assert result is None


def test_resolve_linked_file_traversal_is_blocked(resolver):
    """Linked-file path that escapes base_dir must be rejected."""
    result = resolver.resolve("../../etc/passwd", "ANYKEY22", link_mode=2)
    assert result is None


# ---------------------------------------------------------------------------
# resolve() – linkMode 2 (linked file)
# ---------------------------------------------------------------------------


def test_resolve_linked_absolute_existing(resolver, tmp_path):
    """Absolute linked path that exists is returned as-is."""
    pdf = tmp_path / "linked.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    result = resolver.resolve(str(pdf), "ANYKEY33", link_mode=2)
    assert result == pdf


def test_resolve_linked_absolute_missing_returns_none(resolver, tmp_path):
    pdf = tmp_path / "no_such.pdf"
    result = resolver.resolve(str(pdf), "ANYKEY44", link_mode=2)
    assert result is None


def test_resolve_linked_relative_existing(resolver, base_dir):
    """Relative linked path is resolved relative to base_dir."""
    rel_pdf = base_dir / "my_papers" / "rel.pdf"
    rel_pdf.parent.mkdir()
    rel_pdf.write_bytes(b"%PDF-1.4")
    result = resolver.resolve("my_papers/rel.pdf", "ANYKEY55", link_mode=2)
    assert result == rel_pdf.resolve()


# ---------------------------------------------------------------------------
# ResolvedAttachment dataclass
# ---------------------------------------------------------------------------


def test_resolved_attachment_fields():
    from scitex.scholar.integration.zotero.attachment_resolver import (
        ResolvedAttachment,
    )

    att = ResolvedAttachment(
        path=Path("/some/file.pdf"),
        filename="file.pdf",
        content_type="application/pdf",
        is_pdf=True,
        link_mode=0,
        zotero_key="ABCD1234",
        size_bytes=1024,
    )
    assert att.is_pdf is True
    assert att.size_bytes == 1024
    assert att.zotero_key == "ABCD1234"


def test_resolved_attachment_is_pdf_false_for_other_types():
    from scitex.scholar.integration.zotero.attachment_resolver import (
        ResolvedAttachment,
    )

    att = ResolvedAttachment(
        path=Path("/some/file.html"),
        filename="file.html",
        content_type="text/html",
        is_pdf=False,
        link_mode=1,
        zotero_key="ZZZZZZZZ",
        size_bytes=512,
    )
    assert att.is_pdf is False


# ---------------------------------------------------------------------------
# list_attachments_for_items() – integration tests (need real DB)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not _LINUX_DB.exists(),
    reason="No local Zotero database at ~/Zotero/zotero.sqlite",
)
class TestListAttachmentsIntegration:
    """Integration tests using the real local Zotero database."""

    @pytest.fixture(scope="class")
    def live_resolver(self):
        from scitex.scholar.integration.zotero.attachment_resolver import (
            ZoteroAttachmentResolver,
        )

        return ZoteroAttachmentResolver(_LINUX_DB.parent)

    @pytest.fixture(scope="class")
    def live_conn(self):
        conn = sqlite3.connect(f"file:{_LINUX_DB}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    def test_empty_item_ids_returns_empty_dict(self, live_resolver, live_conn):
        result = live_resolver.list_attachments_for_items([], live_conn)
        assert result == {}

    def test_returns_dict_keyed_by_item_id(self, live_resolver, live_conn):
        """Result maps each requested item_id even when no attachments exist."""
        rows = live_conn.execute(
            """
            SELECT i.itemID FROM items i
            JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
            WHERE it.typeName NOT IN ('attachment','note','annotation')
            LIMIT 5
            """
        ).fetchall()
        item_ids = [r[0] for r in rows]
        result = live_resolver.list_attachments_for_items(item_ids, live_conn)
        for iid in item_ids:
            assert iid in result
            assert isinstance(result[iid], list)

    def test_pdf_only_filter(self, live_resolver, live_conn):
        """When pdf_only=True, returned attachments are all PDFs."""
        rows = live_conn.execute(
            """
            SELECT i.itemID FROM items i
            JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
            WHERE it.typeName NOT IN ('attachment','note','annotation')
            LIMIT 20
            """
        ).fetchall()
        item_ids = [r[0] for r in rows]
        result = live_resolver.list_attachments_for_items(
            item_ids, live_conn, pdf_only=True
        )
        for atts in result.values():
            for att in atts:
                assert att.is_pdf, f"Expected PDF but got: {att.content_type}"

    def test_resolved_attachment_has_existing_path(self, live_resolver, live_conn):
        """Every resolved attachment points to a file that exists on disk."""
        rows = live_conn.execute(
            """
            SELECT i.itemID FROM items i
            JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
            WHERE it.typeName NOT IN ('attachment','note','annotation')
            LIMIT 50
            """
        ).fetchall()
        item_ids = [r[0] for r in rows]
        result = live_resolver.list_attachments_for_items(
            item_ids, live_conn, pdf_only=False
        )
        for atts in result.values():
            for att in atts:
                assert att.path.exists(), f"Resolved path does not exist: {att.path}"


# EOF
