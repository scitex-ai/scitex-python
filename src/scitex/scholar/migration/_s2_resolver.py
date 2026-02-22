#!/usr/bin/env python3
"""Bulk Semantic Scholar ID → DOI resolver.

Uses SemanticScholarEngine.batch_resolve() to efficiently convert
S2 paper IDs (SHA hashes) to DOIs in bulk.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def bulk_resolve_dois(
    s2_ids: List[str],
    api_key: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """Resolve Semantic Scholar paper IDs to DOIs in bulk.

    Parameters
    ----------
    s2_ids : list of str
        Semantic Scholar paper IDs (40-char SHA hashes).
    api_key : str, optional
        S2 API key for higher rate limits.

    Returns
    -------
    dict
        Mapping {s2_paper_id: doi_or_None}.
    """
    if not s2_ids:
        return {}

    from scitex.scholar.metadata_engines.individual.SemanticScholarEngine import (
        SemanticScholarEngine,
    )

    engine = SemanticScholarEngine(api_key=api_key)
    results = engine.batch_resolve(s2_ids, fields="externalIds")

    mapping: Dict[str, Optional[str]] = {}
    for s2_id, result in zip(s2_ids, results):
        if result is None:
            mapping[s2_id] = None
            continue
        external_ids = result.get("externalIds", {}) or {}
        mapping[s2_id] = external_ids.get("DOI")

    return mapping


def bulk_resolve_metadata(
    s2_ids: List[str],
    api_key: Optional[str] = None,
    fields: str = "externalIds,title,year,authors,citationCount,venue",
) -> Dict[str, Optional[Dict]]:
    """Resolve S2 paper IDs to full metadata in bulk.

    Parameters
    ----------
    s2_ids : list of str
        Semantic Scholar paper IDs.
    api_key : str, optional
        S2 API key.
    fields : str
        Comma-separated S2 API fields.

    Returns
    -------
    dict
        Mapping {s2_paper_id: metadata_dict_or_None}.
    """
    if not s2_ids:
        return {}

    from scitex.scholar.metadata_engines.individual.SemanticScholarEngine import (
        SemanticScholarEngine,
    )

    engine = SemanticScholarEngine(api_key=api_key)
    results = engine.batch_resolve(s2_ids, fields=fields)

    return dict(zip(s2_ids, results))


# EOF
