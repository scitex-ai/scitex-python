"""Missing optional runtimes must leave protocol stdout empty."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

_CHILD = """
import importlib.util, sys
sys.path.insert(0, sys.argv[1])
spec = importlib.util.spec_from_file_location('owned_entrypoint', sys.argv[2])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
getattr(module, sys.argv[3])()
"""


@pytest.mark.parametrize(
    "source,operation,hint",
    [
        ("__main__.py", "main", "pip install click"),
        ("helpers/_optional_deps.py", "check_mcp_deps", "pip install mcp"),
    ],
)
def test_missing_runtime_diagnostic_does_not_corrupt_stdout(
    tmp_path, source, operation, hint
):
    # Arrange: expose the real installed logging package, with no Click/MCP.
    logging_spec = importlib.util.find_spec("scitex_logging")
    package_root = Path(next(iter(logging_spec.submodule_search_locations)))
    site = tmp_path / "site"
    site.mkdir()
    (site / "scitex_logging").symlink_to(package_root, target_is_directory=True)
    source_file = Path(__file__).resolve().parents[2] / "src/scitex" / source
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("SCITEX_")
    }
    env.update(HOME=str(tmp_path), SCITEX_DIR=str(tmp_path / "state"))
    # Act: isolated stdlib paths plus the real logging tree make absence genuine.
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            _CHILD,
            str(site),
            str(source_file),
            operation,
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    # Assert
    assert (result.returncode, result.stdout, hint in result.stderr) == (1, "", True)


def test_requested_install_guide_remains_visible_with_warning_root(tmp_path):
    # Arrange: the embedding application's diagnostic threshold is not a result filter.
    source_root = Path(__file__).resolve().parents[2] / "src"
    script = """
import logging, sys
logging.getLogger().addHandler(logging.NullHandler())
logging.getLogger().setLevel(logging.WARNING)
sys.path.insert(0, sys.argv[1])
from scitex.helpers._install_guide import show_install_guide
show_install_guide('cli')
assert logging.getLogger().level == logging.WARNING
"""
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("SCITEX_")
    }
    env.update(HOME=str(tmp_path), SCITEX_DIR=str(tmp_path / "state"))
    # Act
    result = subprocess.run(
        [sys.executable, "-B", "-c", script, str(source_root)],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    # Assert
    assert (
        result.returncode,
        "SciTeX Installation Guide" in result.stdout,
        result.stderr,
    ) == (0, True, "")
