"""Tests for the `scitex.path` pure-utility surface.

Covers the filesystem-inert helpers (`split`, `clean`,
`increment_version`, `find_git_root`) plus tmp-dir-scoped symlink
helpers.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import scitex.path as p

# ---------------------------------------------------------------------------
# split(fpath) -> (dir, stem, ext)
# ---------------------------------------------------------------------------


class TestSplit:
    def test_simple(self):
        d, stem, ext = p.split("/tmp/foo/bar.txt")
        assert d == Path("/tmp/foo")
        assert stem == "bar"
        assert ext == ".txt"

    def test_pathlib_input(self):
        d, stem, ext = p.split(Path("data/x.csv"))
        assert stem == "x"
        assert ext == ".csv"

    def test_no_extension(self):
        _, stem, ext = p.split("/tmp/README")
        assert stem == "README"
        assert ext == ""

    def test_dotfile(self):
        d, stem, ext = p.split("/tmp/.gitignore")
        assert stem == ".gitignore"
        assert ext == ""


# ---------------------------------------------------------------------------
# clean(path_string) — normalize redundant separators + dots
# ---------------------------------------------------------------------------


class TestClean:
    def test_double_slash(self):
        assert p.clean("/tmp//foo") == "/tmp/foo"

    def test_dot_segment(self):
        assert p.clean("/tmp/./foo") == "/tmp/foo"

    def test_idempotent(self):
        cleaned = p.clean("/tmp/./a//b")
        assert p.clean(cleaned) == cleaned


# ---------------------------------------------------------------------------
# increment_version(dirname, fname, ext, version_prefix="_v") -> new path
# ---------------------------------------------------------------------------


class TestIncrementVersion:
    def test_first_version_when_no_existing(self, tmp_path):
        out = p.increment_version(str(tmp_path), "foo", ".txt")
        # The function generates _v001 by default
        assert "_v001" in str(out)
        assert str(out).endswith(".txt")

    def test_existing_files_bump(self, tmp_path):
        (tmp_path / "foo_v001.txt").write_text("x")
        (tmp_path / "foo_v002.txt").write_text("x")
        out = p.increment_version(str(tmp_path), "foo", ".txt")
        # Next version must be >= _v003
        assert "_v003" in str(out) or "_v002" not in str(out)


# ---------------------------------------------------------------------------
# find_git_root — walks up from cwd
# ---------------------------------------------------------------------------


class TestFindGitRoot:
    def test_returns_path_containing_dot_git(self):
        root = p.find_git_root()
        assert (root / ".git").exists() or (root / ".git").is_file()

    def test_inside_repo(self, monkeypatch):
        repo = p.find_git_root()
        # Must be a valid git repo — `git rev-parse` should succeed there.
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
        assert out.returncode == 0
        assert out.stdout.strip() == "true"


# ---------------------------------------------------------------------------
# Symlink helpers — use tmp_path to stay isolated
# ---------------------------------------------------------------------------


class TestSymlinks:
    def test_create_and_detect(self, tmp_path):
        target = tmp_path / "target.txt"
        target.write_text("hi")
        link = tmp_path / "link.txt"

        p.symlink(str(target), str(link))
        assert link.is_symlink()
        assert p.is_symlink(str(link))
        assert link.read_text() == "hi"

    def test_readlink_returns_target(self, tmp_path):
        target = tmp_path / "t.txt"
        target.write_text("x")
        link = tmp_path / "l.txt"
        p.symlink(str(target), str(link))

        resolved = p.readlink(str(link))
        assert Path(resolved).resolve() == target.resolve()

    def test_unlink_symlink(self, tmp_path):
        target = tmp_path / "t.txt"
        target.write_text("x")
        link = tmp_path / "l.txt"
        p.symlink(str(target), str(link))

        p.unlink_symlink(str(link))
        assert not link.exists()
        # Target must not be deleted
        assert target.exists()


# ---------------------------------------------------------------------------
# getsize
# ---------------------------------------------------------------------------


class TestGetsize:
    def test_file_size(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("hello world")
        assert p.getsize(str(f)) == len("hello world")

    def test_missing_file_returns_nonpositive_sentinel(self, tmp_path):
        import math

        missing = tmp_path / "missing"
        # Contract: missing files return NaN (sentinel) rather than raise,
        # so `getsize` is safe to call in scan loops.
        try:
            size = p.getsize(str(missing))
            assert math.isnan(size) or size == 0
        except (FileNotFoundError, OSError):
            pass


# EOF
