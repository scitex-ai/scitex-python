#!/usr/bin/env python3
"""
How to use the OpenURL resolver with Scholar module
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.scitex.scholar import Scholar, ScholarConfig
from src.scitex.scholar._OpenURLResolver import OpenURLResolver

def demo_openurl_resolver():
    """Demonstrate OpenURL resolver usage."""

    print("=" * 80)
    print("OpenURL Resolver Demo - University of Melbourne")
    print("=" * 80)

    # Initialize Scholar
    config = ScholarConfig(
        pdf_dir="./pdfs",
        enable_auto_enrich=False
    )
    scholar = Scholar(config)

    # Search for a paper
    papers = scholar.search(
        "machine learning neuroscience",
        limit=3,
        sources=["pubmed"]
    )

    print(f"\nFound {len(papers)} papers")

    # Initialize OpenURL resolver with UniMelb URL
    resolver = OpenURLResolver("https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")

    for i, paper in enumerate(papers.papers):
        print(f"\n{'='*60}")
        print(f"Paper {i+1}: {paper.title[:60]}...")
        print(f"DOI: {paper.doi}")

        # Convert paper to metadata dict
        paper_metadata = {
            "title": paper.title,
            "authors": paper.authors,
            "journal": paper.journal,
            "year": paper.year,
            "doi": paper.doi,
            "pmid": paper.pmid,
        }

        # Build OpenURL
        openurl = resolver.build_openurl(paper_metadata)
        print(f"\nOpenURL (for manual access):")
        print(f"{openurl[:100]}...")

        # Try to resolve
        print("\nResolving through library...")
        result = resolver.resolve(paper_metadata)

        if result:
            print(f"✅ Access type: {result['access_type']}")
            if result.get('full_text_urls'):
                print(f"   Found {len(result['full_text_urls'])} full-text links")
                for url in result['full_text_urls'][:2]:
                    print(f"   - {url[:80]}...")
        else:
            print("❌ Could not resolve through library")

    print("\n" + "="*80)
    print("How to use OpenURL:")
    print("1. Copy the OpenURL and paste in your browser")
    print("2. You'll be redirected to your library's access page")
    print("3. Log in with your institutional credentials if needed")
    print("4. Access the full text through your library's subscriptions")
    print("\nNote: This works best when on campus or via VPN")

def integrated_download_with_resolver():
    """Show how resolver could be integrated into download process."""

    print("\n" + "="*80)
    print("Integrated Download with OpenURL Resolver")
    print("="*80)

    # This is conceptual - showing how it would work
    config = ScholarConfig(
        pdf_dir="./pdfs",
        # Future: Add resolver URL to config
        # openurl_resolver="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )

    scholar = Scholar(config)

    # Search
    papers = scholar.search("epilepsy detection", limit=1)

    if papers.papers:
        paper = papers.papers[0]
        print(f"\nTrying to download: {paper.title}")

        # Current download strategies:
        print("\nDownload strategies:")
        print("1. Direct publisher patterns")
        print("2. Lean Library (if installed)")
        print("3. OpenURL resolver (NEW!)")
        print("4. Sci-Hub (if acknowledged)")

        # Future enhancement would add OpenURL as a strategy
        # in PDFDownloader._download_from_doi_async()

        print("\nTo add OpenURL to download pipeline:")
        print("1. Modify _PDFDownloader.py to include OpenURL strategy")
        print("2. Add after Direct patterns, before Sci-Hub")
        print("3. Use resolver to find institutional PDF links")

if __name__ == "__main__":
    # Run the demo
    demo_openurl_resolver()

    # Show integration concept
    integrated_download_with_resolver()
