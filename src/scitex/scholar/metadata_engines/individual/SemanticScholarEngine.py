#!/usr/bin/env python3
# Timestamp: "2025-08-22 00:00:02 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/individual/SemanticScholarEngine.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import time
from typing import Dict, List, Optional, Union

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import standardize_metadata
from ._BaseDOIEngine import BaseDOIEngine
from ._s2_batch import S2BatchMixin

logger = logging.getLogger(__name__)


class SemanticScholarEngine(S2BatchMixin, BaseDOIEngine):
    """Combined Semantic Scholar engine with enhanced features."""

    def __init__(self, email: str = "research@example.com", api_key: str = None):
        super().__init__(email)
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self._rate_limit_delay = 0.5 if self.api_key else 1.2

    def _get_user_agent(self) -> str:
        return f"SciTeX/1.0 (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "Semantic_Scholar"

    @property
    def rate_limit_delay(self) -> float:
        return self._rate_limit_delay

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            headers = {
                "User-Agent": self._get_user_agent(),
                "Accept": "application/json",
            }
            if self.api_key:
                headers["x-api-key"] = self.api_key
            self._session.headers.update(headers)
        return self._session

    def _handle_rate_limit(self):
        """Handle rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        doi: Optional[str] = None,
        corpus_id: Optional[str] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict]:
        """When doi or corpus_id is provided, all other information is ignored"""
        if doi:
            return self._search_by_doi(doi, return_as)
        elif corpus_id:
            return self._search_by_corpus_id(corpus_id, return_as)
        else:
            return self._search_by_metadata(
                title, year, authors, max_results, return_as
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_doi(self, doi: str, return_as: str) -> Optional[Dict]:
        """Search by DOI directly"""
        self._handle_rate_limit()

        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        url = f"{self.base_url}/paper/{doi}"
        params = {"fields": "title,year,authors,externalIds,url,venue,abstract"}

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata_from_paper(paper, return_as)
        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warning(f"Semantic Scholar DOI search error: {exc}")
            return self._create_minimal_metadata(
                doi=doi,
                return_as=return_as,
            )

            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_metadata(
        self,
        title: str,
        year: Optional[Union[int, str]] = None,
        authors: Optional[List[str]] = None,
        max_results: int = 1,
        return_as: str = "dict",
    ) -> Optional[Dict]:
        """Search by metadata other than doi"""
        if not title:
            return None

        self._handle_rate_limit()
        url = f"{self.base_url}/paper/search"

        # Clean title to remove meta characters that might interfere with search
        cleaned_title = self._clean_query(title)

        params = {
            "query": cleaned_title,
            "fields": "title,year,authors,externalIds,url,venue,abstract",
            "limit": 10,
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                raise requests.ConnectionError("Rate limit exceeded")
            response.raise_for_status()

            data = response.json()
            papers = data.get("data", [])

            for paper in papers:
                paper_title = paper.get("title", "")
                paper_year = paper.get("year")
                paper_authors = [
                    author.get("name", "") for author in paper.get("authors", [])
                ]

                # Check title match
                if not self._is_title_match(title, paper_title):
                    continue

                # Check year match if provided
                if year and paper_year and int(year) != int(paper_year):
                    continue

                # Check author match if provided
                if authors and paper_authors:
                    # Check if any provided author appears in paper authors
                    author_match = any(
                        any(
                            provided_author.lower() in paper_author.lower()
                            for paper_author in paper_authors
                        )
                        for provided_author in authors
                    )
                    if not author_match:
                        continue

                return self._extract_metadata_from_paper(paper, return_as)

            return None

        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warning(f"Semantic Scholar metadata error: {exc}")
            return self._create_minimal_metadata(
                title=title,
                year=year,
                authors=authors,
                return_as=return_as,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        retry=retry_if_exception_type((requests.ConnectionError,)),
    )
    def _search_by_corpus_id(self, corpus_id: str, return_as: str) -> Optional[Dict]:
        """Search by Corpus ID directly"""
        if not corpus_id.isdigit():
            corpus_id = corpus_id.replace("CorpusId:", "")

        self._handle_rate_limit()

        url = f"{self.base_url}/paper/CorpusId:{corpus_id}"
        params = {"fields": "title,year,authors,externalIds,url,venue,abstract"}

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                raise requests.ConnectionError("Rate limit exceeded")

            if response.status_code == 404:
                logger.warning(f"Semantic Scholar Corpus ID not found: {corpus_id}")
                return None

            response.raise_for_status()
            paper = response.json()
            return self._extract_metadata_from_paper(paper, return_as)
        except requests.ConnectionError:
            raise
        except Exception as exc:
            logger.warning(f"Semantic Scholar Corpus ID search error: {exc}")
            return self._create_minimal_metadata(
                corpus_id=corpus_id,
                return_as=return_as,
            )

            return None

    def _extract_metadata_from_paper(
        self, paper: dict, return_as: str
    ) -> Optional[Dict]:
        """Extract metadata from Semantic Scholar paper"""
        paper_title = paper.get("title", "")
        paper_year = paper.get("year")
        extracted_authors = []
        for author in paper.get("authors", []):
            if author.get("name"):
                extracted_authors.append(author["name"])

        external_ids = paper.get("externalIds", {})
        doi = external_ids.get("DOI")
        corpus_id = external_ids.get("CorpusId")
        arxiv_id = external_ids.get("ArXiv")
        pmid = external_ids.get("PubMed")

        metadata = {
            "id": {
                "doi": doi,
                "doi_engines": [self.name] if doi else None,
                "corpus_id": corpus_id,
                "corpus_id_engines": [self.name] if corpus_id else None,
                "arxiv_id": arxiv_id,
                "arxiv_id_engines": [self.name] if arxiv_id else None,
                "pmid": pmid,
                "pmid_engines": [self.name] if pmid else None,
            },
            "basic": {
                "title": paper_title if paper_title else None,
                "title_engines": [self.name] if paper_title else None,
                "year": paper_year if paper_year else None,
                "year_engines": [self.name] if paper_year else None,
                "abstract": (paper.get("abstract") if paper.get("abstract") else None),
                "abstract_engines": ([self.name] if paper.get("abstract") else None),
                "authors": extracted_authors if extracted_authors else None,
                "authors_engines": [self.name] if extracted_authors else None,
            },
            "publication": {
                "journal": paper.get("venue") if paper.get("venue") else None,
                "journal_engines": [self.name] if paper.get("venue") else None,
            },
            "url": {
                "doi": f"https://doi.org/{doi}" if doi else None,
                "doi_engines": [self.name] if doi else None,
                "publisher": paper.get("url") if paper.get("url") else None,
                "publisher_engines": [self.name] if paper.get("url") else None,
                "arxiv": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
                "arxiv_engines": [self.name] if arxiv_id else None,
                "corpus_id": (
                    f"https://www.semanticscholar.org/paper/{corpus_id}"
                    if corpus_id
                    else None
                ),
                "corpus_id_engines": [self.name] if corpus_id else None,
            },
            "system": {
                f"searched_by_{self.name}": True,
            },
        }

        metadata = standardize_metadata(metadata)

        if return_as == "dict":
            return metadata
        if return_as == "json":
            return json.dumps(metadata, indent=2)

    def _clean_doi(self, doi: str) -> str:
        return doi.strip() if doi else doi

    async def convert_corpus_id_to_doi_async(
        self, corpus_id: str, page
    ) -> Optional[str]:
        """Convert Semantic Scholar Corpus ID to DOI by navigating to page and extracting.

        Args:
            corpus_id: Corpus ID (e.g., "262046731" or "CorpusId:262046731")
            page: Playwright Page object for navigation

        Returns
        -------
            DOI string if found, None otherwise
        """
        if not corpus_id:
            return None

        # Clean corpus_id (remove CorpusId: prefix if present)
        if not corpus_id.isdigit():
            corpus_id = corpus_id.replace("CorpusId:", "")

        # Create Semantic Scholar URL
        url = f"https://www.semanticscholar.org/paper/{corpus_id}"
        logger.info(f"Navigating to Semantic Scholar page: {url}")

        try:
            # Navigate to the page
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for content to load

            # Try to extract DOI from page content
            # Method 1: Look for DOI in meta tags
            doi_meta = await page.query_selector('meta[name="citation_doi"]')
            if doi_meta:
                doi = await doi_meta.get_attribute("content")
                if doi:
                    logger.info(
                        f"Found DOI in meta tag for Corpus ID {corpus_id}: {doi}"
                    )
                    return doi

            # Method 2: Look for DOI link in page
            doi_link = await page.query_selector('a[href*="doi.org"]')
            if doi_link:
                href = await doi_link.get_attribute("href")
                if href and "doi.org/" in href:
                    doi = href.split("doi.org/")[-1].split("?")[0].split("#")[0]
                    logger.info(f"Found DOI in link for Corpus ID {corpus_id}: {doi}")
                    return doi

            # Method 3: Search for DOI pattern in page text
            content = await page.content()
            import re

            doi_pattern = r"10\.\d{4,}/[-._;()/:\w]+"
            matches = re.findall(doi_pattern, content)
            if matches:
                doi = matches[0]  # Take first match
                logger.info(
                    f"Found DOI pattern in content for Corpus ID {corpus_id}: {doi}"
                )
                return doi

            logger.warning(
                f"No DOI found on Semantic Scholar page for Corpus ID {corpus_id}"
            )
            return None

        except Exception as e:
            logger.error(f"Error extracting DOI from Corpus ID {corpus_id}: {e}")
            return None

    # Note: _clean_query() is inherited from BaseDOIEngine


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Attention is All You Need"
    DOI = "10.1126/science.aao0702"
    CORPUS_ID = "276988304"

    engine = SemanticScholarEngine("test@example.com")
    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = engine.search(title=TITLE)
    outputs["metadata_by_title_json"] = engine.search(title=TITLE, return_as="json")

    # Emptry Result
    outputs["empty_dict"] = engine._create_minimal_metadata(return_as="dict")
    outputs["empty_json"] = engine._create_minimal_metadata(return_as="json")

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)


# python -m scitex.scholar.engines.individual.SemanticScholarEngine

# EOF
