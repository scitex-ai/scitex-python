"""Citation graph API routes for Scholar GUI.

Ported from scitex-cloud/apps/scholar_app/api/citation_graph.py
(Django REST → Flask).
"""

import hashlib
import logging
import time
from typing import Dict, Optional

from flask import Flask, current_app, jsonify, request

logger = logging.getLogger(__name__)

# Simple in-memory cache (no Django cache dependency)
_cache: Dict[str, dict] = {}
_cache_timestamps: Dict[str, float] = {}
_CACHE_TTL = 3600  # 1 hour


def _cache_get(key: str) -> Optional[dict]:
    """Get value from cache if not expired."""
    if key in _cache:
        if time.time() - _cache_timestamps.get(key, 0) < _CACHE_TTL:
            return _cache[key]
        del _cache[key]
        del _cache_timestamps[key]
    return None


def _cache_set(key: str, value: dict, ttl: int = _CACHE_TTL):
    """Set value in cache."""
    _cache[key] = value
    _cache_timestamps[key] = time.time()


def _make_cache_key(prefix: str, doi: str, **kwargs) -> str:
    """Create cache key from parameters."""
    parts = [prefix, doi.lower()]
    for k, v in sorted(kwargs.items()):
        parts.append(f"{k}={v}")
    return f"cg:{hashlib.md5(':'.join(parts).encode()).hexdigest()}"


def _get_builder():
    """Get or create CitationGraphBuilder from app config."""
    db_path = current_app.config.get("CROSSREF_DB_PATH")
    if not db_path:
        return None

    from scitex.scholar.citation_graph import CitationGraphBuilder

    return CitationGraphBuilder(db_path)


def register_graph_routes(app: Flask):
    """Register citation graph API routes."""

    @app.route("/api/graph/network")
    def graph_network():
        """Build citation network for a DOI."""
        doi = request.args.get("doi")
        if not doi:
            return jsonify({"error": "DOI parameter required"}), 400

        try:
            top_n = int(request.args.get("top_n", 20))
            top_n = max(1, min(50, top_n))
            weight_coupling = float(request.args.get("weight_coupling", 2.0))
            weight_cocitation = float(request.args.get("weight_cocitation", 2.0))
            weight_direct = float(request.args.get("weight_direct", 1.0))
        except ValueError as e:
            return jsonify({"error": f"Invalid parameter: {e}"}), 400

        use_cache = request.args.get("no_cache", "false").lower() != "true"

        # Check cache
        cache_key = _make_cache_key(
            "net",
            doi,
            top_n=top_n,
            wc=weight_coupling,
            wco=weight_cocitation,
            wd=weight_direct,
        )
        if use_cache:
            cached = _cache_get(cache_key)
            if cached:
                cached["metadata"]["cached"] = True
                return jsonify(cached)

        # Build network
        builder = _get_builder()
        if not builder:
            return jsonify({"error": "CrossRef database not configured"}), 503

        try:
            graph = builder.build(
                seed_doi=doi,
                top_n=top_n,
                weight_coupling=weight_coupling,
                weight_cocitation=weight_cocitation,
                weight_direct=weight_direct,
            )
            result = graph.to_dict()
            result["metadata"]["cached"] = False

            # Mark seed node
            for node in result["nodes"]:
                node["is_seed"] = node["id"].lower() == doi.lower()

            _cache_set(cache_key, result)
            return jsonify(result)

        except FileNotFoundError:
            return jsonify({"error": "CrossRef database not found"}), 503
        except Exception as e:
            logger.error(f"Error building network for {doi}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to build network: {e}"}), 500

    @app.route("/api/graph/related")
    def graph_related():
        """Get related papers for a DOI."""
        doi = request.args.get("doi")
        if not doi:
            return jsonify({"error": "DOI parameter required"}), 400

        try:
            limit = int(request.args.get("limit", 10))
            limit = max(1, min(30, limit))
        except ValueError as e:
            return jsonify({"error": f"Invalid parameter: {e}"}), 400

        builder = _get_builder()
        if not builder:
            return jsonify({"error": "CrossRef database not configured"}), 503

        try:
            graph = builder.build(seed_doi=doi, top_n=limit)
            result = graph.to_dict()

            # Sort by similarity, exclude seed
            related = sorted(
                [n for n in result["nodes"] if n["id"].lower() != doi.lower()],
                key=lambda n: n.get("similarity_score", 0),
                reverse=True,
            )[:limit]

            return jsonify({"doi": doi, "related": related, "count": len(related)})

        except Exception as e:
            logger.error(f"Error getting related papers for {doi}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to get related papers: {e}"}), 500

    @app.route("/api/graph/paper")
    def graph_paper():
        """Get paper summary."""
        doi = request.args.get("doi")
        if not doi:
            return jsonify({"error": "DOI parameter required"}), 400

        builder = _get_builder()
        if not builder:
            return jsonify({"error": "CrossRef database not configured"}), 503

        try:
            summary = builder.get_paper_summary(doi)
            if summary:
                return jsonify(summary)
            return jsonify({"error": "Paper not found"}), 404

        except Exception as e:
            logger.error(f"Error getting paper summary for {doi}: {e}", exc_info=True)
            return jsonify({"error": f"Failed to get summary: {e}"}), 500

    @app.route("/api/graph/health")
    def graph_health():
        """Health check for citation graph service."""
        db_path = current_app.config.get("CROSSREF_DB_PATH")
        if not db_path:
            return jsonify(
                {"status": "unhealthy", "error": "No database configured"}
            ), 503

        try:
            builder = _get_builder()
            summary = builder.get_paper_summary("10.1038/s41586-020-2008-3")
            return jsonify(
                {
                    "status": "healthy" if summary else "degraded",
                    "database": db_path,
                    "database_accessible": True,
                }
            )
        except Exception as e:
            return jsonify(
                {
                    "status": "unhealthy",
                    "database": db_path,
                    "error": str(e),
                }
            ), 503


# EOF
