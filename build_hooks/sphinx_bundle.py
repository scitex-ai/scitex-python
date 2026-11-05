"""Rebuild the static Sphinx bundle for each normal PEP517 target.

The release verifier repeats this producer from immutable Git source; an
archive-provided bundle or manifest is never the authority for derived bytes.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.builders.constants import EXCLUDED_DIRECTORIES


def source_candidates(root: Path, subtree: str = "") -> list[Path]:
    """Tracked lexical Git paths, or physical construction paths without Git."""
    root = root.resolve(strict=True)
    if (root / ".git").exists() or (root / ".git").is_symlink():
        env = {"PATH": os.defpath, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_OPTIONAL_LOCKS": "0"}
        top = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"], env=env, timeout=15
        ).decode().strip()
        if Path(top).resolve() != root:
            raise ValueError("documentation Git root differs")
        raw = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "--cached", "-z", "--", subtree or "."],
            env=env, timeout=15,
        )
        return sorted(root / os.fsdecode(name) for name in set(raw.split(b"\0")) if name)
    # Archive paths are construction inputs only, never external identity authority.
    paths = []
    for directory, dirs, files in os.walk(root / subtree, followlinks=False):
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
        paths.extend(Path(directory) / name for name in files)
    return sorted(paths)


def contained_regular(path: Path, root: Path) -> None:
    if (not path.resolve(strict=True).is_relative_to(root)
            or not path.is_file()
            or any(parent.is_symlink() for parent in (path, *path.parents)
                   if parent.is_relative_to(root))):
        raise ValueError("source input is not a contained regular file")


def documentation_inputs(root: Path) -> list[Path]:
    """Explicit tracked ignored docs survive normal source construction."""
    root = root.resolve(strict=True)
    source = root / "docs/sphinx"
    paths = source_candidates(root, "docs/sphinx")
    if not paths:
        raise ValueError("documentation source input inventory is empty")
    for path in paths:
        contained_regular(path, root)
        if not path.is_relative_to(source):
            raise ValueError("documentation source input escapes its source root")
    return paths


def ordinary_source_inputs(root: Path, config) -> list[Path]:
    """Use pinned Hatch selection without following directory aliases."""
    root = root.resolve(strict=True)
    selected = []
    for path in source_candidates(root):
        # Native Hatch retains deliberate literal links; external proof validates them.
        if path.is_symlink() or path.is_dir():
            continue
        contained_regular(path, root)
        relative = path.relative_to(root)
        if any(parent.name in EXCLUDED_DIRECTORIES or config.directory_is_excluded(
                parent.name, parent.parent.as_posix() if parent.parent != Path(".") else "")
               for parent in relative.parents if parent != Path(".")):
            continue
        if config.include_path(relative.as_posix(), is_package=(path.parent / "__init__.py").is_file()):
            selected.append(path)
    return selected


# No notebook/plot execution, subprocesses, or outbound sockets during autodoc.
# This is a static/mock documentation build, not runtime API qualification.
SPHINX_DRIVER = '''
import sys
import json
import os
import platform
from pathlib import Path
# PEP517 may install declared dependencies in an overlay outside sys.prefix.
# Restore its package directories without forwarding cwd or raw PYTHONPATH.
runtime_paths = tuple(Path(path) for path in json.loads(sys.argv.pop(1)))
sys.path[:0] = [str(path) for path in runtime_paths]
# Wheel data files use the installation prefix, not site-packages. Jupyter's
# template discovery otherwise checks the bare caller venv instead of overlays.
runtime_data_paths = tuple(
    (path.parents[2] / "share/jupyter").resolve()
    for path in runtime_paths if (path.parents[2] / "share/jupyter").is_dir()
)
os.environ["JUPYTER_PATH"] = os.pathsep.join(str(path) for path in runtime_data_paths)
# Resolve stdlib platform detection before documentation code runs.
platform.uname().processor
# Matplotlib discovers local fonts once; no plots are evaluated.
import matplotlib.font_manager
# Builtin MIME mappings suffice for static assets; ignore host /etc overlays.
import mimetypes
mimetypes.knownfiles = []
mimetypes.init()
# Initialize the trusted toolchain (including Babel's local-zone lookup) before
# guarding project configuration and autodoc. No project has been loaded yet.
from sphinx.cmd.build import main
# Pandas initializes these two fixed UTC aliases through dateutil separately
# from Babel/ZoneInfo. Keep their read-only timezone bootstrap outside autodoc.
from dateutil.tz import gettz
utc_timezones = tuple(gettz(name) for name in ("UTC", "Etc/UTC"))
root = Path(sys.argv.pop(1)).resolve()
allowed = (root, Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve(),
           *runtime_paths, *runtime_data_paths,
           Path(__import__("os").environ["HOME"]).parent.resolve())
class RefusedOperation(BaseException):
    pass

def deny_effects(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system", "os.posix_spawn"}:
        raise RefusedOperation("documentation build refuses " + event)
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = Path(__import__("os").fsdecode(args[0])).resolve()
        flags = args[2]
        writing = flags & (__import__("os").O_WRONLY | __import__("os").O_RDWR | __import__("os").O_CREAT | __import__("os").O_TRUNC)
        private = allowed[-1]
        if writing and path != Path("/dev/null") and not path.is_relative_to(private):
            raise RefusedOperation("documentation build refuses non-private writes")
        runtime_cpu = path.is_relative_to(Path("/sys/fs/cgroup"))
        if path != Path("/dev/null") and not runtime_cpu and not any(path.is_relative_to(base) for base in allowed):
            raise RefusedOperation("documentation build refuses out-of-tree file access: " + str(path))
sys.addaudithook(deny_effects)
result = main(sys.argv[1:])
raise SystemExit(result)
'''


def build_bundle(root: Path, output: Path) -> None:
    """Produce HTML in a new private directory, refusing preexisting payload."""
    root = root.resolve(strict=True)
    if output.exists() or output.is_symlink():
        raise ValueError("documentation output must be absent")
    with tempfile.TemporaryDirectory(prefix="scitex-sphinx-") as temporary:
        scratch = Path(temporary)
        env = {
            "PATH": os.defpath,
            "HOME": str(scratch / "home"),
            "TMPDIR": str(scratch),
            "XDG_CACHE_HOME": str(scratch / "cache"),
            "MPLCONFIGDIR": str(scratch / "matplotlib"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
            "SOURCE_DATE_EPOCH": "0",
            "PYTHONHASHSEED": "0",
            "SCITEX_DOCS_STATIC": "1",
        }
        subprocess.run(
            [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + str(scratch / "pycache"),
             "-c", SPHINX_DRIVER, json.dumps([
                 str(Path(path).resolve()) for path in sys.path
                 if path and Path(path).name in {"site-packages", "dist-packages"}
             ]), str(root),
             "-E", "-a", "-b", "html", "-d", str(scratch / "doctrees"),
             str(root / "docs/sphinx"), str(scratch / "html")],
            cwd=root, env=env, check=True,
        )
        # .buildinfo is an incremental-builder cache, not served content.
        (scratch / "html/.buildinfo").unlink(missing_ok=True)
        if not (scratch / "html/index.html").is_file():
            raise ValueError("Sphinx did not produce its real index")
        for path in (scratch / "html").rglob("*"):
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ValueError("unsafe generated documentation member")
        shutil.copytree(scratch / "html", output)


class CustomBuildHook(BuildHookInterface):
    """Rebuild even from an sdist; never accept the sdist's copied HTML."""

    def initialize(self, version, build_data):
        if self.config.get("source-input-root") != "docs/sphinx":
            raise ValueError("reviewed documentation source root differs")
        self._temporary = tempfile.TemporaryDirectory(prefix="scitex-doc-bundle-")
        output = Path(self._temporary.name) / "html"
        build_bundle(Path(self.root), output)
        destination = (
            "scitex/_sphinx_html" if self.target_name == "wheel"
            else "src/scitex/_sphinx_html"
        )
        # Hatch reserves destinations for forced FILES, not external
        # directories. This overrides copied sdist HTML without duplicate ZIP
        # entries, while still deriving every member from this fresh build.
        targets = set(build_data["force_include"].values())
        if self.target_name == "sdist":
            # Reserve selected regular files before native safe_walk can lose a
            # directory inode through an earlier ignored symlink alias.
            source_files = set(ordinary_source_inputs(Path(self.root), self.build_config))
            source_files.update(documentation_inputs(Path(self.root)))
            for path in sorted(source_files):
                target = path.relative_to(Path(self.root).resolve()).as_posix()
                if target in targets:
                    same = any(Path(source).resolve() == path.resolve() and value == target
                               for source, value in build_data["force_include"].items())
                    if not same:
                        raise ValueError("documentation source target collision")
                    continue
                targets.add(target)
                build_data["force_include"][str(path)] = target
        for path in sorted(output.rglob("*")):
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ValueError("unsafe generated documentation member")
            if path.is_file():
                target = destination + "/" + path.relative_to(output).as_posix()
                if target in targets:
                    raise ValueError("generated documentation target collision")
                targets.add(target)
                build_data["force_include"][str(path)] = target

    def finalize(self, version, build_data, artifact_path):
        self._temporary.cleanup()
