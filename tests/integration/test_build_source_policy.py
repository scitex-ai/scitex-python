"""Private source exclusions retain their meaning under ignored parent paths."""

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "_build_source_policy", ROOT / "build_hooks/source_policy.py"
)
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


@pytest.mark.parametrize("parent", ["var", "neutral"])
def test_private_paths_and_explicit_veto_keep_git_ignore_semantics(tmp_path, parent):
    # Arrange
    root = tmp_path / parent / "project"
    root.mkdir(parents=True)
    (root / ".gitignore").write_text(
        "var/\nGITIGNORED/\n.env\n*.ignored\n!kept.ignored\n!veto.ignored\n"
    )
    patterns = POLICY.source_excludes(root, ["veto.ignored"])
    (root / ".gitignore").write_text("\n".join(patterns) + "\n")
    env = {
        "PATH": os.defpath,
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    subprocess.run(
        ["git", "init", "--quiet", "--template=", str(root)], env=env, check=True
    )
    candidates = [
        "public.txt",
        "kept.ignored",
        "hidden.ignored",
        "veto.ignored",
        "GITIGNORED/private.txt",
        ".env",
    ]

    # Act
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "--no-index", "--stdin"],
        input="\n".join(candidates) + "\n",
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )

    # Assert
    assert set(result.stdout.splitlines()) == {
        "hidden.ignored",
        "veto.ignored",
        "GITIGNORED/private.txt",
        ".env",
    }


@pytest.mark.parametrize("kind", ["missing", "symlink"])
def test_missing_or_external_ignore_policy_is_refused(tmp_path, kind):
    # Arrange
    root = tmp_path / "project"
    root.mkdir()
    if kind == "symlink":
        outside = tmp_path / "outside-ignore"
        outside.write_text(".env\n")
        (root / ".gitignore").symlink_to(outside)

    # Act / Assert
    with pytest.raises(ValueError, match="contained regular file"):
        POLICY.source_excludes(root, [])
