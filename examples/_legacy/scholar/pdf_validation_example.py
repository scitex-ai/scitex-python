#!/usr/bin/env python3
"""Example: Validate downloaded PDFs for completeness and readability."""

import asyncio
from pathlib import Path
from scitex.scholar.validation import PDFValidator, ValidationResult


async def validation_example():
    """Demonstrate PDF validation features."""

    print("=== SciTeX Scholar - PDF Validation Example ===\n")

    # Initialize validator
    validator = PDFValidator(cache_results=True)

    # Example 1: Validate single PDF
    print("1. Validating a single PDF:")
    print("-" * 50)

    # Replace with actual PDF path
    pdf_path = Path("./pdfs/example_paper.pdf")

    if pdf_path.exists():
        result = validator.validate(pdf_path)
        print(f"Result: {result}")

        if result.is_valid:
            print(f"  ✓ Valid PDF")
            print(f"  Pages: {result.page_count}")
            print(f"  Size: {result.file_size / (1024*1024):.1f} MB")
            print(f"  Searchable: {'Yes' if result.has_text else 'No'}")

            if result.metadata:
                print("  Metadata:")
                for key, value in result.metadata.items():
                    print(f"    {key}: {value}")
        else:
            print(f"  ✗ Invalid PDF")
            for error in result.errors:
                print(f"    ERROR: {error}")
    else:
        print(f"  Sample PDF not found at {pdf_path}")

    # Example 2: Validate directory
    print("\n\n2. Validating all PDFs in directory:")
    print("-" * 50)

    pdf_dir = Path("./pdfs")
    if pdf_dir.exists():
        results = validator.validate_directory(pdf_dir, recursive=True)

        # Summary
        valid_count = sum(1 for r in results.values() if r.is_valid)
        print(f"Found {len(results)} PDFs: {valid_count} valid, {len(results) - valid_count} invalid")

        # Show invalid files
        for path, result in results.items():
            if not result.is_valid:
                print(f"\n  ✗ {Path(path).name}")
                for error in result.errors:
                    print(f"    - {error}")
    else:
        print(f"  Directory {pdf_dir} not found")

    # Example 3: Batch validation with progress
    print("\n\n3. Batch validation with progress:")
    print("-" * 50)

    # Create sample list of PDFs
    pdf_list = list(Path(".").rglob("*.pdf"))[:5]  # First 5 PDFs found

    if pdf_list:
        async def progress_callback(current, total, filename):
            print(f"  Validating {current}/{total}: {Path(filename).name}")

        results = await validator.validate_batch_async(pdf_list, progress_callback)

        # Generate report
        print("\n4. Validation Report:")
        print("-" * 50)
        report = validator.generate_report(results)
        print(report)

        # Save report
        report_path = Path("./validation_report.txt")
        validator.generate_report(results, report_path)
        print(f"\nReport saved to: {report_path}")
    else:
        print("  No PDFs found for batch validation")


async def validate_after_download():
    """Example: Validate PDFs after downloading."""

    print("\n\n=== Validation After Download ===\n")

    from scitex.scholar import Scholar

    # Simulated download results
    download_results = {
        "10.1234/example1": {"success": True, "path": "./pdfs/paper1.pdf"},
        "10.1234/example2": {"success": True, "path": "./pdfs/paper2.pdf"},
        "10.1234/example3": {"success": False, "error": "404 Not Found"},
    }

    # Validate successful downloads
    validator = PDFValidator()
    validation_results = {}

    for doi, result in download_results.items():
        if result.get("success") and result.get("path"):
            pdf_path = Path(result["path"])
            if pdf_path.exists():
                validation = validator.validate(pdf_path)
                validation_results[doi] = validation

                if validation.is_valid and validation.is_complete:
                    print(f"✓ {doi}: Valid and complete ({validation.page_count} pages)")
                elif validation.is_valid:
                    print(f"⚠ {doi}: Valid but may be incomplete")
                else:
                    print(f"✗ {doi}: Invalid PDF - {validation.errors}")
            else:
                print(f"? {doi}: File not found at {pdf_path}")

    # Summary
    print(f"\nValidation Summary:")
    print(f"  Total downloads: {len(download_results)}")
    print(f"  Successful downloads: {sum(1 for r in download_results.values() if r.get('success'))}")
    print(f"  Valid PDFs: {sum(1 for v in validation_results.values() if v.is_valid)}")
    print(f"  Complete PDFs: {sum(1 for v in validation_results.values() if v.is_complete)}")


def check_common_issues():
    """Check for common PDF issues."""

    print("\n\n=== Common PDF Issues ===\n")

    issues = [
        {
            "name": "Empty file",
            "description": "0 byte file - download failed",
            "check": lambda r: r.file_size == 0
        },
        {
            "name": "Too small",
            "description": "< 10KB - likely error page",
            "check": lambda r: r.file_size < 10000
        },
        {
            "name": "No pages",
            "description": "Valid PDF but 0 pages",
            "check": lambda r: r.is_valid and r.page_count == 0
        },
        {
            "name": "Scanned PDF",
            "description": "No searchable text",
            "check": lambda r: r.is_valid and not r.has_text
        },
        {
            "name": "Truncated",
            "description": "PDF appears incomplete",
            "check": lambda r: r.is_valid and not r.is_complete
        }
    ]

    for issue in issues:
        print(f"• {issue['name']}: {issue['description']}")

    print("\nValidation helps identify these issues automatically!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(validation_example())
    asyncio.run(validate_after_download())
    check_common_issues()

    print("\n\nNote: Install optional dependencies for full functionality:")
    print("  pip install PyPDF2    # For metadata extraction")
    print("  pip install pdfplumber # For text extraction")
