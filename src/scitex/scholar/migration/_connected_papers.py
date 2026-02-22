#!/usr/bin/env python3
"""Connected Papers import/export for scitex.scholar.

Import: Fetch a Connected Papers graph and convert to CitationGraph or Papers.
Export: Convert CitationGraph to BibTeX/JSON importable by CP web UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ._s2_resolver import bulk_resolve_dois, bulk_resolve_metadata


def from_connected_papers(
    paper_id: str,
    *,
    cp_api_key: Optional[str] = None,
    s2_api_key: Optional[str] = None,
    output_format: str = "citation_graph",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Import a Connected Papers graph into scitex.

    Parameters
    ----------
    paper_id : str
        Semantic Scholar paper ID (40-char SHA) for the seed paper.
    cp_api_key : str, optional
        Connected Papers API key.
    s2_api_key : str, optional
        Semantic Scholar API key for DOI resolution.
    output_format : str
        "citation_graph" returns CitationGraph, "papers" returns Papers.
    dry_run : bool
        If True, fetch and report stats without creating objects.

    Returns
    -------
    dict
        {success: True, graph/papers, stats, warnings} or
        {success: False, error: str}.
    """
    try:
        import connectedpapers
    except ImportError:
        return {
            "success": False,
            "error": (
                "connectedpapers-py is required. "
                "Install with: pip install connectedpapers-py"
            ),
        }

    if output_format not in ("citation_graph", "papers"):
        return {
            "success": False,
            "error": f"Invalid output_format: {output_format!r}. "
            "Must be 'citation_graph' or 'papers'.",
        }

    warnings: List[str] = []

    try:
        # Fetch graph from Connected Papers API
        client = connectedpapers.Client(api_key=cp_api_key)
        graph_response = client.get_graph_sync(paper_id)

        if not hasattr(graph_response, "graph"):
            return {"success": False, "error": "No graph data in CP response."}

        cp_graph = graph_response.graph
        nodes = cp_graph.nodes or {}
        edges = cp_graph.edges or {}

        # Collect all S2 paper IDs from graph
        s2_ids = list(nodes.keys())
        if not s2_ids:
            return {
                "success": True,
                "dry_run": dry_run,
                "stats": {"node_count": 0, "edge_count": 0, "resolved_dois": 0},
                "warnings": ["Graph contains no papers."],
            }

        # Bulk resolve S2 IDs → DOIs
        doi_map = bulk_resolve_dois(s2_ids, api_key=s2_api_key)
        resolved_count = sum(1 for v in doi_map.values() if v is not None)
        unresolved = [k for k, v in doi_map.items() if v is None]

        if unresolved:
            warnings.append(f"{len(unresolved)} papers could not be resolved to DOIs.")

        stats = {
            "node_count": len(s2_ids),
            "edge_count": len(edges),
            "resolved_dois": resolved_count,
            "unresolved_count": len(unresolved),
        }

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "stats": stats,
                "warnings": warnings,
            }

        # Get full metadata for resolved papers
        metadata_map = bulk_resolve_metadata(s2_ids, api_key=s2_api_key)

        if output_format == "citation_graph":
            result_obj = _build_citation_graph(
                paper_id, nodes, edges, doi_map, metadata_map, warnings
            )
            return {
                "success": True,
                "dry_run": False,
                "graph": result_obj,
                "stats": stats,
                "warnings": warnings,
            }
        else:
            result_obj = _build_papers(doi_map, metadata_map, warnings)
            return {
                "success": True,
                "dry_run": False,
                "papers": result_obj,
                "stats": stats,
                "warnings": warnings,
            }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


def to_connected_papers(
    graph,
    *,
    output: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Export a CitationGraph as BibTeX/JSON for Connected Papers.

    Parameters
    ----------
    graph : CitationGraph
        Citation graph to export.
    output : str or Path, optional
        Output directory. Defaults to current directory.

    Returns
    -------
    dict
        {success, bibtex_path, json_path, paper_count} or {success: False, error}.
    """
    try:
        from scitex.scholar import to_bibtex

        out_dir = Path(output) if output else Path.cwd()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Export as JSON (graph structure with S2-compatible metadata)
        json_path = out_dir / "connected_papers_export.json"
        _write_json(json_path, graph.to_dict())

        # Export as BibTeX (importable by CP web UI)
        bibtex_path = out_dir / "connected_papers_export.bib"
        entries = []
        for node in graph.nodes:
            if node.doi:
                bib = to_bibtex(
                    doi=node.doi,
                    title=node.title,
                    year=node.year,
                    authors=node.authors,
                    journal=node.journal,
                )
                entries.append(bib)

        bibtex_path.write_text("\n\n".join(entries), encoding="utf-8")

        return {
            "success": True,
            "bibtex_path": str(bibtex_path),
            "json_path": str(json_path),
            "paper_count": len(graph.nodes),
            "bibtex_entries": len(entries),
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_citation_graph(seed_id, nodes, edges, doi_map, metadata_map, warnings):
    """Convert CP graph data to CitationGraph."""
    from scitex.scholar.citation_graph.models import (
        CitationEdge,
        CitationGraph,
        PaperNode,
    )

    seed_doi = doi_map.get(seed_id, seed_id)
    paper_nodes = []

    for s2_id, node_data in nodes.items():
        doi = doi_map.get(s2_id)
        meta = metadata_map.get(s2_id, {}) or {}
        ext_ids = meta.get("externalIds", {}) or {}
        authors = [a.get("name", "") for a in (meta.get("authors") or [])]

        paper_nodes.append(
            PaperNode(
                doi=doi or s2_id,
                title=meta.get("title", getattr(node_data, "title", "")),
                year=meta.get("year", 0) or 0,
                authors=authors,
                journal=meta.get("venue", ""),
                citation_count=meta.get("citationCount", 0) or 0,
                is_seed=(s2_id == seed_id),
                metadata={"s2_id": s2_id, "external_ids": ext_ids},
            )
        )

    citation_edges = []
    for edge_data in edges if isinstance(edges, list) else edges.values():
        src = getattr(edge_data, "source", None)
        tgt = getattr(edge_data, "target", None)
        if src and tgt:
            citation_edges.append(
                CitationEdge(
                    source=doi_map.get(src, src),
                    target=doi_map.get(tgt, tgt),
                    edge_type="similar",
                    weight=getattr(edge_data, "weight", 1.0),
                )
            )

    return CitationGraph(
        seed_doi=seed_doi or seed_id,
        seed_dois=[seed_doi] if seed_doi else [],
        nodes=paper_nodes,
        edges=citation_edges,
        metadata={"source": "connected_papers", "seed_s2_id": seed_id},
    )


def _build_papers(doi_map, metadata_map, warnings):
    """Convert resolved metadata to Papers collection."""
    from scitex.scholar.core import Paper, Papers

    papers = []
    for s2_id, meta in metadata_map.items():
        if meta is None:
            continue
        doi = doi_map.get(s2_id)
        if not doi:
            continue
        try:
            paper = Paper()
            paper.metadata.set_doi(doi)
            paper.metadata.basic.title = meta.get("title", "")
            paper.metadata.basic.year = meta.get("year")
            paper.metadata.basic.authors = [
                a.get("name", "") for a in (meta.get("authors") or [])
            ]
            papers.append(paper)
        except Exception as exc:
            warnings.append(f"Failed to create Paper for {doi}: {exc}")

    return Papers(papers)


def _write_json(path: Path, data: dict) -> None:
    """Write dict to JSON file."""
    import json

    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# EOF
