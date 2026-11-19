"""The one generated payload admitted into the umbrella release archives.

scitex-cloud serves package documentation from the installed wheel's
``scitex/_sphinx_html/`` (scitex-dev PS-121). The bundle is rendered by
``build-in-sif.sh`` AFTER the clean-source check and stays gitignored, so it is
never part of the Git-selected public source that release-identity.py binds.
It is verified here instead, on its own terms:

* the wheel carries ``index.html`` (a docs-less wheel is refused, not shipped);
* no Sphinx build cache (``.doctrees`` / ``.buildinfo``) rides along;
* every sdist member is a regular file;
* the wheel bundle and the sdist bundle are byte-identical, so the wheel built
  from the sdist cannot carry anything the sdist does not;
* a manifest digest is returned for the release proof.

The Hatch ``artifacts`` list is pinned here and compared verbatim against
pyproject.toml by release-identity.py's ``selected_paths``.
"""

import hashlib
import json
import sys
import tarfile
import zipfile
from pathlib import PurePosixPath

ARTIFACTS = [
    "src/scitex/_sphinx_html/**/*",
    "!src/scitex/_sphinx_html/.doctrees/**",
    "!src/scitex/_sphinx_html/.buildinfo",
]
SOURCE = "src/scitex/_sphinx_html/"
WHEEL = SOURCE.removeprefix("src/")
CACHES = {".doctrees", ".buildinfo"}
INDEX = "index.html"


def relative(name, prefix):
    """Bundle-relative member name; refuses an empty name or a build cache."""
    parts = PurePosixPath(name[len(prefix) :]).parts
    if not parts:
        raise ValueError("docs bundle member is unnamed")
    if CACHES & set(parts):
        raise ValueError("docs bundle carries Sphinx build caches")
    return "/".join(parts)


def wheel_bundle(archive, names):
    """Map bundle-relative names to bytes for the wheel's bundle files."""
    return {
        relative(name, WHEEL): archive.read(name)
        for name in names
        if name.startswith(WHEEL) and not name.endswith("/")
    }


def sdist_bundle(archive, members, root):
    """Map bundle-relative names to bytes for the sdist's bundle files."""
    prefix = root + "/" + SOURCE
    bundle = {}
    for item in members:
        if not item.name.startswith(prefix) or item.isdir():
            continue
        if not item.isfile():
            raise ValueError("docs bundle member is not regular")
        bundle[relative(item.name, prefix)] = archive.extractfile(item).read()
    return bundle


def identity(wheel_docs, sdist_docs):
    """Refuse a missing or diverging bundle; return its proof summary."""
    if INDEX not in wheel_docs:
        raise ValueError("wheel ships no docs bundle index")
    if wheel_docs != sdist_docs:
        raise ValueError("wheel and sdist docs bundles differ")
    manifest = [
        [name, len(body), hashlib.sha256(body).hexdigest()]
        for name, body in sorted(wheel_docs.items())
    ]
    return {
        "members": len(manifest),
        "bytes": sum(row[1] for row in manifest),
        "sha256": hashlib.sha256(json.dumps(manifest).encode()).hexdigest(),
    }


def main(argv):
    """Print the bundle identity of one built wheel and sdist, or refuse."""
    wheel_path, sdist_path = argv
    with zipfile.ZipFile(wheel_path) as wheel, tarfile.open(sdist_path) as sdist:
        members = sdist.getmembers()
        roots = {PurePosixPath(item.name).parts[0] for item in members}
        if len(roots) != 1:
            raise ValueError("sdist has multiple roots")
        summary = identity(
            wheel_bundle(wheel, wheel.namelist()),
            sdist_bundle(sdist, members, roots.pop()),
        )
    print("in-wheel docs bundle: " + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
