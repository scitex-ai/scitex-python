#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 02:14:00 (ywatanabe)"
# File: ./.dev/download_alcohol_paper_by_doi.py
# ----------------------------------------

"""
Download the alcohol paper using its DOI.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Scholar


def download_by_doi():
    """Download paper by DOI."""

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

    # The DOI we found
    doi = "10.1038/s41593-025-01970-x"
    title = "Suppression of binge alcohol drinking by an inhibitory neuronal ensemble in the mouse medial orbitofrontal cortex"

    print(f"\n📄 Paper Details:")
    print(f"Title: {title}")
    print(f"DOI: {doi}")
    print(f"Journal: Nature Neuroscience")
    print(f"Year: 2025")

    # Create output directory
    output_dir = Path("./.dev/alcohol_paper_pdf")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download the PDF
    print("\n📥 Downloading PDF...")

    try:
        # Download using DOI
        result = scholar.download_pdfs(
            [doi],
            download_dir=output_dir,
            show_progress=True,
            acknowledge_ethical_usage=False  # Using OpenAthens, not Sci-Hub
        )

        # Check results
        pdf_files = list(output_dir.glob("*.pdf"))
        if pdf_files:
            print(f"\n✅ Successfully downloaded PDF!")
            for pdf in pdf_files:
                size_mb = pdf.stat().st_size / (1024 * 1024)
                print(f"   File: {pdf.name}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Path: {pdf.absolute()}")

                # Also save the paper info
                info_file = output_dir / "paper_info.txt"
                with open(info_file, "w") as f:
                    f.write(f"Title: {title}\n")
                    f.write(f"DOI: {doi}\n")
                    f.write(f"Journal: Nature Neuroscience\n")
                    f.write(f"Year: 2025\n")
                    f.write(f"URL: https://doi.org/{doi}\n")
                print(f"\n📝 Paper info saved to: {info_file}")

        else:
            print("\n❌ PDF download failed")
            print("   This might be because:")
            print("   - The paper is not available through your institution")
            print("   - OpenAthens authentication needs to be refreshed")
            print("   - The paper is very new (2025) and might not be available yet")
            print(f"\n💡 Try accessing directly: https://doi.org/{doi}")

            # Check if authentication is working
            if scholar.is_openathens_authenticated():
                print("\n✓ OpenAthens is authenticated")
            else:
                print("\n❌ OpenAthens is not authenticated - try authenticating first")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    download_by_doi()
