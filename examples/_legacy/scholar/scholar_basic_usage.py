#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:45:00 (ywatanabe)"
# File: ./examples/scholar_basic_usage.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scholar_basic_usage.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Basic usage of the new Scholar API
  - Search, filter, and save papers
  - Show simple workflows

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex

Input:
  - None (hardcoded examples)

Output:
  - ./basic_search.bib
  - ./filtered_papers.json
"""

"""Imports"""
import scitex as stx
from scitex.scholar import Scholar, Paper, PaperCollection

"""Functions & Classes"""
def main():
    """Demonstrate basic Scholar usage."""

    # Example 1: Simple search
    stx.str.printc("\n=== Example 1: Simple Search ===", c="blue")

    scholar = Scholar()
    papers = scholar.search("deep learning", limit=10)

    print(f"Found {len(papers)} papers")

    # Show first 3 papers
    for i, paper in enumerate(papers[:3], 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
        print(f"   Year: {paper.year}, Citations: {paper.citation_count}")
        if paper.impact_factor:
            print(f"   Impact Factor: {paper.impact_factor:.2f}")

    # Save as BibTeX
    papers.save("./basic_search.bib")
    print("\nSaved to basic_search.bib")

    # Example 2: Filtering
    stx.str.printc("\n=== Example 2: Filtering Papers ===", c="blue")

    # Filter by year and citations
    recent_high_impact = papers.filter(
        year_min=2020,
        min_citations=50
    )

    print(f"Papers from 2020+ with 50+ citations: {len(recent_high_impact)}")

    # Example 3: Sorting
    stx.str.printc("\n=== Example 3: Sorting Papers ===", c="blue")

    # Sort by impact factor
    sorted_papers = papers.sort_by("impact_factor", reverse=True)

    print("Top 3 papers by impact factor:")
    for i, paper in enumerate(sorted_papers[:3], 1):
        if_str = f"{paper.impact_factor:.2f}" if paper.impact_factor else "N/A"
        print(f"{i}. {paper.journal} (IF: {if_str}) - {paper.title[:60]}...")

    # Example 4: Method chaining
    stx.str.printc("\n=== Example 4: Method Chaining ===", c="blue")

    # Chain operations together
    result = scholar.search("machine learning", limit=50) \
                   .filter(year_min=2022) \
                   .sort_by("citations") \
                   .deduplicate()

    print(f"Chained result: {len(result)} papers")

    # Save in different format
    result.save("./filtered_papers.json", format="json")
    print("Saved to filtered_papers.json")

    # Example 5: Quick search (just titles)
    stx.str.printc("\n=== Example 5: Quick Search ===", c="blue")

    from scitex.scholar import _search_quick

    titles = _search_quick("neural networks", top_n=5)
    print("\nQuick search results:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")

    # Example 6: Paper analysis
    stx.str.printc("\n=== Example 6: Collection Analysis ===", c="blue")

    trends = papers.analyze_trends()

    print(f"\nCollection statistics:")
    print(f"- Total papers: {trends['total_papers']}")
    if trends['date_range']:
        print(f"- Year range: {trends['date_range']['start']}-{trends['date_range']['end']}")
    if trends['citation_statistics']:
        print(f"- Avg citations: {trends['citation_statistics']['mean']:.1f}")
    print(f"- Open access rate: {trends['open_access_rate']:.1f}%")

    # Show summary
    print("\n" + papers.summary())

    return 0


if __name__ == "__main__":
    main()

# EOF
