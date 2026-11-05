"""Observed normal Hatch 1.33 static-2.5 metadata, plus real header controls."""

import copy
import importlib.metadata
import importlib.util
from pathlib import Path
import tomllib
import unittest

from hatchling.builders.wheel import WheelBuilder

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("owned_metadata25_verifier", ROOT / ".github/ci/release-identity.py")
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)
if importlib.metadata.version("hatchling") != "1.33.0":
    raise RuntimeError("These controls qualify only the observed Hatch 1.33 cohort")
BUILDER = WheelBuilder(str(ROOT))
RAW = BUILDER.config.core_metadata_constructor(BUILDER.metadata).encode()
ENTRY_POINTS = BUILDER.construct_entry_points_file().encode()
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]


def inserted(header):
    first, rest = RAW.split(b"\n", 1)
    return first + b"\n" + header + b"\n" + rest


class StaticMetadata25Tests(unittest.TestCase):
    def test_actual_normal_backend_headers_bind_full_source_contract(self):
        result = RELEASE.metadata_source_identity(RAW, RAW, ENTRY_POINTS, PROJECT, required_version="2.5")
        assert result == {"runtime_requirements": 631, "extras": 77, "entry_point_groups": 3}

    def test_qualified_profile_refuses_downgrade_future_duplicate_and_unknown(self):
        for version in (b"2.4", b"2.6", b"3.0", b"unknown"):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "metadata version"):
                RELEASE.metadata_source_identity(RAW.replace(b"Metadata-Version: 2.5", b"Metadata-Version: " + version, 1), RAW, ENTRY_POINTS, PROJECT, required_version="2.5")
        with self.assertRaisesRegex(ValueError, "metadata version"):
            RELEASE.metadata_source_identity(inserted(b"Metadata-Version: 2.5"), RAW, ENTRY_POINTS, PROJECT, required_version="2.5")
        for version in (b"2.4", b"2.6"):
            raw = RAW.replace(b"Metadata-Version: 2.5", b"Metadata-Version: " + version, 1)
            with self.subTest(sdist_version=version), self.assertRaisesRegex(ValueError, "metadata version"):
                RELEASE.metadata_source_identity(RAW, raw, ENTRY_POINTS, PROJECT, required_version="2.5")

    def test_legacy_default_and_explicit_profile_enum_remain_bounded(self):
        with self.assertRaisesRegex(ValueError, "metadata version"):
            RELEASE.metadata_source_identity(RAW, RAW, ENTRY_POINTS, PROJECT)
        for version in ("2.4", "2.6", "future", 2.5, [], {}):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "qualified metadata version"):
                RELEASE.metadata_source_identity(RAW, RAW, ENTRY_POINTS, PROJECT, required_version=version)

    def test_import_claims_dynamic_and_unqualified_source_declarations_refuse(self):
        for header in (b"Import-Name: scitex", b"Import-Name:", b"Import-Namespace: scitex", b"Dynamic: Summary"):
            with self.subTest(header=header), self.assertRaises(ValueError):
                RELEASE.metadata_source_identity(inserted(header), RAW, ENTRY_POINTS, PROJECT, required_version="2.5")
        for field in ("import-names", "import-namespaces"):
            project = copy.deepcopy(PROJECT)
            project[field] = ["scitex"]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "source import declarations"):
                RELEASE.metadata_source_identity(RAW, RAW, ENTRY_POINTS, project, required_version="2.5")

    def test_license_expression_and_file_remain_exact_source_values(self):
        candidates = [
            RAW.replace(b"License-Expression: AGPL-3.0-only", b"License-Expression: MIT", 1),
            inserted(b"License-Expression: AGPL-3.0-only"), inserted(b"License: AGPL-3.0-only"),
            RAW.replace(b"License-File: LICENSE", b"License-File: ../LICENSE", 1),
            inserted(b"License-File: LICENSE"),
        ]
        for raw in candidates:
            with self.subTest(raw_sha=__import__("hashlib").sha256(raw).hexdigest()), self.assertRaisesRegex(ValueError, "License"):
                RELEASE.metadata_source_identity(raw, RAW, ENTRY_POINTS, PROJECT, required_version="2.5")

    def test_full_dependencies_and_extras_cannot_be_stripped_in_25(self):
        for prefix in (b"Requires-Dist:", b"Provides-Extra:"):
            raw = b"\n".join(line for line in RAW.split(b"\n") if not line.startswith(prefix))
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                RELEASE.metadata_source_identity(raw, RAW, ENTRY_POINTS, PROJECT, required_version="2.5")


if __name__ == "__main__":
    unittest.main()
