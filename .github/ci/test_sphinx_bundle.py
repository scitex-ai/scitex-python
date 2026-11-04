"""Real Sphinx producer controls, using small owned source trees."""

import importlib.util
from pathlib import Path
import tempfile
import subprocess
import os
import sys
import zipfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("owned_sphinx_bundle", ROOT / "build_hooks/sphinx_bundle.py")
PRODUCER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRODUCER)


def source_at(root, text):
    source = root / "docs/sphinx"
    source.mkdir(parents=True)
    (source / "conf.py").write_text('project = "Owned fixture"\nrelease = "2.30.9"\nextensions = []\n')
    (source / "index.rst").write_text(text)


class SphinxBundleTests(unittest.TestCase):
    def test_real_pep517_wheel_from_sdist_has_one_copy_of_generated_docs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            source_at(root, "Owned normal PEP517 page\n========================\n")
            (root / "src/scitex").mkdir(parents=True)
            (root / "src/scitex/__init__.py").write_text("")
            (root / "build_hooks").mkdir()
            (root / "build_hooks/sphinx_bundle.py").write_bytes((ROOT / "build_hooks/sphinx_bundle.py").read_bytes())
            (root / ".gitignore").write_text("src/scitex/_sphinx_html/\n/dist\n")
            (root / "pyproject.toml").write_text(
                '[build-system]\nrequires = ["hatchling==1.33.0"]\nbuild-backend = "hatchling.build"\n'
                '[project]\nname = "scitex"\nversion = "1.0.0"\n'
                '[tool.hatch.build.hooks.custom]\npath = "build_hooks/sphinx_bundle.py"\n'
                '[tool.hatch.build.targets.wheel]\nartifacts = ["src/scitex/_sphinx_html/**"]\n'
            )
            scratch = Path(temporary) / "scratch"
            scratch.mkdir()
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-m", "build", "--no-isolation", str(root)],
                env={"PATH": os.defpath, "HOME": str(root / "home"), "TMPDIR": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                self.fail(result.stdout + result.stderr)
            with zipfile.ZipFile(next((root / "dist").glob("*.whl"))) as wheel:
                names = wheel.namelist()
                html = wheel.read("scitex/_sphinx_html/index.html")
            assert len(names) == len(set(names)) and names.count("scitex/_sphinx_html/index.html") == 1 and b"Owned normal PEP517 page" in html

    def test_current_producer_admission_refuses_real_legacy_source_frame(self):
        historical_spec = importlib.util.spec_from_file_location(
            "owned_historical_boundary_fixture", ROOT / ".github/ci/test_release_identity.py"
        )
        fixture = importlib.util.module_from_spec(historical_spec)
        historical_spec.loader.exec_module(fixture)
        with self.assertRaisesRegex(ValueError, "requires derived documentation"):
            fixture.RELEASE.check_source_layout(
                fixture.SOURCE, fixture.REPOSITORY, require_derived_docs=True
            )

    def test_actual_project_config_refuses_unresolved_source_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned\n=====\n")
            (root / "docs/sphinx/conf.py").write_bytes((ROOT / "docs/sphinx/conf.py").read_bytes())
            (root / "pyproject.toml").write_text('[project]\nversion = "unresolved"\n')
            with self.assertRaises(subprocess.CalledProcessError):
                PRODUCER.build_bundle(root, root / "output")
            assert not (root / "output").exists()

    def test_actual_sphinx_output_tracks_changed_source_and_has_no_incremental_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "First owned page\n================\n\nReal fixture content.\n")
            PRODUCER.build_bundle(root, root / "first")
            (root / "docs/sphinx/index.rst").write_text("Changed owned page\n==================\n\nChanged fixture content.\n")
            PRODUCER.build_bundle(root, root / "second")
            actual = ((root / "first/index.html").read_bytes(), (root / "second/index.html").read_bytes())
            assert b"First owned page" in actual[0] and b"Changed owned page" in actual[1] and actual[0] != actual[1] and not (root / "second/.buildinfo").exists()

    def test_existing_output_symlink_is_refused_and_target_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned\n=====\n")
            sentinel = root / "retained"
            sentinel.write_text("keep")
            (root / "output").symlink_to(sentinel)
            with self.assertRaisesRegex(ValueError, "must be absent"):
                PRODUCER.build_bundle(root, root / "output")
            assert sentinel.read_text() == "keep"

    def test_actual_sphinx_include_cannot_read_outside_owned_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            secret = root / "outside.txt"
            secret.write_text("private owned negative control")
            source = root / "source"
            source_at(source, "Owned\n=====\n\n.. include:: ../../../outside.txt\n")
            with self.assertRaises(subprocess.CalledProcessError):
                PRODUCER.build_bundle(source, root / "output")
            assert not (root / "output").exists()


if __name__ == "__main__":
    unittest.main()
