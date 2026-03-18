#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:20:00 (ywatanabe)"
# File: ./.dev/download_bibfile_papers.py
# ----------------------------------------

"""
Download papers from the bibfile.bib using OpenAthens.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar
from scitex.io import load


def download_bibfile_papers():
    """Download papers from bibfile.bib."""

    # Enable OpenAthens
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
    os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

    # Check if email is set
    email = os.environ.get("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("Please set your institutional email:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'")
        return

    print(f"Using email: {email}")

    # Initialize Scholar
    print("\nInitializing Scholar...")
    scholar = Scholar()

    # Load the bib file
    bibfile_path = "/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/bibfile.bib"
    print(f"\nLoading bibliography from: {bibfile_path}")

    # Load and parse the bibtex file
    papers = load(bibfile_path)
    print(f"\nFound {len(papers)} papers in the bibliography")

    # Extract DOIs from the papers
    dois = []
    paper_info = []

    for i, entry in enumerate(papers, 1):
        # Papers are loaded as dictionaries with nested structure
        paper = entry.get('fields', {})
        title = paper.get('title', 'Unknown title')
        authors = paper.get('author', '').split(' and ')
        year = paper.get('year', 'Unknown')
        journal = paper.get('journal', 'Unknown journal')
        doi = paper.get('doi', None)

        print(f"\n{i}. {title}")
        print(f"   Authors: {', '.join(authors[:3])}...")
        print(f"   Year: {year}")
        print(f"   Journal: {journal}")

        if doi:
            print(f"   DOI: {doi}")
            dois.append(doi)
            paper_info.append({
                'doi': doi,
                'title': title,
                'authors': authors,
                'year': year,
                'journal': journal
            })
        else:
            print("   No DOI found")

    if not dois:
        print("\nNo DOIs found in the bibliography")
        return

    # Create output directory
    output_dir = Path("./.dev/bibfile_pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download the PDFs
    print(f"\n📥 Downloading {len(dois)} PDFs...")

    try:
        # Download using DOIs
        result = scholar.download_pdfs(
            dois,
            download_dir=output_dir,
            show_progress=True,
            acknowledge_ethical_usage=False  # Using OpenAthens
        )

        # Check results
        pdf_files = list(output_dir.glob("*.pdf"))

        print(f"\n📊 Download Summary:")
        print(f"   Total papers: {len(dois)}")
        print(f"   Downloaded: {len(pdf_files)}")
        print(f"   Success rate: {len(pdf_files)/len(dois)*100:.1f}%")

        if pdf_files:
            print("\n✅ Downloaded PDFs:")
            for pdf in pdf_files:
                size_mb = pdf.stat().st_size / (1024 * 1024)
                print(f"   - {pdf.name} ({size_mb:.1f} MB)")

                # Try to match with paper info
                for info in paper_info:
                    if info['doi'].replace('/', '_') in pdf.name or info['doi'].split('/')[-1] in pdf.name:
                        print(f"     Title: {info['title'][:60]}...")
                        break

        # Save summary
        summary_file = output_dir / "download_summary.txt"
        with open(summary_file, "w") as f:
            f.write(f"Download Summary - {len(pdf_files)}/{len(dois)} PDFs\n")
            f.write("="*60 + "\n\n")

            for i, info in enumerate(paper_info, 1):
                f.write(f"{i}. {info['title']}\n")
                f.write(f"   DOI: {info['doi']}\n")
                f.write(f"   Year: {info['year']}\n")
                f.write(f"   Journal: {info['journal']}\n")

                # Check if downloaded
                downloaded = any(info['doi'].replace('/', '_') in pdf.name or
                               info['doi'].split('/')[-1] in pdf.name
                               for pdf in pdf_files)
                f.write(f"   Status: {'✅ Downloaded' if downloaded else '❌ Not available'}\n")
                f.write("\n")

        print(f"\n📝 Summary saved to: {summary_file}")

        # Check authentication status
        if scholar.is_openathens_authenticated():
            print("\n✓ OpenAthens authentication active")
        else:
            print("\n❌ OpenAthens not authenticated")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    download_bibfile_papers()
