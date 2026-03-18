#!/usr/bin/env python3
"""Test PDF download functionality with detailed debugging."""

from scitex.scholar import Scholar, ScholarConfig
from scitex import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Create config with ethical acknowledgment
config = ScholarConfig(
    acknowledge_scihub_ethical_usage=True,
    pubmed_email="ywatanabe@gmail.com"
)

# Initialize Scholar
scholar = Scholar(config=config)

# Search for a paper we know should be downloadable
print("\n=== Testing PDF download ===")
print("1. Searching for papers...")
papers = scholar.search("systems neuroscience", limit=3)

print(f"\nFound {len(papers)} papers:")
for i, paper in enumerate(papers):
    print(f"{i+1}. {paper.title}")
    print(f"   DOI: {paper.doi}")
    print(f"   Source: {paper.source}")
    print(f"   PDF URL: {paper.pdf_url}")

# Try downloading
print("\n2. Attempting downloads...")
results = scholar.download_pdfs(papers, acknowledge_ethical_usage=True)

print(f"\n=== Download Results ===")
print(f"✓ Successful: {results['successful']}")
print(f"✗ Failed: {results['failed']}")
print(f"Downloaded files: {results.get('downloaded_files', {})}")

# Try with a known open access DOI
print("\n3. Testing with known open access paper...")
open_access_doi = "10.1371/journal.pone.0029609"  # Known open access
results_oa = scholar.download_pdfs([open_access_doi], acknowledge_ethical_usage=True)
print(f"Open access download - Success: {results_oa['successful']}, Failed: {results_oa['failed']}")

# Check download directory
import os
pdf_dir = scholar.workspace_dir / "pdfs"
print(f"\n4. PDF directory: {pdf_dir}")
print(f"   Exists: {pdf_dir.exists()}")
if pdf_dir.exists():
    pdfs = list(pdf_dir.glob("*.pdf"))
    print(f"   Contains {len(pdfs)} PDFs")
    for pdf in pdfs[:5]:  # Show first 5
        print(f"   - {pdf.name} ({pdf.stat().st_size / 1024:.1f} KB)")
