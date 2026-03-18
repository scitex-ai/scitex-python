#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-11 16:30:00
# File: /home/ywatanabe/proj/scitex-code/examples/msword/04_custom_profile.py

"""
Example: Create and use custom journal profiles.

This example demonstrates how to:
1. Create a custom journal profile
2. Register it for use with load_docx/save_docx
3. Customize style mappings for specific templates
"""

from pathlib import Path
import tempfile

from scitex.msword import (
    BaseWordProfile,
    register_profile,
    get_profile,
    list_profiles,
    load_docx,
    save_docx,
)

# Path to sample documents
DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "MSWORD_MANUSCTIPS"
RESNA_DOCX = DOCS_DIR / "RESNA 2025 Scientific Paper Template.docx"


def example_create_custom_profile():
    """Create a custom journal profile."""
    print("=" * 60)
    print("Create Custom Journal Profile")
    print("=" * 60)

    # Create a custom profile for a hypothetical journal
    custom_profile = BaseWordProfile(
        name="my-custom-journal",
        description="Custom profile for My Journal (2025)",
        heading_styles={
            1: "Heading 1",
            2: "Heading 2",
            3: "Heading 3",
        },
        caption_style="Caption",
        normal_style="Normal",
        reference_section_titles=["References", "Bibliography", "Works Cited"],
        figure_caption_prefixes=["Figure", "Fig.", "Fig"],
        table_caption_prefixes=["Table", "Tab."],
        columns=1,
        double_anonymous=False,
    )

    print(f"\n1. Created profile: {custom_profile.name}")
    print(f"   Description: {custom_profile.description}")
    print(f"   Columns: {custom_profile.columns}")
    print(f"   Double-anonymous: {custom_profile.double_anonymous}")

    # Register the profile
    register_profile(custom_profile)

    print(f"\n2. Registered profile")
    print(f"   Available profiles: {list_profiles()}")

    # Use the custom profile
    if RESNA_DOCX.exists():
        print(f"\n3. Using custom profile to load document...")
        doc = load_docx(RESNA_DOCX, profile="my-custom-journal")
        print(f"   Loaded {len(doc['blocks'])} blocks")
        print(f"   Profile used: {doc['metadata']['profile']}")


def example_specialized_profiles():
    """Create specialized profiles for different use cases."""
    print("\n" + "=" * 60)
    print("Specialized Profiles")
    print("=" * 60)

    # Profile for double-blind review
    blind_profile = BaseWordProfile(
        name="blind-review",
        description="Double-blind review submission",
        heading_styles={1: "Heading 1", 2: "Heading 2", 3: "Heading 3"},
        double_anonymous=True,
    )

    # Profile for two-column conference papers
    conference_profile = BaseWordProfile(
        name="conference-2col",
        description="Two-column conference paper",
        heading_styles={1: "Heading 1", 2: "Heading 2"},
        columns=2,
        reference_section_titles=["References", "REFERENCES"],
    )

    # Profile with custom list styles
    thesis_profile = BaseWordProfile(
        name="thesis",
        description="Thesis/dissertation format",
        heading_styles={
            1: "Chapter Title",
            2: "Section Heading",
            3: "Subsection Heading",
            4: "Paragraph Heading",
        },
        list_styles={
            "bullet": "Thesis Bullet",
            "numbered": "Thesis Numbered",
        },
        columns=1,
    )

    # Register all profiles
    for profile in [blind_profile, conference_profile, thesis_profile]:
        register_profile(profile)
        print(f"\nRegistered: {profile.name}")
        print(f"  Description: {profile.description}")
        print(f"  Columns: {profile.columns}")
        print(f"  Double-anonymous: {profile.double_anonymous}")

    print(f"\nAll available profiles: {list_profiles()}")


def example_profile_with_hooks():
    """Create a profile with pre/post processing hooks."""
    print("\n" + "=" * 60)
    print("Profile with Processing Hooks")
    print("=" * 60)

    def post_import_hook(doc):
        """Add a warning for documents with many images."""
        num_images = len(doc.get("images", []))
        if num_images > 5:
            doc["warnings"].append(
                f"Document contains {num_images} images. "
                "Consider reducing for faster compilation."
            )
        return doc

    def pre_export_hook(doc):
        """Ensure all headings are uppercase for this journal."""
        for block in doc.get("blocks", []):
            if block.get("type") == "heading" and block.get("level") == 1:
                block["text"] = block.get("text", "").upper()
        return doc

    # Create profile with hooks
    hooked_profile = BaseWordProfile(
        name="uppercase-headings",
        description="Journal requiring uppercase section headings",
        heading_styles={1: "Heading 1", 2: "Heading 2"},
        post_import_hooks=[post_import_hook],
        pre_export_hooks=[pre_export_hook],
    )

    register_profile(hooked_profile)
    print(f"\n1. Created profile with hooks: {hooked_profile.name}")

    # Demonstrate with a sample document
    doc = {
        "blocks": [
            {"type": "heading", "level": 1, "text": "Introduction"},
            {"type": "paragraph", "text": "Some content here."},
            {"type": "heading", "level": 1, "text": "Methods"},
            {"type": "paragraph", "text": "More content."},
        ],
        "metadata": {},
        "images": [{"hash": f"img{i}"} for i in range(7)],  # Trigger warning
        "references": [],
        "warnings": [],
    }

    # Apply post-import hook manually (normally called during load)
    doc = post_import_hook(doc)
    print(f"\n2. After post-import hook:")
    print(f"   Warnings: {doc['warnings']}")

    # Apply pre-export hook manually (normally called during save)
    doc = pre_export_hook(doc)
    print(f"\n3. After pre-export hook:")
    for block in doc["blocks"]:
        if block.get("type") == "heading":
            print(f"   Heading: {block['text']}")


def example_compare_profiles():
    """Compare different profiles side by side."""
    print("\n" + "=" * 60)
    print("Compare Built-in Profiles")
    print("=" * 60)

    profiles_to_compare = [
        "generic",
        "mdpi-ijerph",
        "resna-2025",
        "iop-double-anonymous",
        "ieee",
    ]

    print(f"\n{'Profile':<25} {'Columns':<10} {'Anonymous':<12} {'Ref Titles'}")
    print("-" * 70)

    for name in profiles_to_compare:
        try:
            profile = get_profile(name)
            ref_titles = ", ".join(profile.reference_section_titles[:2])
            print(f"{profile.name:<25} {profile.columns:<10} {str(profile.double_anonymous):<12} {ref_titles}")
        except KeyError:
            print(f"{name:<25} (not found)")


def main():
    example_create_custom_profile()
    example_specialized_profiles()
    example_profile_with_hooks()
    example_compare_profiles()


if __name__ == "__main__":
    main()
