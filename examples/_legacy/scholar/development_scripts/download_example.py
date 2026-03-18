#!/usr/bin/env python3
"""
Example: Download PDFs using SciTeX Scholar

Shows how to search for papers and download PDFs with proper configuration.
"""

from scitex.scholar import Scholar, ScholarConfig

# Configure Scholar
config = ScholarConfig(
    # Required for PubMed searches
    pubmed_email="your-email@example.com",

    # Enable Sci-Hub (requires ethical acknowledgment)
    acknowledge_scihub_ethical_usage=True,

    # Optional: Get better citation data
    # semantic_scholar_api_key="your-api-key",
)

# Initialize Scholar
scholar = Scholar(config=config)

# Search for papers
print("Searching for neuroscience papers...")
papers = scholar.search("neuroscience open access", limit=5)

print(f"\nFound {len(papers)} papers:")
for i, paper in enumerate(papers, 1):
    print(f"{i}. {paper.title[:80]}...")
    print(f"   DOI: {paper.doi}")
    print(f"   Year: {paper.year}")
    print(f"   Citations: {paper.citation_count}")

# Download PDFs
print("\nDownloading PDFs...")
results = scholar.download_pdfs(
    papers,
    acknowledge_ethical_usage=True,  # Required for Sci-Hub
    show_progress=True
)

# Show results
print(f"\n=== Download Summary ===")
print(f"✓ Successful: {results['successful']}")
print(f"✗ Failed: {results['failed']}")

if results['downloaded_files']:
    print("\nDownloaded files:")
    for doi, path in results['downloaded_files'].items():
        print(f"  {doi} -> {path}")

# Access your PDFs
pdf_dir = scholar.get_workspace_dir() / "pdfs"
print(f"\nAll PDFs are in: {pdf_dir}")

# Example: Search and download specific DOIs
specific_dois = [
    "10.1371/journal.pone.0029609",  # Open access
    "10.1038/s41586-019-1786-y",      # Nature paper
]

print("\n\nDownloading specific DOIs...")
results = scholar.download_pdfs(specific_dois, acknowledge_ethical_usage=True)
print(f"Downloaded {results['successful']}/{len(specific_dois)} papers")
