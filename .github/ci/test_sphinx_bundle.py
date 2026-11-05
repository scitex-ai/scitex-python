"""Real Sphinx producer controls, using small owned source trees."""

import importlib.util
from pathlib import Path
import tempfile
import subprocess
import os
import sys
import zipfile
import tarfile
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
    def test_project_config_cannot_start_children_after_toolchain_bootstrap(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned config guard\n==================\n")
            marker = root / "must-not-exist"
            with (root / "docs/sphinx/conf.py").open("a") as stream:
                stream.write(
                    "import subprocess, sys\n"
                    "subprocess.run([sys.executable, '-c', "
                    + repr(f"from pathlib import Path; Path({str(marker)!r}).write_text('unexpected')")
                    + "], check=True)\n"
                )
            with self.assertRaises(subprocess.CalledProcessError):
                PRODUCER.build_bundle(root, root / "output")
            assert not marker.exists() and not (root / "output").exists()

    def test_build_uses_declared_dependencies_outside_interpreter_prefix(self):
        """PEP517 overlays install dependencies outside the caller's venv."""
        import venv

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned overlay page\n==================\n")
            with (root / "docs/sphinx/conf.py").open("a") as stream:
                stream.write('extensions = ["nbsphinx"]\n')
            bare = root / "bare"
            venv.EnvBuilder(with_pip=False).create(bare)
            dependency_paths = [
                str(Path(path).resolve()) for path in sys.path
                if path and Path(path).name in {"site-packages", "dist-packages"}
            ]
            import json

            driver = (
                "import sys,json,runpy; from pathlib import Path; "
                "sys.path[:0]=json.loads(sys.argv[1]); "
                "m=runpy.run_path(sys.argv[2]); "
                "m['build_bundle'](Path(sys.argv[3]),Path(sys.argv[4]))"
            )
            result = subprocess.run(
                [str(bare / "bin/python"), "-I", "-B", "-c", driver,
                 json.dumps(dependency_paths), str(ROOT / "build_hooks/sphinx_bundle.py"),
                 str(root), str(root / "output")],
                env={"PATH": os.defpath, "HOME": str(root / "home"), "TMPDIR": str(root)},
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                self.fail(result.stdout + result.stderr)
            assert b"Owned overlay page" in (root / "output/index.html").read_bytes()

    def test_actual_napoleon_config_hides_private_path_and_keeps_public_members(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned public API\n================\n\n.. automodule:: scitex\n   :members:\n")
            (root / "docs/sphinx/conf.py").write_bytes((ROOT / "docs/sphinx/conf.py").read_bytes())
            (root / "pyproject.toml").write_text('[project]\nversion = "2.30.9"\n')
            package = root / "src/scitex"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text(
                '\"\"\"Owned real autodoc fixture.\"\"\"\n'
                '__version__ = "2.30.9"\n'
                '__DIR__ = "/owned/private/installation/path"\n'
                '\"\"\"Private installation directory.\"\"\"\n'
                'PUBLIC_VALUE = 17\n'
                '\"\"\"Public documented data.\"\"\"\n'
                'def public_function(value=1):\n'
                '    \"\"\"Public documented function.\"\"\"\n'
                '    return value\n'
            )
            PRODUCER.build_bundle(root, root / "output")
            html = (root / "output/index.html").read_text()
            assert "scitex.__DIR__" not in html and "/owned/private/installation/path" not in html
            assert "scitex.public_function" in html and "scitex.PUBLIC_VALUE" in html

    def test_actual_config_refuses_installed_root_as_documented_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_at(root, "Owned\n=====\n\n.. automodule:: scitex\n")
            (root / "docs/sphinx/conf.py").write_bytes((ROOT / "docs/sphinx/conf.py").read_bytes())
            (root / "pyproject.toml").write_text('[project]\nversion = "2.30.9"\n')
            driver = "import runpy,sys; from pathlib import Path; m=runpy.run_path(sys.argv[1]); m['build_bundle'](Path(sys.argv[2]),Path(sys.argv[3]))"
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-c", driver, str(ROOT / "build_hooks/sphinx_bundle.py"), str(root), str(root / "output")],
                capture_output=True, text=True, timeout=30,
            )
            assert result.returncode != 0 and "instead of trusted source" in result.stderr and not (root / "output").exists()

    def test_real_pep517_wheel_from_sdist_has_one_copy_of_generated_docs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            source_at(root, "Owned normal PEP517 page\n========================\n")
            static = root / "docs/sphinx/_static"
            static.mkdir()
            (static / "fixture.png").write_bytes((ROOT / "docs/sphinx/_static/workflow.png").read_bytes())
            with (root / "docs/sphinx/index.rst").open("a") as stream:
                stream.write("\n.. image:: _static/fixture.png\n")
            with (root / "docs/sphinx/conf.py").open("a") as stream:
                stream.write('html_static_path = ["_static"]\n')
            # An ignored earlier alias must not consume the real directory inode.
            (root / "real-docs").mkdir()
            (root / "real-docs/authored.md").write_text("owned ordinary tracked source")
            (root / ".claude").mkdir()
            (root / ".claude/agents").symlink_to("../real-docs", target_is_directory=True)
            (root / "ignored.txt").write_text("tracked but ignored non-documentation")
            (root / "keep.tmp").write_text("negated ignore remains selected")
            (root / "src/scitex").mkdir(parents=True)
            (root / "src/scitex/__init__.py").write_text("")
            (root / "build_hooks").mkdir()
            (root / "build_hooks/sphinx_bundle.py").write_bytes((ROOT / "build_hooks/sphinx_bundle.py").read_bytes())
            (root / ".gitignore").write_text("src/scitex/_sphinx_html/\n/dist\n")
            (root / "pyproject.toml").write_text(
                '[build-system]\nrequires = ["hatchling==1.33.0"]\nbuild-backend = "hatchling.build"\n'
                '[project]\nname = "scitex"\nversion = "1.0.0"\n'
                '[tool.hatch.build.hooks.custom]\npath = "build_hooks/sphinx_bundle.py"\nsource-input-root = "docs/sphinx"\n'
                '[tool.hatch.build.targets.wheel]\nartifacts = ["src/scitex/_sphinx_html/**"]\n'
            )
            scratch = Path(temporary) / "scratch"
            scratch.mkdir()
            git_env = {"PATH": os.defpath, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
            subprocess.run(["git", "init", "--quiet", "--template=", str(root)], check=True, env=git_env, timeout=7)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True, env=git_env, timeout=7)
            with (root / ".gitignore").open("a") as stream:
                stream.write("*.png\n.claude/\nignored.txt\n*.tmp\n!keep.tmp\n")  # Tracked inputs become ignored.
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
                wheel_docs = {name: wheel.read(name) for name in names if name.startswith("scitex/_sphinx_html/")}
            with tarfile.open(next((root / "dist").glob("*.tar.gz"))) as sdist:
                archive_names = set(sdist.getnames())
                assert "scitex-1.0.0/real-docs/authored.md" in archive_names
                assert "scitex-1.0.0/ignored.txt" not in archive_names
                assert "scitex-1.0.0/keep.tmp" in archive_names
                assert not any("/.claude/" in name for name in archive_names)
                sdist_docs = {item.name.removeprefix("scitex-1.0.0/src/"): sdist.extractfile(item).read() for item in sdist.getmembers() if item.isfile() and "/src/scitex/_sphinx_html/" in item.name}
            assert len(names) == len(set(names)) and names.count("scitex/_sphinx_html/index.html") == 1 and b"Owned normal PEP517 page" in html and wheel_docs == sdist_docs

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
