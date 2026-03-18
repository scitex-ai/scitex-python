#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:47:00 (ywatanabe)"
# File: ./examples/scholar_advanced_usage.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scholar_advanced_usage.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Advanced usage of Scholar API
  - Local PDF library management
  - Custom paper enrichment
  - Multiple source searching
  - Format conversions

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex
    - pandas

Input:
  - Optional: Local PDF directory

Output:
  - ./literature_review.bib
  - ./papers_by_year.md
  - ./custom_analysis.csv
"""

"""Imports"""
import scitex as stx
from scitex.scholar import Scholar, Paper, PaperCollection
from scitex.scholar import papers_to_markdown, papers_to_ris
import pandas as pd
from pathlib import Path

"""Functions & Classes"""
def example_local_library():
    """Example: Managing local PDF library."""
    stx.str.printc("\n=== Local PDF Library Management ===", c="blue")

    scholar = Scholar()

    # Check if we have a PDF directory
    pdf_dir = Path("./my_papers")
    if pdf_dir.exists():
        # Index local PDFs
        stats = scholar._index_local_pdfs(pdf_dir, recursive=True)
        print(f"Indexed {stats['indexed']} PDFs")

        # Search within local library
        local_results = scholar.search_local("transformer", limit=10)
        print(f"Found {len(local_results)} local papers about transformers")

        for paper in local_results[:3]:
            print(f"- {paper.title}")
            print(f"  Path: {paper.pdf_path}")
    else:
        print(f"Create {pdf_dir} directory with PDFs to test local search")


def example_multi_source_search():
    """Example: Search across multiple sources."""
    stx.str.printc("\n=== Multi-Source Search ===", c="blue")

    scholar = Scholar()

    # Search specific sources
    semantic_papers = scholar.search(
        "deep learning healthcare",
        sources=['semantic_scholar'],
        limit=10
    )
    print(f"Semantic Scholar: {len(semantic_papers)} papers")

    arxiv_papers = scholar.search(
        "deep learning healthcare",
        sources=['arxiv'],
        limit=10
    )
    print(f"arXiv: {len(arxiv_papers)} papers")

    # Search all sources
    all_papers = scholar.search(
        "deep learning healthcare",
        sources=['semantic_scholar', 'pubmed', 'arxiv'],
        limit=30
    )
    print(f"All sources: {len(all_papers)} papers")

    # Analyze source distribution
    trends = all_papers.analyze_trends()
    if 'source_distribution' in trends:
        print("\nPapers by source:")
        for source, count in trends['source_distribution'].items():
            print(f"  - {source}: {count}")


def example_custom_enrichment():
    """Example: Custom paper enrichment."""
    stx.str.printc("\n=== Custom Paper Enrichment ===", c="blue")

    # Create papers manually
    papers = [
        Paper(
            title="Deep Learning in Medical Imaging",
            authors=["Smith, J.", "Doe, A."],
            abstract="A comprehensive review of deep learning applications...",
            source="manual",
            year=2023,
            journal="Nature Medicine"
        ),
        Paper(
            title="Transformer Models for Healthcare",
            authors=["Johnson, B.", "Lee, C."],
            abstract="We present a novel transformer architecture...",
            source="manual",
            year=2024,
            journal="Nature"
        )
    ]

    # Create collection
    collection = PaperCollection(papers)

    # Enrich with journal metrics
    scholar = Scholar()
    enriched = scholar._enrich_papers(collection)

    print("Enrichment results:")
    for paper in enriched:
        print(f"\n- {paper.title}")
        print(f"  Journal: {paper.journal}")
        if paper.impact_factor:
            print(f"  Impact Factor: {paper.impact_factor}")
            print(f"  Quartile: {paper.journal_quartile}")


def example_literature_review():
    """Example: Conduct literature review."""
    stx.str.printc("\n=== Literature Review Workflow ===", c="blue")

    scholar = Scholar()

    # Search multiple related topics
    topics = [
        "transformer architecture",
        "attention mechanism",
        "self-attention"
    ]

    # Collect papers from all topics
    all_papers = []
    for topic in topics:
        papers = scholar.search(topic, limit=20)
        all_papers.extend(papers.papers)
        print(f"Found {len(papers)} papers for '{topic}'")

    # Create collection and deduplicate
    collection = PaperCollection(all_papers)
    print(f"\nTotal papers before deduplication: {len(collection)}")

    collection = collection.deduplicate(threshold=0.85)
    print(f"After deduplication: {len(collection)}")

    # Filter to recent, high-quality papers
    filtered = collection.filter(
        year_min=2020,
        min_citations=10
    ).sort_by("impact_factor")

    print(f"After filtering (2020+, 10+ citations): {len(filtered)}")

    # Save bibliography
    filtered.save("./literature_review.bib")
    print("\nSaved bibliography to literature_review.bib")

    # Create markdown summary grouped by year
    md_content = papers_to_markdown(filtered.papers, group_by='year')
    with open("./papers_by_year.md", "w") as f:
        f.write(md_content)
    print("Saved markdown summary to papers_by_year.md")

    return filtered


def example_data_analysis():
    """Example: Analyze papers with pandas."""
    stx.str.printc("\n=== Data Analysis with Pandas ===", c="blue")

    scholar = Scholar()
    papers = scholar.search("machine learning", limit=100)

    # Convert to DataFrame
    df = papers.to_dataframe()

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns)}")

    # Basic statistics
    print("\nPublication year distribution:")
    print(df['year'].value_counts().head())

    print("\nTop journals:")
    print(df['journal'].value_counts().head())

    # Papers with both high citations and high impact factor
    high_quality = df[
        (df['citation_count'] > 100) &
        (df['impact_factor'] > 5.0)
    ]
    print(f"\nHigh quality papers (100+ citations, IF > 5): {len(high_quality)}")

    # Save analysis
    df.to_csv("./custom_analysis.csv", index=False)
    print("\nSaved analysis to custom_analysis.csv")


def example_similar_papers():
    """Example: Find similar papers."""
    stx.str.printc("\n=== Finding Similar Papers ===", c="blue")

    scholar = Scholar()

    # Find papers similar to a landmark paper
    similar = scholar.find_similar("Attention is All You Need", limit=10)

    print(f"Found {len(similar)} similar papers:")
    for i, paper in enumerate(similar[:5], 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:2])}...")
        print(f"   Year: {paper.year}, Source: {paper.source}")


def example_format_conversions():
    """Example: Convert between formats."""
    stx.str.printc("\n=== Format Conversions ===", c="blue")

    scholar = Scholar()
    papers = scholar.search("quantum computing", limit=5)

    # Convert to different formats
    print("Converting to different formats...")

    # RIS format (for EndNote, Mendeley)
    ris_content = papers_to_ris(papers.papers)
    with open("./papers.ris", "w") as f:
        f.write(ris_content)
    print("- Saved RIS format to papers.ris")

    # Markdown with journal grouping
    md_content = papers_to_markdown(papers.papers, group_by='journal')
    with open("./papers_by_journal.md", "w") as f:
        f.write(md_content)
    print("- Saved Markdown (by journal) to papers_by_journal.md")

    # Custom JSON with metadata
    from scitex.scholar import papers_to_json
    json_content = papers_to_json(papers.papers, indent=2, include_metadata=True)
    with open("./papers_metadata.json", "w") as f:
        f.write(json_content)
    print("- Saved JSON with metadata to papers_metadata.json")


def main():
    """Run all advanced examples."""

    # Run examples
    example_multi_source_search()
    example_custom_enrichment()
    example_literature_review()
    example_data_analysis()
    example_similar_papers()
    example_format_conversions()
    example_local_library()

    print("\n✅ All examples completed!")
    return 0


if __name__ == "__main__":
    main()

# EOF
