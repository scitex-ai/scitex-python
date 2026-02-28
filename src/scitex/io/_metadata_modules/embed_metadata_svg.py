#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_metadata_modules/embed_metadata_svg.py

"""SVG metadata embedding using <metadata> element."""

import re


def embed_metadata_svg(image_path: str, metadata_json: str) -> None:
    """
    Embed metadata into an SVG file using <metadata> element.

    Args:
        image_path: Path to the SVG file.
        metadata_json: JSON string of metadata to embed.

    Raises
    ------
        ValueError: If the SVG file is invalid.
    """
    with open(image_path, encoding="utf-8") as f:
        svg_content = f.read()

    # Remove existing scitex metadata if present
    svg_content = re.sub(
        r'<metadata[^>]*id="scitex_metadata"[^>]*>.*?</metadata>',
        "",
        svg_content,
        flags=re.DOTALL,
    )

    # Find the opening <svg> tag and insert metadata after it
    svg_match = re.search(r"(<svg[^>]*>)", svg_content)
    if svg_match:
        svg_tag_end = svg_match.end()
        # Create metadata element with scitex data
        metadata_element = (
            f'\n<metadata id="scitex_metadata">'
            f"<scitex:data><![CDATA[{metadata_json}]]></scitex:data>"
            f"</metadata>\n"
        )
        svg_content = (
            svg_content[:svg_tag_end] + metadata_element + svg_content[svg_tag_end:]
        )

        # Ensure scitex namespace is declared in svg tag if not present
        if "xmlns:scitex" not in svg_content:
            svg_content = svg_content.replace(
                "<svg",
                '<svg xmlns:scitex="http://scitex.io/metadata"',
                1,
            )

        with open(image_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
    else:
        raise ValueError(f"Invalid SVG file: {image_path}")


# EOF
