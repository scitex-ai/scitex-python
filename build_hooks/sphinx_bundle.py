"""Rebuild the static Sphinx bundle for each normal PEP517 target.

The release verifier repeats this producer from immutable Git source; an
archive-provided bundle or manifest is never the authority for derived bytes.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


# No notebook/plot execution, subprocesses, or outbound sockets during autodoc.
# This is a static/mock documentation build, not runtime API qualification.
SPHINX_DRIVER = '''
import sys
import platform
from pathlib import Path
# Resolve stdlib platform detection before documentation code runs.
platform.uname().processor
# Matplotlib discovers local fonts once; no plots are evaluated.
import matplotlib.font_manager
# Builtin MIME mappings suffice for static assets; ignore host /etc overlays.
import mimetypes
mimetypes.knownfiles = []
mimetypes.init()
root = Path(sys.argv.pop(1)).resolve()
allowed = (root, Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve(),
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
from sphinx.cmd.build import main
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
            "SOURCE_DATE_EPOCH": "0",
            "PYTHONHASHSEED": "0",
            "SCITEX_DOCS_STATIC": "1",
        }
        subprocess.run(
            [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + str(scratch / "pycache"),
             "-c", SPHINX_DRIVER, str(root),
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
