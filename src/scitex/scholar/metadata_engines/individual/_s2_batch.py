#!/usr/bin/env python3
"""Semantic Scholar batch API operations.

Provides batch_resolve() and search_by_paper_id() as a mixin
for SemanticScholarEngine, split out to keep file sizes manageable.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

logger = logging.getLogger(__name__)


class S2BatchMixin:
    """Mixin adding batch and SHA-based lookup to SemanticScholarEngine."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def search_by_paper_id(
        self, paper_id: str, return_as: str = "dict"
    ) -> Optional[Dict]:
        """Lookup by Semantic Scholar 40-char SHA paper ID.

        Parameters
        ----------
        paper_id : str
            S2 paper ID (e.g., "649def34f8be52c8b66281af98ae884c09aef38b").
        return_as : str
            "dict" or "json".

        Returns
        -------
        dict or None
            Standardized metadata dict, or None if not found.
        """
        self._handle_rate_limit()
        url = f"{self.base_url}/paper/{paper_id}"
        params = {"fields": "title,year,authors,externalIds,url,venue,abstract"}

        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 404:
                logger.warning(f"S2 paper ID not found: {paper_id}")
                return None
            if response.status_code == 429:
                raise requests.ConnectionError("Rate limit exceeded")
            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata_from_paper(paper, return_as)
        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warning(f"S2 paper ID lookup error: {exc}")
            return None

    def batch_resolve(
        self,
        ids: List[str],
        fields: str = "externalIds,title,year,authors",
    ) -> List[Optional[Dict]]:
        """Resolve multiple papers via POST /paper/batch.

        Auto-chunks into batches of 500 (S2 API limit).

        Parameters
        ----------
        ids : list of str
            S2 paper IDs, DOIs, corpus IDs, or any S2-accepted identifier.
        fields : str
            Comma-separated fields to retrieve.

        Returns
        -------
        list
            List aligned with input; each element is a paper dict or None.
        """
        if not ids:
            return []

        chunk_size = 500
        all_results: List[Optional[Dict]] = []

        for start in range(0, len(ids), chunk_size):
            chunk = ids[start : start + chunk_size]
            self._handle_rate_limit()

            url = f"{self.base_url}/paper/batch"
            params = {"fields": fields}

            try:
                response = self.session.post(
                    url,
                    params=params,
                    json={"ids": chunk},
                    timeout=60,
                )
                if response.status_code == 429:
                    logger.warning("S2 batch rate limit; retrying after delay")
                    time.sleep(5)
                    response = self.session.post(
                        url,
                        params=params,
                        json={"ids": chunk},
                        timeout=60,
                    )
                response.raise_for_status()
                results = response.json()
                all_results.extend(results)
            except Exception as exc:
                logger.warning(f"S2 batch resolve error: {exc}")
                all_results.extend([None] * len(chunk))

        return all_results


# EOF
