#!/usr/bin/env python3
# Timestamp: "2026-03-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/cli/_convert_bundle.py

"""Internal helper for converting legacy bundle formats to .stx."""

import json
import tempfile
import uuid
import zipfile
from pathlib import Path


def convert_bundle(input_path: Path, output_path: Path) -> None:
    """Convert a legacy bundle to .stx format.

    Args:
        input_path: Path to legacy bundle (.figz, .pltz, .statsz)
        output_path: Path for output .stx bundle
    """

    def generate_bundle_id():
        return str(uuid.uuid4())[:8]

    def normalize_spec(spec):
        return spec  # FTS handles normalization internally

    # Determine bundle type from extension
    ext = input_path.suffix
    type_map = {
        ".figz": "figure",
        ".pltz": "plot",
        ".statsz": "stats",
    }
    bundle_type = type_map.get(ext)

    # Read input bundle
    with zipfile.ZipFile(input_path, "r") as zf:
        # Read spec
        spec_data = zf.read("spec.json")
        spec = json.loads(spec_data)

        # Normalize to v2.0.0
        normalized_spec = normalize_spec(spec, bundle_type)

        # Ensure bundle_id
        if "bundle_id" not in normalized_spec:
            normalized_spec["bundle_id"] = generate_bundle_id()

        # Copy all files to new bundle
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract all
            zf.extractall(tmpdir)

            # Write updated spec
            spec_path = Path(tmpdir) / "spec.json"
            with open(spec_path, "w") as f:
                json.dump(normalized_spec, f, indent=2)

            # Create output bundle
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as out_zf:
                for file_path in Path(tmpdir).rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(tmpdir)
                        out_zf.write(file_path, arcname)


# EOF
