#!/usr/bin/env python3
"""Generate DOI URLs for manual or automated download."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar

# Enhance BibTeX and generate DOI URLs
scholar = Scholar(
    email_crossref="research@example.com",
    email_pubmed="research@example.com"
)

# Your BibTeX file
input_path = "/home/ywatanabe/win/downloads/papers.bib"

print("Finding DOIs for papers in your BibTeX file...")
print("=" * 60)

# Enhance to get DOIs
enhanced = scholar.enrich_bibtex(
    input_path,
    output_path="/home/ywatanabe/win/downloads/papers_with_dois.bib"
)

# Get papers with DOIs
papers_with_dois = [p for p in enhanced if p.doi]
print(f"\nFound {len(papers_with_dois)} papers with DOIs out of {len(enhanced)} total")

# Generate URL list
output_file = "/home/ywatanabe/win/downloads/doi_urls.txt"
with open(output_file, 'w') as f:
    f.write("# DOI URLs for Zotero Download\n")
    f.write("# Open each URL in Chrome and press Ctrl+Shift+S\n")
    f.write("# " + "="*50 + "\n\n")

    for i, paper in enumerate(papers_with_dois):
        f.write(f"# {i+1}. {paper.title[:70]}...\n")
        f.write(f"https://doi.org/{paper.doi}\n\n")

print(f"\n✓ Generated {output_file}")
print(f"  Contains {len(papers_with_dois)} DOI URLs")

# Also create a shell script for automated opening
shell_script = "/home/ywatanabe/win/downloads/open_dois_in_chrome.sh"
with open(shell_script, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write("# Open DOI URLs in Chrome for Zotero download\n\n")

    # Open in batches of 5 to avoid overwhelming the browser
    for i in range(0, len(papers_with_dois), 5):
        batch = papers_with_dois[i:i+5]
        f.write(f"# Batch {i//5 + 1}\n")
        for paper in batch:
            f.write(f'google-chrome "https://doi.org/{paper.doi}" &\n')
        f.write("sleep 10  # Wait before next batch\n\n")

import os
os.chmod(shell_script, 0o755)
print(f"✓ Generated {shell_script}")
print("  Run this script to open DOIs in Chrome in batches")

# Show summary
print("\n" + "="*60)
print("Next steps:")
print("1. Manual: Open doi_urls.txt and visit each URL")
print("2. Semi-auto: Run ./open_dois_in_chrome.sh")
print("3. Full auto: Use the Playwright script above")
print("\nIn Chrome with Zotero Connector:")
print("  • Press Ctrl+Shift+S on each paper page")
print("  • Or click the Zotero button in the toolbar")
print("="*60)
