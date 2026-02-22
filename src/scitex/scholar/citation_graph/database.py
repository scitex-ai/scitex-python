"""
Database access layer for citation graph queries.

Handles all SQL queries to the CrossRef SQLite database with
optimized queries and connection management.
"""

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CitationDatabase:
    """
    Database interface for citation graph operations.

    Provides optimized queries for:
    - Citation extraction (forward/reverse)
    - Co-citation analysis
    - Bibliographic coupling
    - Paper metadata lookup
    """

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to CrossRef SQLite database
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.conn = None

    def connect(self, read_only: bool = True):
        """
        Connect to database.

        Args:
            read_only: If True, open in read-only mode (default)
        """
        if read_only:
            self.conn = sqlite3.connect(
                f"file:{self.db_path}?mode=ro",
                uri=True,
                check_same_thread=False,  # Allow multi-threaded access (e.g., Django)
            )
        else:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def get_references(self, doi: str, limit: int = 100) -> List[str]:
        """
        Get papers cited by this DOI (forward citations).

        Args:
            doi: DOI of the paper
            limit: Maximum number of references to return

        Returns
        -------
            List of DOIs cited by the paper
        """
        cursor = self.conn.execute(
            """
            SELECT cited_doi
            FROM citations
            WHERE citing_doi = ?
            LIMIT ?
            """,
            (doi.lower(), limit),
        )
        return [row[0] for row in cursor]

    def get_citations(self, doi: str, limit: int = 100) -> List[Tuple[str, int]]:
        """
        Get papers that cite this DOI (reverse citations).

        Args:
            doi: DOI of the paper
            limit: Maximum number of citations to return

        Returns
        -------
            List of (citing_doi, year) tuples
        """
        cursor = self.conn.execute(
            """
            SELECT citing_doi, citing_year
            FROM citations
            WHERE cited_doi = ?
            ORDER BY citing_year DESC
            LIMIT ?
            """,
            (doi.lower(), limit),
        )
        return [(row[0], row[1]) for row in cursor]

    def get_cocited_papers(self, doi: str, limit: int = 50) -> List[Tuple[str, int]]:
        """
        Find papers co-cited with this DOI.

        Papers are co-cited if they appear together in reference lists.

        Args:
            doi: DOI of the paper
            limit: Maximum number of results

        Returns
        -------
            List of (cocited_doi, cocitation_count) tuples
        """
        cursor = self.conn.execute(
            """
            SELECT c2.cited_doi, COUNT(*) as cocitation_count
            FROM citations c1
            JOIN citations c2 ON c1.citing_doi = c2.citing_doi
            WHERE c1.cited_doi = ?
              AND c2.cited_doi != ?
            GROUP BY c2.cited_doi
            ORDER BY cocitation_count DESC
            LIMIT ?
            """,
            (doi.lower(), doi.lower(), limit),
        )
        return [(row[0], row[1]) for row in cursor]

    def get_bibliographic_coupled_papers(
        self, doi: str, limit: int = 50
    ) -> List[Tuple[str, int]]:
        """
        Find papers with similar references (bibliographic coupling).

        Papers are bibliographically coupled if they cite the same references.

        Args:
            doi: DOI of the paper
            limit: Maximum number of results

        Returns
        -------
            List of (coupled_doi, shared_references_count) tuples
        """
        cursor = self.conn.execute(
            """
            SELECT c2.citing_doi, COUNT(*) as shared_refs
            FROM citations c1
            JOIN citations c2 ON c1.cited_doi = c2.cited_doi
            WHERE c1.citing_doi = ?
              AND c2.citing_doi != ?
            GROUP BY c2.citing_doi
            ORDER BY shared_refs DESC
            LIMIT ?
            """,
            (doi.lower(), doi.lower(), limit),
        )
        return [(row[0], row[1]) for row in cursor]

    def get_paper_metadata(self, doi: str) -> Optional[Dict]:
        """
        Get metadata for a paper from works table.

        Args:
            doi: DOI of the paper

        Returns
        -------
            Dictionary with paper metadata, or None if not found
        """
        cursor = self.conn.execute("SELECT metadata FROM works WHERE doi = ?", (doi,))
        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

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

        Combines:
        - Bibliographic coupling (shared references)
        - Co-citation (cited together)
        - Direct citations (cites or is cited by)

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
        Calculate combined similarity scores for multiple seed DOIs in batch.

        Uses batch SQL (WHERE IN) instead of per-DOI loops — O(4) queries
        instead of O(4*N), critical for large DOI sets (100-1000+).

        Args:
            seed_dois: List of seed DOIs
            weight_coupling: Weight for bibliographic coupling score
            weight_cocitation: Weight for co-citation score
            weight_direct: Weight for direct citation score

        Returns
        -------
            Counter with {doi: combined_score} across all seeds
        """
        scores = Counter()
        lower_dois = [d.lower() for d in seed_dois]
        placeholders = ",".join("?" * len(lower_dois))

        # 1. Bibliographic coupling (batch)
        cursor = self.conn.execute(
            f"""
            SELECT c2.citing_doi, COUNT(*) as shared_refs
            FROM citations c1
            JOIN citations c2 ON c1.cited_doi = c2.cited_doi
            WHERE c1.citing_doi IN ({placeholders})
              AND c2.citing_doi NOT IN ({placeholders})
            GROUP BY c2.citing_doi
            ORDER BY shared_refs DESC
            """,
            lower_dois + lower_dois,
        )
        for row in cursor:
            scores[row[0]] += row[1] * weight_coupling

        # 2. Co-citation (batch)
        cursor = self.conn.execute(
            f"""
            SELECT c2.cited_doi, COUNT(*) as cocitation_count
            FROM citations c1
            JOIN citations c2 ON c1.citing_doi = c2.citing_doi
            WHERE c1.cited_doi IN ({placeholders})
              AND c2.cited_doi NOT IN ({placeholders})
            GROUP BY c2.cited_doi
            ORDER BY cocitation_count DESC
            """,
            lower_dois + lower_dois,
        )
        for row in cursor:
            scores[row[0]] += row[1] * weight_cocitation

        # 3. Direct citations — references (batch)
        cursor = self.conn.execute(
            f"""
            SELECT cited_doi
            FROM citations
            WHERE citing_doi IN ({placeholders})
              AND cited_doi NOT IN ({placeholders})
            """,
            lower_dois + lower_dois,
        )
        for row in cursor:
            scores[row[0]] += weight_direct

        # 4. Direct citations — cited by (batch)
        cursor = self.conn.execute(
            f"""
            SELECT citing_doi
            FROM citations
            WHERE cited_doi IN ({placeholders})
              AND citing_doi NOT IN ({placeholders})
            """,
            lower_dois + lower_dois,
        )
        for row in cursor:
            scores[row[0]] += weight_direct

        return scores
