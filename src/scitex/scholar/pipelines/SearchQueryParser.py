#!/usr/bin/env python3
# File: ./src/scitex/scholar/pipelines/SearchQueryParser.py

"""
SearchQueryParser - Parse advanced search queries with filters

Supports:
  - Positive keywords: "hippocampus sharp wave"
  - Negative keywords: "-seizure -epilepsy"
  - Year range: "year:2020-2024" or "year:>2020"
  - Impact factor: "impact_factor:>5"
  - Open access: "open_access:true"
  - Citation count: "citations:>100"

Example:
  query = "hippocampus sharp wave -seizure year:2020-2024 impact_factor:>5 open_access:true"
  parser = SearchQueryParser(query)

  filters = parser.get_filters()
  # {
  #   'positive_keywords': ['hippocampus', 'sharp', 'wave'],
  #   'negative_keywords': ['seizure'],
  #   'year_start': 2020,
  #   'year_end': 2024,
  #   'min_impact_factor': 5,
  #   'open_access': True
  # }
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class SearchQueryParser:
    """Parse advanced search queries with filters."""

    def __init__(self, query: str):
        """Initialize parser with query string.

        Args:
            query: Search query with optional filters
        """
        self.original_query = query
        self.positive_keywords: List[str] = []
        self.negative_keywords: List[str] = []
        self.year_start: Optional[int] = None
        self.year_end: Optional[int] = None
        self.min_impact_factor: Optional[float] = None
        self.max_impact_factor: Optional[float] = None
        self.min_citations: Optional[int] = None
        self.max_citations: Optional[int] = None
        self.open_access: Optional[bool] = None
        self.document_type: Optional[str] = None
        self.title_includes: List[str] = []
        self.title_excludes: List[str] = []
        self.author_includes: List[str] = []
        self.author_excludes: List[str] = []
        self.journal_includes: List[str] = []
        self.journal_excludes: List[str] = []

        self._parse()

    def _parse(self):
        """Parse the query string."""
        remaining_text = self.original_query

        # Extract year filter: year:2020-2024 or year:>2020 or year:<2024
        year_pattern = r"year:(\d{4})-(\d{4})|year:([><])(\d{4})"
        year_matches = re.findall(year_pattern, remaining_text)
        for match in year_matches:
            if match[0] and match[1]:  # Range format: 2020-2024
                self.year_start = int(match[0])
                self.year_end = int(match[1])
            elif match[2] and match[3]:  # Comparison format: >2020
                year = int(match[3])
                if match[2] == ">":
                    self.year_start = year
                else:  # <
                    self.year_end = year
        remaining_text = re.sub(year_pattern, "", remaining_text)

        # Extract impact factor filter: impact_factor:>5 or if:>5
        if_pattern = r"(?:impact_factor|if):([><])?([\d.]+)"
        if_matches = re.findall(if_pattern, remaining_text)
        for match in if_matches:
            value = float(match[1])
            if match[0] == ">":
                self.min_impact_factor = value
            elif match[0] == "<":
                self.max_impact_factor = value
            else:
                self.min_impact_factor = value
        remaining_text = re.sub(if_pattern, "", remaining_text)

        # Extract citation count filter: citations:>100
        cit_pattern = r"citations?:([><])?([\d]+)"
        cit_matches = re.findall(cit_pattern, remaining_text)
        for match in cit_matches:
            value = int(match[1])
            if match[0] == ">":
                self.min_citations = value
            elif match[0] == "<":
                self.max_citations = value
            else:
                self.min_citations = value
        remaining_text = re.sub(cit_pattern, "", remaining_text)

        # Extract open access filter: open_access:true or oa:true
        oa_pattern = r"(?:open_access|oa):(true|false|yes|no|1|0)"
        oa_match = re.search(oa_pattern, remaining_text, re.IGNORECASE)
        if oa_match:
            oa_value = oa_match.group(1).lower()
            self.open_access = oa_value in ["true", "yes", "1"]
        remaining_text = re.sub(oa_pattern, "", remaining_text, flags=re.IGNORECASE)

        # Extract document type filter: type:article or type:review
        type_pattern = r"type:(article|review|conference|book)"
        type_match = re.search(type_pattern, remaining_text, re.IGNORECASE)
        if type_match:
            self.document_type = type_match.group(1).lower()
        remaining_text = re.sub(type_pattern, "", remaining_text, flags=re.IGNORECASE)

        # Extract negative keywords (words starting with -)
        neg_pattern = r"-(\w+)"
        neg_matches = re.findall(neg_pattern, remaining_text)
        self.negative_keywords = neg_matches
        remaining_text = re.sub(neg_pattern, "", remaining_text)

        # Extract quoted phrases as single keywords
        quoted_pattern = r'"([^"]+)"'
        quoted_matches = re.findall(quoted_pattern, remaining_text)
        self.positive_keywords.extend(quoted_matches)
        remaining_text = re.sub(quoted_pattern, "", remaining_text)

        # Remaining words are positive keywords
        words = remaining_text.split()
        words = [w.strip() for w in words if w.strip()]
        self.positive_keywords.extend(words)

    def get_keyword_query(self) -> str:
        """Get cleaned keyword query (positive keywords only)."""
        return " ".join(self.positive_keywords)

    def get_filters(self) -> Dict[str, Any]:
        """Get all filters as dictionary."""
        filters = {}

        if self.positive_keywords:
            filters["positive_keywords"] = self.positive_keywords
        if self.negative_keywords:
            filters["negative_keywords"] = self.negative_keywords
        if self.year_start is not None:
            filters["year_start"] = self.year_start
        if self.year_end is not None:
            filters["year_end"] = self.year_end
        if self.min_impact_factor is not None:
            filters["min_impact_factor"] = self.min_impact_factor
        if self.max_impact_factor is not None:
            filters["max_impact_factor"] = self.max_impact_factor
        if self.min_citations is not None:
            filters["min_citations"] = self.min_citations
        if self.max_citations is not None:
            filters["max_citations"] = self.max_citations
        if self.open_access is not None:
            filters["open_access"] = self.open_access
        if self.document_type is not None:
            filters["document_type"] = self.document_type
        if self.title_includes:
            filters["title_includes"] = self.title_includes
        if self.title_excludes:
            filters["title_excludes"] = self.title_excludes
        if self.author_includes:
            filters["author_includes"] = self.author_includes
        if self.author_excludes:
            filters["author_excludes"] = self.author_excludes
        if self.journal_includes:
            filters["journal_includes"] = self.journal_includes
        if self.journal_excludes:
            filters["journal_excludes"] = self.journal_excludes

        return filters

    @classmethod
    def from_shell_syntax(cls, query: str) -> "SearchQueryParser":
        """Parse shell-style operators from a query string.

        Supports the following shell-style operators:
          -t VALUE or --title VALUE : Title include filter
          -t -VALUE                 : Title exclude filter (- prefix on value)
          -a VALUE or --author VALUE: Author include filter
          -a -VALUE                 : Author exclude filter
          -j VALUE or --journal VALUE: Journal include filter
          -j -VALUE                 : Journal exclude filter
          -ymin YYYY or --year-min YYYY: Minimum year
          -ymax YYYY or --year-max YYYY: Maximum year
          -cmin N or --citations-min N : Minimum citations
          -cmax N or --citations-max N : Maximum citations
          -ifmin N or --if-min N   : Minimum impact factor
          -ifmax N or --if-max N   : Maximum impact factor

        Args:
            query: Query string with shell-style operators

        Returns
        -------
            SearchQueryParser instance with parsed fields set

        Example:
            parser = SearchQueryParser.from_shell_syntax(
                "hippocampus -t theta -a -Smith -ymin 2020 -cmin 50"
            )
        """
        # Create instance without running the standard _parse() on the raw query.
        # We do this by initialising with an empty string and then setting
        # original_query and the parsed fields manually.
        instance = cls.__new__(cls)
        instance.original_query = query
        instance.positive_keywords = []
        instance.negative_keywords = []
        instance.year_start = None
        instance.year_end = None
        instance.min_impact_factor = None
        instance.max_impact_factor = None
        instance.min_citations = None
        instance.max_citations = None
        instance.open_access = None
        instance.document_type = None
        instance.title_includes = []
        instance.title_excludes = []
        instance.author_includes = []
        instance.author_excludes = []
        instance.journal_includes = []
        instance.journal_excludes = []

        if not query:
            return instance

        remaining = query

        # Text filters: -t/-a/-j  (value may be prefixed with - for exclude)
        text_patterns = [
            (r'(?:-t|--title)\s+(-?)([^\s]+|"[^"]+"|\'[^\']+\')', "title"),
            (r'(?:-a|--author)\s+(-?)([^\s]+|"[^"]+"|\'[^\']+\')', "author"),
            (r'(?:-j|--journal)\s+(-?)([^\s]+|"[^"]+"|\'[^\']+\')', "journal"),
        ]

        for pattern, field_name in text_patterns:
            for match in re.finditer(pattern, remaining, re.IGNORECASE):
                is_exclude = match.group(1) == "-"
                value = match.group(2).strip("\"'")
                if is_exclude:
                    getattr(instance, f"{field_name}_excludes").append(value)
                else:
                    getattr(instance, f"{field_name}_includes").append(value)
            remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE)

        # Numeric filters
        numeric_patterns = [
            (r"(?:-ymin|--year-min)\s+(\d{4})", "year_min"),
            (r"(?:-ymax|--year-max)\s+(\d{4})", "year_max"),
            (r"(?:-cmin|--citations-min)\s+(\d+)", "citations_min"),
            (r"(?:-cmax|--citations-max)\s+(\d+)", "citations_max"),
            (r"(?:-ifmin|--if-min)\s+(\d+(?:\.\d+)?)", "impact_factor_min"),
            (r"(?:-ifmax|--if-max)\s+(\d+(?:\.\d+)?)", "impact_factor_max"),
        ]

        field_mapping = {
            "year_min": "year_start",
            "year_max": "year_end",
            "citations_min": "min_citations",
            "citations_max": "max_citations",
            "impact_factor_min": "min_impact_factor",
            "impact_factor_max": "max_impact_factor",
        }

        for pattern, field_name in numeric_patterns:
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                raw_value = match.group(1)
                if "impact_factor" in field_name:
                    value = float(raw_value)
                elif "year" in field_name:
                    value = int(raw_value)
                else:
                    value = int(raw_value)
                attr_name = field_mapping[field_name]
                setattr(instance, attr_name, value)
                remaining = re.sub(pattern, "", remaining, flags=re.IGNORECASE)

        # Remaining text becomes positive keywords
        words = remaining.split()
        instance.positive_keywords = [w.strip() for w in words if w.strip()]

        return instance

    def get_api_filters(self) -> Dict[str, Any]:
        """Get filters that can be pushed to API level."""
        api_filters = {}

        if self.year_start is not None:
            api_filters["year_start"] = self.year_start
        if self.year_end is not None:
            api_filters["year_end"] = self.year_end
        if self.open_access is not None:
            api_filters["open_access"] = self.open_access
        if self.document_type is not None:
            api_filters["document_type"] = self.document_type

        return api_filters

    def get_post_filters(self) -> Dict[str, Any]:
        """Get filters that must be applied post-API (client-side)."""
        post_filters = {}

        if self.negative_keywords:
            post_filters["negative_keywords"] = self.negative_keywords
        if self.min_impact_factor is not None:
            post_filters["min_impact_factor"] = self.min_impact_factor
        if self.max_impact_factor is not None:
            post_filters["max_impact_factor"] = self.max_impact_factor
        if self.min_citations is not None:
            post_filters["min_citations"] = self.min_citations
        if self.max_citations is not None:
            post_filters["max_citations"] = self.max_citations

        return post_filters

    def to_pubmed_query(self) -> str:
        """Convert to PubMed E-utilities query format."""
        parts = []

        # Positive keywords
        if self.positive_keywords:
            keyword_part = " ".join(self.positive_keywords)
            parts.append(f"({keyword_part})[Title/Abstract]")

        # Negative keywords
        for neg in self.negative_keywords:
            parts.append(f"NOT {neg}[Title/Abstract]")

        # Year range
        if self.year_start and self.year_end:
            parts.append(f"{self.year_start}:{self.year_end}[pdat]")
        elif self.year_start:
            current_year = datetime.now().year
            parts.append(f"{self.year_start}:{current_year}[pdat]")
        elif self.year_end:
            parts.append(f"1900:{self.year_end}[pdat]")

        return " AND ".join(parts) if parts else ""

    def to_crossref_params(self) -> Dict[str, Any]:
        """Convert to CrossRef API parameters."""
        params = {}

        # Query
        if self.positive_keywords:
            params["query.bibliographic"] = " ".join(self.positive_keywords)

        # Year filter
        if self.year_start:
            params["filter"] = f"from-pub-date:{self.year_start}"
        if self.year_end:
            if "filter" in params:
                params["filter"] += f",until-pub-date:{self.year_end}"
            else:
                params["filter"] = f"until-pub-date:{self.year_end}"

        return params

    def to_arxiv_query(self) -> str:
        """Convert to arXiv API query format."""
        parts = []

        # Positive keywords
        for kw in self.positive_keywords:
            if " " in kw:  # Quoted phrase
                parts.append(f'all:"{kw}"')
            else:
                parts.append(f"all:{kw}")

        # Negative keywords
        for neg in self.negative_keywords:
            parts.append(f"ANDNOT all:{neg}")

        return " AND ".join(parts) if parts else ""

    def __repr__(self) -> str:
        return (
            f"SearchQueryParser("
            f"positive={self.positive_keywords}, "
            f"negative={self.negative_keywords}, "
            f"year={self.year_start}-{self.year_end}, "
            f"if>={self.min_impact_factor}, "
            f"oa={self.open_access})"
        )


# EOF
