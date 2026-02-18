#!/usr/bin/env python3
"""
Zotero integration for SciTeX Scholar module.

This module provides bidirectional integration with Zotero reference manager:
- Import: Bibliography with collections/tags, PDF annotations, paper metadata
- Export: Manuscripts as preprint entries, project metadata, citation files (.bib, .ris)
- Link: Live citation insertion, auto-update on library changes, tagged items

Public API:
- ZoteroImporter: Import data from Zotero
- ZoteroExporter: Export data to Zotero
- ZoteroLinker: Live synchronization with Zotero
"""

from .exporter import ZoteroExporter
from .importer import ZoteroImporter
from .linker import ZoteroLinker
from .local_reader import ZoteroLocalReader, export_for_zotero
from .mapper import ZoteroMapper

__all__ = [
    "ZoteroImporter",
    "ZoteroExporter",
    "ZoteroLinker",
    "ZoteroLocalReader",
    "ZoteroMapper",
    "export_for_zotero",
]
