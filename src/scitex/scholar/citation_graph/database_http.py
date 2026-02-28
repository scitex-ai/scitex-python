"""
HTTP-based database access layer for citation graph queries.

Uses crossref-local HTTP API instead of direct SQLite access.
Implements the same interface as CitationDatabase for drop-in replacement.
"""

from collections import Counter
from typing import Dict, List, Optional, Tuple


class CitationDatabaseHTTP:
    """
    HTTP interface for citation graph operations via crossref-local API.

    Drop-in replacement for CitationDatabase that uses the crossref-local
    HTTP server instead of direct SQLite database access.

    Example:
        >>> db = CitationDatabaseHTTP()  # auto-detects from env/config
        >>> with db:
        ...     refs = db.get_references("10.1038/s41586-020-2008-3")
    """

    def __init__(self, api_url: str = None):
        """
        Initialize HTTP database connection.

        Args:
            api_url: URL of the crossref-local HTTP API server.
                     If None, auto-detects from CROSSREF_LOCAL_API_URL env var
                     or crossref_local config defaults.
        """
        from crossref_local.remote import RemoteClient

        if api_url is None:
            import os

            from crossref_local._core.config import DEFAULT_API_URL

            api_url = os.environ.get("CROSSREF_LOCAL_API_URL", DEFAULT_API_URL)

        self.api_url = api_url
        self.client = RemoteClient(api_url)

    def connect(self, read_only: bool = True):
        """No-op for HTTP mode (connection is stateless)."""

    def close(self):
        """No-op for HTTP mode."""

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""

    def get_references(self, doi: str, limit: int = 100) -> List[str]:
        """
        Get papers cited by this DOI (forward citations / references).

        Args:
            doi: DOI of the paper
            limit: Maximum number of references to return

        Returns
        -------
            List of DOIs cited by the paper
        """
        return self.client.get_cited(doi, limit=limit)

    def get_citations(self, doi: str, limit: int = 100) -> List[Tuple[str, int]]:
        """
        Get papers that cite this DOI (reverse citations).

        Args:
            doi: DOI of the paper
            limit: Maximum number of citations to return

        Returns
        -------
            List of (citing_doi, year) tuples.
            Note: year is 0 since the HTTP API doesn't return year with citing DOIs.
        """
        citing_dois = self.client.get_citing(doi, limit=limit)
        return [(d, 0) for d in citing_dois]

    def get_cocited_papers(self, doi: str, limit: int = 50) -> List[Tuple[str, int]]:
        """
        Find papers co-cited with this DOI.

        Computed client-side: find papers that cite the seed,
        then count how often other papers appear in their reference lists.

        Args:
            doi: DOI of the paper
            limit: Maximum number of results

        Returns
        -------
            List of (cocited_doi, cocitation_count) tuples
        """
        # Get papers that cite this DOI
        citing_dois = self.client.get_citing(doi, limit=50)

        # For each citing paper, get its references and count co-occurrences
        cocitation_counts = Counter()
        for citing_doi in citing_dois[:30]:  # Limit HTTP calls
            refs = self.client.get_cited(citing_doi, limit=100)
            for ref_doi in refs:
                if ref_doi.lower() != doi.lower():
                    cocitation_counts[ref_doi] += 1

        return cocitation_counts.most_common(limit)

    def get_bibliographic_coupled_papers(
        self, doi: str, limit: int = 50
    ) -> List[Tuple[str, int]]:
        """
        Find papers with similar references (bibliographic coupling).

        Computed client-side: get seed's references, then for each reference
        find papers that also cite it, and count shared references.

        Args:
            doi: DOI of the paper
            limit: Maximum number of results

        Returns
        -------
            List of (coupled_doi, shared_references_count) tuples
        """
        # Get seed paper's references
        seed_refs = self.client.get_cited(doi, limit=100)

        # For each reference, find other papers that also cite it
        coupling_counts = Counter()
        for ref_doi in seed_refs[:30]:  # Limit HTTP calls
            citers = self.client.get_citing(ref_doi, limit=100)
            for citer_doi in citers:
                if citer_doi.lower() != doi.lower():
                    coupling_counts[citer_doi] += 1

        return coupling_counts.most_common(limit)

    def get_paper_metadata(self, doi: str) -> Optional[Dict]:
        """
        Get metadata for a paper from crossref-local API.

        Args:
            doi: DOI of the paper

        Returns
        -------
            Dictionary with paper metadata in CrossRef format, or None
        """
        work = self.client.get(doi)
        if work is None:
            return None

        # Convert Work object to CrossRef-style metadata dict
        # that CitationGraphBuilder._create_paper_node expects
        metadata = {
            "title": [work.title] if work.title else ["Unknown"],
            "author": [],
            "container-title": [work.journal] if work.journal else [],
        }

        # Parse authors
        if work.authors:
            for author_str in work.authors:
                parts = author_str.rsplit(" ", 1)
                if len(parts) == 2:
                    metadata["author"].append({"given": parts[0], "family": parts[1]})
                else:
                    metadata["author"].append({"family": author_str, "given": ""})

        # Add year in CrossRef date format
        if work.year:
            metadata["published"] = {"date-parts": [[work.year]]}

        return metadata

    def get_combined_similarity_scores(
        self,
        seed_doi: str,
        weight_coupling: float = 2.0,
        weight_cocitation: float = 2.0,
        weight_direct: float = 1.0,
        max_papers: int = 100,
    ) -> Counter:
        """
        Calculate combined similarity scores using multiple metrics.

        Same algorithm as CitationDatabase but using HTTP API.

        Args:
            seed_doi: DOI of the seed paper
            weight_coupling: Weight for bibliographic coupling score
            weight_cocitation: Weight for co-citation score
            weight_direct: Weight for direct citation score
            max_papers: Maximum papers to consider per metric

        Returns
        -------
            Counter with {doi: combined_score}
        """
        scores = Counter()

        # 1. Bibliographic coupling
        coupled = self.get_bibliographic_coupled_papers(seed_doi, limit=max_papers)
        for doi, count in coupled:
            scores[doi] += count * weight_coupling

        # 2. Co-citation
        cocited = self.get_cocited_papers(seed_doi, limit=max_papers)
        for doi, count in cocited:
            scores[doi] += count * weight_cocitation

        # 3. Direct citations
        refs = self.get_references(seed_doi, limit=50)
        for doi in refs:
            scores[doi] += weight_direct

        citations = self.get_citations(seed_doi, limit=50)
        for doi, _ in citations:
            scores[doi] += weight_direct

        return scores

    def get_combined_similarity_scores_batch(
        self,
        seed_dois: List[str],
        weight_coupling: float = 2.0,
        weight_cocitation: float = 2.0,
        weight_direct: float = 1.0,
    ) -> Counter:
        """
        Batch similarity scores via parallel HTTP requests.

        HTTP API doesn't support batch SQL, so parallelize per-DOI calls
        using ThreadPoolExecutor for acceptable performance.
        """
        from concurrent.futures import ThreadPoolExecutor

        scores = Counter()
        seed_set = set(d.lower() for d in seed_dois)

        def _score_one(doi):
            return self.get_combined_similarity_scores(
                doi,
                weight_coupling=weight_coupling,
                weight_cocitation=weight_cocitation,
                weight_direct=weight_direct,
            )

        max_workers = min(len(seed_dois), 20)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            results = pool.map(_score_one, seed_dois)

        for per_doi_scores in results:
            for doi, score in per_doi_scores.items():
                if doi.lower() not in seed_set:
                    scores[doi] += score

        return scores
