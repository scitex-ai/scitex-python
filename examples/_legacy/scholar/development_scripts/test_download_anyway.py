#!/usr/bin/env python3
"""
Test downloading papers with current setup
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.scitex.scholar import Scholar, ScholarConfig

def test_downloads():
    """Test downloading the requested papers."""

    print("=" * 80)
    print("TESTING PDF DOWNLOADS")
    print("=" * 80)

    # Configure Scholar
    config = ScholarConfig(
        pdf_dir="./.dev/pdfs_final",
        enable_auto_download=False,
        enable_auto_enrich=False,
        openathens_enabled=False,
        use_lean_library=True,  # Try with Lean Library anyway
        acknowledge_scihub_ethical_usage=True,  # Enable Sci-Hub as fallback
        debug_mode=False
    )

    scholar = Scholar(config)
    output_dir = Path("./.dev/pdfs_final")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Papers to download
    papers = [
        {
            "doi": "10.1038/s41593-025-01990-7",
            "title": "Addressing artifactual bias in large, automated MRI analyses"
        },
        {
            "doi": "10.1007/s13755-020-00129-1",
            "title": "Automated epilepsy detection techniques from EEG signals"
        }
    ]

    print(f"\n📁 Output directory: {output_dir.absolute()}")
    print("\n" + "-" * 60)

    for paper in papers:
        print(f"\n📄 Downloading: {paper['title'][:50]}...")
        print(f"   DOI: {paper['doi']}")

        downloaded = scholar.download_pdfs(
            paper['doi'],
            download_dir=output_dir,
            force=True,
            show_progress=True
        )

        if len(downloaded) > 0:
            print("✅ Download successful!")
            for dl_paper in downloaded.papers:
                if dl_paper.pdf_path:
                    pdf_path = Path(dl_paper.pdf_path)
                    if pdf_path.exists():
                        size_kb = pdf_path.stat().st_size / 1024
                        print(f"   File: {pdf_path.name}")
                        print(f"   Size: {size_kb:.1f} KB")

                        # Check content
                        import subprocess
                        try:
                            text = subprocess.run(
                                ["pdftotext", str(pdf_path), "-", "-l", "1"],
                                capture_output=True,
                                text=True
                            ).stdout[:300].lower()

                            if "reporting summary" in text:
                                print("   ⚠️  WARNING: This is a reporting summary, not the full paper")
                            elif "abstract" in text:
                                print("   ✅ This appears to be the full paper!")
                            elif "review" in text and "epilepsy" in text:
                                print("   ✅ This appears to be the epilepsy review paper!")
                        except:
                            pass
        else:
            print("❌ Download failed")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    pdf_files = list(output_dir.glob("*.pdf"))
    if pdf_files:
        print(f"\n✅ Downloaded {len(pdf_files)} files:")
        for pdf in sorted(pdf_files):
            size_kb = pdf.stat().st_size / 1024
            print(f"   - {pdf.name} ({size_kb:.1f} KB)")
    else:
        print("\n❌ No files downloaded")

    print("\n💡 Tips:")
    print("- If you got reporting summaries instead of full papers:")
    print("  1. Make sure Lean Library is configured with your institution")
    print("  2. Or try accessing the paper manually in Chrome first")
    print("- Sci-Hub is enabled as a fallback for paywalled content")

if __name__ == "__main__":
    test_downloads()
