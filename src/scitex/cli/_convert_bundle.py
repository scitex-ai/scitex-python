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

    # Read input bundle
    with zipfile.ZipFile(input_path, "r") as zf:
        # The spec is carried over as-is (the FTS layer normalizes it on
        # load); only a missing bundle_id is filled in.
        normalized_spec = json.loads(zf.read("spec.json"))
        if "bundle_id" not in normalized_spec:
            normalized_spec["bundle_id"] = str(uuid.uuid4())[:8]

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
