#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_metadata_modules/read_metadata_svg.py

"""SVG metadata reading from <metadata> element."""

import json
import re
from typing import Any, Dict, Optional


def read_metadata_svg(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Read metadata from an SVG file.

    Args:
        image_path: Path to the SVG file.

    Returns
    -------
        Dictionary containing metadata, or None if no metadata found.
    """
    metadata = None

    with open(image_path, encoding="utf-8") as f:
        svg_content = f.read()

    # Look for scitex metadata element (supports both CDATA and raw JSON)
    match = re.search(
        r'<metadata[^>]*id="scitex_metadata"[^>]*>.*?'
        r"<scitex:data>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</scitex:data>.*?</metadata>",
        svg_content,
        flags=re.DOTALL,
    )
    if match:
        metadata_json = match.group(1)
        try:
            metadata = json.loads(metadata_json)
        except json.JSONDecodeError:
            metadata = {"raw": metadata_json}

    return metadata


# EOF
