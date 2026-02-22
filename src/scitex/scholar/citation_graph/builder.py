"""
Citation Graph Builder

Main interface for building citation networks from CrossRef data.
"""

import json
from pathlib import Path
from typing import List, Optional

from .database import CitationDatabase
from .models import CitationEdge, CitationGraph, PaperNode


class CitationGraphBuilder:
    """
    Build citation network graphs for academic papers.

    Auto-detects backend via crossref_local.Config (DB → HTTP).

    Example (auto-detect):
        >>> builder = CitationGraphBuilder()
        >>> graph = builder.build("10.1038/s41586-020-2008-3", top_n=20)

    Example (explicit SQLite):
        >>> builder = CitationGraphBuilder(db_path="/path/to/crossref.db")

    Example (explicit HTTP):
        >>> builder = CitationGraphBuilder(api_url="http://localhost:31291")
    """

    def __init__(self, db_path: str = None, api_url: str = None):
        """
        Initialize builder with database path, HTTP API URL, or auto-detect.

        When no args given, delegates to crossref_local.Config for auto-detection:
        1. CROSSREF_LOCAL_MODE env var (explicit "db" or "http")
        2. CROSSREF_LOCAL_API_URL env var → HTTP mode
        3. Local DB file existence → DB mode
        4. Fallback to HTTP mode

        Args:
            db_path: Path to CrossRef SQLite database (local mode)
            api_url: URL of crossref-local HTTP API (HTTP mode)
        """
        if api_url:
            from .database_http import CitationDatabaseHTTP

            self.db_path = None
            self.db = CitationDatabaseHTTP(api_url)
        elif db_path:
            self.db_path = db_path
            self.db = CitationDatabase(db_path)
        else:
            self._auto_detect()

    def _auto_detect(self):
        """Auto-detect backend via crossref_local.Config."""
        from crossref_local._core.config import Config

        mode = Config.get_mode()

        if mode == "db":
            self.db_path = str(Config.get_db_path())
            self.db = CitationDatabase(self.db_path)
        else:
            from .database_http import CitationDatabaseHTTP

            self.db_path = None
            self.db = CitationDatabaseHTTP(Config.get_api_url())

    def build(
        self,
        seed_doi: str,
        top_n: int = 20,
        weight_coupling: float = 2.0,
        weight_cocitation: float = 2.0,
        weight_direct: float = 1.0,
    ) -> CitationGraph:
        """
        Build citation network around a seed paper.

        Args:
            seed_doi: DOI of the seed paper
            top_n: Number of most similar papers to include
            weight_coupling: Weight for bibliographic coupling
            weight_cocitation: Weight for co-citation
            weight_direct: Weight for direct citations

        Returns
        -------
            CitationGraph object with nodes and edges
        """
        with self.db:
            # Calculate similarity scores
            scores = self.db.get_combined_similarity_scores(
                seed_doi,
                weight_coupling=weight_coupling,
                weight_cocitation=weight_cocitation,
                weight_direct=weight_direct,
            )

            # Get top N most similar papers
            top_dois = [seed_doi] + [doi for doi, _ in scores.most_common(top_n)]

            # Build nodes with metadata
            nodes = []
            for doi in top_dois:
                node = self._create_paper_node(doi, scores.get(doi, 100.0))
                if doi == seed_doi:
                    node.is_seed = True
                nodes.append(node)

            # Build edges (citations between papers in network)
            edges = self._build_citation_edges(top_dois)

            # Create graph
            graph = CitationGraph(
                seed_doi=seed_doi,
                seed_dois=[seed_doi],
                nodes=nodes,
                edges=edges,
                metadata={
                    "top_n": top_n,
                    "weights": {
                        "coupling": weight_coupling,
                        "cocitation": weight_cocitation,
                        "direct": weight_direct,
                    },
                },
            )

            return graph

    def _create_paper_node(self, doi: str, similarity_score: float) -> PaperNode:
        """
        Create a PaperNode with metadata from database.

        Args:
            doi: DOI of the paper
            similarity_score: Calculated similarity score

        Returns
        -------
            PaperNode object
        """
        metadata = self.db.get_paper_metadata(doi)

        if metadata:
            # Extract author names
            authors = metadata.get("author", [])
            author_names = [
                f"{a.get('family', '')} {a.get('given', '')[:1]}" for a in authors[:3]
            ]

            # Extract year
            year = 0
            if "published" in metadata and "date-parts" in metadata["published"]:
                date_parts = metadata["published"]["date-parts"]
                if date_parts and date_parts[0]:
                    year = date_parts[0][0] if date_parts[0][0] else 0

            # Extract journal
            journal = ""
            if "container-title" in metadata and metadata["container-title"]:
                journal = metadata["container-title"][0]

            return PaperNode(
                doi=doi,
                title=metadata.get("title", ["Unknown"])[0][:200],
                year=year,
                authors=author_names,
                journal=journal,
                similarity_score=similarity_score,
            )
        else:
            return PaperNode(doi=doi, similarity_score=similarity_score)

    def _build_citation_edges(self, dois: List[str]) -> List[CitationEdge]:
        """
        Build citation edges between papers in the network.

        Args:
            dois: List of DOIs in the network

        Returns
        -------
            List of CitationEdge objects
        """
        edges = []
        doi_set = set(d.lower() for d in dois)

        for doi in dois:
            # Get references (papers this one cites)
            refs = self.db.get_references(doi, limit=100)

            for cited_doi in refs:
                if cited_doi in doi_set:
                    edges.append(
                        CitationEdge(
                            source=doi,
                            target=cited_doi,
                            edge_type="cites",
                        )
                    )

        return edges

    def build_from_dois(
        self,
        dois: List[str],
        num_related_per_doi: int = 20,
        weight_coupling: float = 2.0,
        weight_cocitation: float = 2.0,
        weight_direct: float = 1.0,
    ) -> CitationGraph:
        """
        Build citation network from multiple seed DOIs.

        Combines similarity scores from all seeds to find papers
        related to the entire set, producing a richer connected graph.

        Args:
            dois: List of seed DOIs
            num_related_per_doi: Number of related papers to discover per DOI
            weight_coupling: Weight for bibliographic coupling
            weight_cocitation: Weight for co-citation
            weight_direct: Weight for direct citations

        Returns
        -------
            CitationGraph with all seeds + related papers + edges
        """
        with self.db:
            seed_set = set(d.lower() for d in dois)

            # Batch query: 4 SQL queries total regardless of DOI count
            combined_scores = self.db.get_combined_similarity_scores_batch(
                dois,
                weight_coupling=weight_coupling,
                weight_cocitation=weight_cocitation,
                weight_direct=weight_direct,
            )

            # Top N related papers (scaled by number of seeds)
            top_count = num_related_per_doi * len(dois)
            related_dois = [doi for doi, _ in combined_scores.most_common(top_count)]

            # All DOIs = seeds + related
            all_dois = list(dois) + related_dois

            # Build nodes
            nodes = []
            for doi in all_dois:
                score = combined_scores.get(doi, 100.0)
                node = self._create_paper_node(doi, score)
                if doi.lower() in seed_set:
                    node.is_seed = True
                nodes.append(node)

            # Build edges
            edges = self._build_citation_edges(all_dois)

            return CitationGraph(
                seed_doi=dois[0],
                seed_dois=list(dois),
                nodes=nodes,
                edges=edges,
                metadata={
                    "num_related_per_doi": num_related_per_doi,
                    "num_seeds": len(dois),
                    "weights": {
                        "coupling": weight_coupling,
                        "cocitation": weight_cocitation,
                        "direct": weight_direct,
                    },
                },
            )

    def build_from_query(
        self,
        query: str,
        num_related_per_doi: int = 20,
        search_limit: int = 10,
        weight_coupling: float = 2.0,
        weight_cocitation: float = 2.0,
        weight_direct: float = 1.0,
    ) -> CitationGraph:
        """
        Build citation network from a text query.

        Searches local databases, extracts DOIs from results,
        then delegates to build_from_dois().

        Args:
            query: Search query (e.g. "hippocampal sharp wave ripples")
            num_related_per_doi: Related papers per seed DOI
            search_limit: Max papers to fetch from search
            weight_coupling: Weight for bibliographic coupling
            weight_cocitation: Weight for co-citation
            weight_direct: Weight for direct citations

        Returns
        -------
            CitationGraph with search-discovered seeds + related papers
        """
        from ..local_dbs.unified import search

        results = search(query, limit=search_limit)
        dois = [w.doi for w in results.works if w.doi and w.doi.strip()]

        if not dois:
            return CitationGraph(
                seed_doi="",
                seed_dois=[],
                nodes=[],
                edges=[],
                metadata={"query": query, "error": "No papers with DOI found"},
            )

        graph = self.build_from_dois(
            dois=dois,
            num_related_per_doi=num_related_per_doi,
            weight_coupling=weight_coupling,
            weight_cocitation=weight_cocitation,
            weight_direct=weight_direct,
        )
        graph.metadata["query"] = query
        graph.metadata["search_results_count"] = len(results.works)
        return graph

    def export_json(self, graph: CitationGraph, output_path: str):
        """
        Export graph to JSON file for visualization.

        Args:
            graph: CitationGraph to export
            output_path: Path to output JSON file
        """
        output = Path(output_path)
        with open(output, "w") as f:
            json.dump(graph.to_dict(), f, indent=2)

    def get_paper_summary(self, doi: str) -> Optional[dict]:
        """
        Get summary information for a paper.

        Args:
            doi: DOI of the paper

        Returns
        -------
            Dictionary with paper summary
        """
        with self.db:
            metadata = self.db.get_paper_metadata(doi)

            if not metadata:
                return None

            # Get citation counts
            refs = self.db.get_references(doi, limit=1000)
            citations = self.db.get_citations(doi, limit=1000)

            return {
                "doi": doi,
                "title": metadata.get("title", ["Unknown"])[0],
                "year": metadata.get("published", {}).get("date-parts", [[0]])[0][0],
                "authors": [
                    f"{a.get('family', '')} {a.get('given', '')}"
                    for a in metadata.get("author", [])[:5]
                ],
                "journal": metadata.get("container-title", ["Unknown"])[0],
                "reference_count": len(refs),
                "citation_count": len(citations),
            }
