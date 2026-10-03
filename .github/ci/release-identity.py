#!/usr/bin/env python3
"""Bind a SciTeX release to one tag, source commit and two verified artifacts."""

import argparse
import base64
import configparser
import csv
import hashlib
import io
import json
import os
import posixpath
import re
import select
import signal
import stat
import subprocess
import tarfile
import tempfile
import time
import tomllib
import urllib.request
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath

REPOSITORY = "scitex-ai/scitex-python"
TAG = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
SHA = re.compile(r"[0-9a-f]{40}")
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
PROOF = "release-proof.json"
SIF_SHA256 = "aa5836a6c317640d7e20f01eb79aa7385b3dca2f369b595065c50ba3dd34a7d5"


def api(path, status=200, *, open_url=urllib.request.urlopen):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with open_url(request, timeout=10) as response:
        if response.status != status:
            raise ValueError("GitHub identity response did not match")
        if status == 204:
            return {"status": 204}
        body = response.read(1048577)
        if len(body) > 1048576:
            raise ValueError("GitHub identity response too large")
        return json.loads(body)


def member_admission(query=api):
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise ValueError("release repository does not match")
    actors = {
        os.environ.get("GITHUB_ACTOR", ""),
        os.environ.get("GITHUB_TRIGGERING_ACTOR", ""),
    }
    if not actors or any(not LOGIN.fullmatch(actor) for actor in actors):
        raise ValueError("release actor is missing or malformed")
    for actor in actors:
        if query("orgs/scitex-ai/public_members/" + actor, status=204) != {
            "status": 204
        }:
            raise ValueError("organization membership is not confirmed")


def resolve(tag, query=api):
    if not TAG.fullmatch(tag):
        raise ValueError("release requires an existing vX.Y.Z tag")
    prefix = "repos/" + REPOSITORY
    ref = query(prefix + "/git/ref/tags/" + tag)
    if ref.get("ref") != "refs/tags/" + tag:
        raise ValueError("returned tag ref differs")
    item = ref["object"]
    seen = set()
    for _ in range(5):
        digest = item.get("sha", "")
        if not SHA.fullmatch(digest) or digest in seen:
            raise ValueError("invalid or cyclic tag object")
        seen.add(digest)
        if item.get("type") == "commit":
            break
        if item.get("type") != "tag":
            raise ValueError("tag does not resolve to a commit")
        item = query(prefix + "/git/tags/" + digest)["object"]
    else:
        raise ValueError("tag annotation depth exceeded")
    commit = item["sha"]
    comparison = query(prefix + "/compare/" + commit + "...main")
    if comparison.get("base_commit", {}).get("sha") != commit or comparison.get(
        "status"
    ) not in {"ahead", "identical"}:
        raise ValueError("release source has not been promoted to main")
    content = query(prefix + "/contents/pyproject.toml?ref=" + commit)
    if content.get("encoding") != "base64":
        raise ValueError("unsupported metadata encoding")
    raw = base64.b64decode(content["content"].replace("\n", ""), validate=True)
    if len(raw) > 131072 or hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw
    ).hexdigest() != content.get("sha"):
        raise ValueError("release metadata Git identity differs")
    project = tomllib.loads(raw.decode())["project"]
    if (
        project["name"].replace("_", "-").lower() != "scitex"
        or project["version"] != tag[1:]
    ):
        raise ValueError("tag and project metadata differ")
    return {"tag": tag, "commit": commit, "version": tag[1:]}


def regular_bytes(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("artifact must be a regular file")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 268435456:
            raise ValueError("artifact type or size is invalid")
        raw = stream.read()
        after = os.fstat(stream.fileno())
    if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ) or path.lstat().st_ino != before.st_ino:
        raise ValueError("artifact changed while reading")
    return raw


def safe_member(name):
    path = PurePosixPath(name)
    if (
        "\\" in name
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in name.rstrip("/").split("/"))
    ):
        raise ValueError("unsafe archive member")


def metadata_identity(raw, version):
    message = BytesParser().parsebytes(raw)
    if message.get_all("Name") != ["scitex"]:
        raise ValueError("artifact distribution differs")
    if message.get_all("Version") != [version]:
        raise ValueError("artifact version differs")


def wheel_platform_identity(raw):
    headers = BytesParser().parsebytes(raw)
    if (
        headers.get_all("Wheel-Version") != ["1.0"]
        or headers.get_all("Root-Is-Purelib") != ["true"]
        or headers.get_all("Tag") != ["py3-none-any"]
    ):
        raise ValueError("wheel platform differs from reviewed pure Python source")


def wheel_identity(raw, version):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 20000:
            raise ValueError("duplicate or excessive wheel members")
        for item in archive.infolist():
            safe_member(item.filename)
            mode = stat.S_IFMT(item.external_attr >> 16)
            if mode not in {0, stat.S_IFREG, stat.S_IFDIR} or item.file_size > 67108864:
                raise ValueError("unsupported wheel member")
        if sum(item.file_size for item in archive.infolist()) > 1073741824:
            raise ValueError("wheel expanded size exceeded")
        metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
        records = [name for name in names if name.endswith(".dist-info/RECORD")]
        if len(metadata) != 1 or len(records) != 1:
            raise ValueError("wheel metadata identity is ambiguous")
        metadata_identity(archive.read(metadata[0]), version)
        record = records[0]
        owner = "scitex-" + version + ".dist-info"
        if metadata[0] != owner + "/METADATA" or record != owner + "/RECORD":
            raise ValueError("wheel metadata and RECORD owners differ")
        if owner + "/WHEEL" not in names:
            raise ValueError("wheel platform metadata is missing")
        wheel_platform_identity(archive.read(owner + "/WHEEL"))
        seen = set()
        for name, digest, size in csv.reader(
            io.StringIO(archive.read(record).decode())
        ):
            if name in seen or name not in names:
                raise ValueError("wheel RECORD membership differs")
            seen.add(name)
            if name == record:
                if digest or size:
                    raise ValueError("wheel RECORD self entry differs")
                continue
            body = archive.read(name)
            expected = "sha256=" + base64.urlsafe_b64encode(
                hashlib.sha256(body).digest()
            ).decode().rstrip("=")
            if digest != expected or size != str(len(body)):
                raise ValueError("wheel RECORD hash or size differs")
        if seen != set(names):
            raise ValueError("wheel has unrecorded members")
        if not {
            "scitex/__init__.py",
            "scitex/cli/__init__.py",
            "scitex/__version__.py",
        }.issubset(names):
            raise ValueError("wheel lost required public payload")
        return {"members": len(names), "record_members": len(seen)}


def sdist_identity(raw, version):
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        entries = archive.getmembers()
        names = [item.name for item in entries]
        if len(names) != len(set(names)) or len(names) > 20000:
            raise ValueError("duplicate or excessive sdist members")
        for item in entries:
            safe_member(item.name)
            if (
                not (item.isfile() or item.isdir() or item.issym())
                or item.size > 67108864
            ):
                raise ValueError("unsupported sdist member")
            if item.issym():
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(item.name), item.linkname)
                )
                if (
                    item.linkname.startswith("/")
                    or "\\" in item.linkname
                    or not target.startswith(item.name.split("/", 1)[0] + "/")
                ):
                    raise ValueError("sdist link escapes its source root")
                relative = item.name.split("/", 1)[1]
                if PUBLIC_LINKS.get(relative) != item.linkname:
                    raise ValueError("unreviewed sdist literal link")
        if sum(item.size for item in entries) > 1073741824:
            raise ValueError("sdist expanded size exceeded")
        roots = {PurePosixPath(name).parts[0] for name in names}
        if len(roots) != 1:
            raise ValueError("sdist has multiple roots")
        root = next(iter(roots))
        required = {
            root + "/src/scitex/__init__.py",
            root + "/src/scitex/cli/__init__.py",
            root + "/src/scitex/__version__.py",
            root + "/PKG-INFO",
            root + "/pyproject.toml",
        }
        if not required.issubset(names) or any(
            not archive.getmember(name).isfile() for name in required
        ):
            raise ValueError("sdist lost required public payload")
        metadata_identity(archive.extractfile(root + "/PKG-INFO").read(), version)
        project = tomllib.loads(
            archive.extractfile(root + "/pyproject.toml").read().decode()
        )["project"]
        if (
            project["version"] != version
            or project["name"].replace("_", "-").lower() != "scitex"
        ):
            raise ValueError("sdist project identity differs")
        return {"members": len(entries)}


def git_read(argv, source_root, stdin=None):
    process = subprocess.Popen(
        ["git", "-C", str(source_root), *argv],
        stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, _ = process.communicate(stdin, timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise ValueError("public source read timed out") from None
    if process.returncode:
        raise ValueError("public source Git read failed")
    return stdout


# Public selection is evaluated by Git's own ignore engine in an isolated
# metadata-only repository. The reviewed ignore bytes and Hatch default target
# shape are fixed; no caller global/info/nested ignores or filesystem walks.
IGNORE_SHA256 = "83fbffa2f6bb7b4df285d6381e114ffb3ccff7075610d48dcf3e7caa1bb39663"
EXCLUDES = [
    "src/scitex/scholar/.env",
    "src/scitex/scholar/.venv",
    "src/scitex/scholar/.claude",
    "src/scitex/scholar/crossref_local",
    "src/scitex/scholar/library",
    "src/scitex/scholar/docs/to_claude",
    "src/scitex/scholar/data/impact_factor/impact_factor.db",
]
SKIP_DIRS = {
    "__pycache__",
    ".venv",
    ".git",
    ".hg",
    ".hatch",
    ".tox",
    ".nox",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".pixi",
}
PUBLIC_LINKS = {
    ("docs/assets/logos/scitex-logo.svg"): (
        "logo_files/svg/Color logo - no background.svg"
    ),
    ("examples/_legacy/msword/IOP-SCIENCE-Word-template-Double-anonymous.docx"): (
        "../../docs/MSWORD_MANUSCTIPS/IOP-SCIENCE-Word-template-Double-anonymous.docx"
    ),
    ("examples/_legacy/msword/RESNA 2025 Scientific Paper Template.docx"): (
        "../../docs/MSWORD_MANUSCTIPS/RESNA 2025 Scientific Paper Template.docx"
    ),
    ("examples/_legacy/msword/ijerph-template.dot"): (
        "../../docs/MSWORD_MANUSCTIPS/ijerph-template.dot"
    ),
    ("examples/_legacy/scitex/plt/pltz.py"): ("../io/bundle/pltz.py"),
    (
        "examples/_legacy/scitex/session/docs/to_claude/examples/example-e"
        "lisp-project-emacs-hello-world/LATEST-ELISP-REPORT.org"
    ): ("ELISP-TEST-REPORT-20250513-012234-48-PASSED-49-TOTAL-97-PERCENT.org"),
    ("examples/_legacy/stats/statsz.py"): ("../scitex/io/bundle/statsz.py"),
}


def git_tree(commit, source_root):
    if not SHA.fullmatch(commit):
        raise ValueError("public source commit is malformed")
    entries = {}
    raw = git_read(["ls-tree", "-r", "-z", "-l", "--full-tree", commit], source_root)
    if len(raw) > 8388608:
        raise ValueError("public source metadata exceeds bounds")
    for row in filter(None, raw.split(b"\0")):
        frame, name = row.split(b"\t", 1)
        mode, kind, oid, size = frame.decode().split()
        name = name.decode()
        safe_member(name)
        if (
            name in entries
            or not SHA.fullmatch(oid)
            or (kind, mode)
            not in {
                ("blob", "100644"),
                ("blob", "100755"),
                ("blob", "120000"),
                ("commit", "160000"),
            }
        ):
            raise ValueError("public source tree is ambiguous")
        entries[name] = (mode, oid, None if size == "-" else int(size))
    if len(entries) > 20000:
        raise ValueError("public source inventory exceeds bounds")
    return entries


def selected_paths(entries, project, ignore_raw):
    build = project.get("tool", {}).get("hatch", {}).get("build", {})
    if build != {
        "targets": {"wheel": {"exclude": EXCLUDES}, "sdist": {"exclude": EXCLUDES}}
    }:
        raise ValueError("reviewed umbrella Hatch mapping changed")
    if hashlib.sha256(ignore_raw).hexdigest() != IGNORE_SHA256:
        raise ValueError("reviewed umbrella ignore selection changed")
    with tempfile.TemporaryDirectory(prefix="scitex-release-selector-") as temporary:
        root = Path(temporary)
        git_read(["init", "--quiet", "--template=", str(root)], Path("."))
        (root / ".gitignore").write_bytes(
            ignore_raw + b"\n*.py[cdo]\n/dist\n" + "\n".join(EXCLUDES).encode() + b"\n"
        )
        request = b"".join(name.encode() + b"\0" for name in entries)
        # check-ignore returns1 when no input is excluded, which is valid.
        process = subprocess.Popen(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "core.excludesFile=/dev/null",
                "check-ignore",
                "--no-index",
                "-z",
                "--stdin",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            output, _ = process.communicate(request, timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise ValueError("public selection timed out") from None
        if process.returncode not in {0, 1}:
            raise ValueError("public selection failed")
        excluded = set(filter(None, output.decode().split("\0")))
    selected = {
        name
        for name, row in entries.items()
        if row[0] != "160000"
        and name not in excluded
        and PurePosixPath(name).name != ".DS_Store"
        and not (set(PurePosixPath(name).parts[:-1]) & SKIP_DIRS)
    }
    wheel = {
        name.removeprefix("src/"): name
        for name in selected
        if name.startswith("src/scitex/")
    }
    if not wheel or any(
        entries[path][0] not in {"100644", "100755"} for path in wheel.values()
    ):
        raise ValueError("unsupported public wheel payload")
    if sum(entries[name][2] for name in selected) > 268435456:
        raise ValueError("selected source inventory exceeds bounds")
    return wheel, selected


class GitBodies:
    """One selected-object stream, never preloading unrelated repository bytes."""

    def __init__(self, source_root):
        self.process = subprocess.Popen(
            ["git", "-C", str(source_root), "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            bufsize=0,
        )
        self.pending = b""
        self.deadline = time.monotonic() + 60

    def read(self, length, line=False):
        while b"\n" not in self.pending if line else len(self.pending) < length:
            remaining = self.deadline - time.monotonic()
            if (
                remaining <= 0
                or not select.select([self.process.stdout], [], [], remaining)[0]
            ):
                raise ValueError("selected Git payload deadline exceeded")
            block = os.read(self.process.stdout.fileno(), 65536)
            if not block or (line and len(self.pending) > 256):
                raise ValueError("selected Git payload frame truncated")
            self.pending += block
        end = self.pending.index(b"\n") + 1 if line else length
        result, self.pending = self.pending[:end], self.pending[end:]
        return result

    def body(self, row):
        _, oid, size = row
        if size is None or size > 67108864:
            raise ValueError("selected public blob size is invalid")
        self.process.stdin.write((oid + "\n").encode())
        header = self.read(0, line=True).decode().strip().split()
        if header != [oid, "blob", str(size)]:
            raise ValueError("selected Git payload frame differs")
        body = self.read(size)
        if (
            self.read(1) != b"\n"
            or hashlib.sha1(b"blob " + str(size).encode() + b"\0" + body).hexdigest()
            != oid
        ):
            raise ValueError("selected Git payload bytes differ")
        return body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGKILL)
            self.process.wait()
        self.process.stdout.close()


def normalized_name(value):
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?", value):
        raise ValueError("unsupported dependency name")
    return re.sub(r"[-_.]+", "-", value).lower()


def specifier_identity(value):
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    if not value:
        return ()
    parts = [part.strip().lower() for part in value.split(",")]
    if any(
        not re.fullmatch(r"(?:===|==|!=|~=|<=|>=|<|>)\s*[a-z0-9.*+!_-]+", part)
        for part in parts
    ):
        raise ValueError("unsupported dependency version constraint")
    return tuple(sorted({re.sub(r"\s+", "", part) for part in parts}))


def marker_identity(value):
    if not value:
        return ()
    token = re.compile(
        r"""\s*("[^"\\]*"|'[^'\\]*'|===|==|!=|~=|<=|>=|[<>()]|[A-Za-z_][A-Za-z0-9_]*)"""
    )
    tokens = []
    position = 0
    while position < len(value):
        match = token.match(value, position)
        if not match:
            if value[position:].strip():
                raise ValueError("unsupported dependency marker")
            break
        tokens.append(match[1])
        position = match.end()
    if len(tokens) > 128:
        raise ValueError("dependency marker is excessive")
    position = 0
    variables = {
        "python_version",
        "python_full_version",
        "os_name",
        "sys_platform",
        "platform_release",
        "platform_system",
        "platform_version",
        "platform_machine",
        "platform_python_implementation",
        "implementation_name",
        "implementation_version",
        "extra",
    }

    def operand():
        nonlocal position
        if position >= len(tokens):
            raise ValueError("incomplete dependency marker")
        item = tokens[position]
        position += 1
        if item[:1] in {"'", '"'}:
            return ("literal", item[1:-1])
        if item not in variables:
            raise ValueError("unknown dependency marker variable")
        return ("variable", item)

    def atom(depth):
        nonlocal position
        if depth > 16 or position >= len(tokens):
            raise ValueError("incomplete dependency marker")
        if tokens[position] == "(":
            position += 1
            result = expression(depth + 1)
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError("unclosed dependency marker")
            position += 1
            return result
        left = operand()
        if position >= len(tokens):
            raise ValueError("incomplete dependency marker")
        operator = tokens[position]
        position += 1
        if operator == "not":
            if position >= len(tokens) or tokens[position] != "in":
                raise ValueError("unsupported dependency marker operator")
            position += 1
            operator = "not in"
        if operator not in {
            "===",
            "==",
            "!=",
            "~=",
            "<=",
            ">=",
            "<",
            ">",
            "in",
            "not in",
        }:
            raise ValueError("unsupported dependency marker operator")
        right = operand()
        if left == ("variable", "extra") and right[0] == "literal":
            right = ("literal", normalized_name(right[1]))
        if right == ("variable", "extra") and left[0] == "literal":
            left = ("literal", normalized_name(left[1]))
        return ("compare", left, operator, right)

    def combine(operator, values):
        flat = []
        for item in values:
            flat.extend(item[1:] if item[0] == operator else [item])
        return flat[0] if len(flat) == 1 else (operator, *sorted(set(flat)))

    def conjunction(depth):
        nonlocal position
        values = [atom(depth)]
        while position < len(tokens) and tokens[position] == "and":
            position += 1
            values.append(atom(depth))
        return combine("and", values)

    def expression(depth):
        nonlocal position
        values = [conjunction(depth)]
        while position < len(tokens) and tokens[position] == "or":
            position += 1
            values.append(conjunction(depth))
        return combine("or", values)

    result = expression(0)
    if position != len(tokens):
        raise ValueError("unsupported dependency marker suffix")
    return result


def requirement_identity(value):
    requirement, separator, marker = value.partition(";")
    match = re.fullmatch(
        r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)(?:\[([^]]+)\])?\s*(.*?)\s*", requirement
    )
    if not match or "@" in requirement:
        raise ValueError("unsupported dependency requirement")
    extras = tuple(
        sorted(
            {
                normalized_name(x.strip())
                for x in (match[2] or "").split(",")
                if x.strip()
            }
        )
    )
    return (
        normalized_name(match[1]),
        extras,
        specifier_identity(match[3]),
        marker_identity(marker if separator else ""),
    )


def declared_metadata(project):
    """Follow the reviewed Hatch static metadata and recursive-extra contract."""
    if project.get("dynamic"):
        raise ValueError("dynamic release metadata is not qualified")
    core = {requirement_identity(value) for value in project.get("dependencies", [])}
    groups = {}
    inherited = {}
    for name, requirements in project.get("optional-dependencies", {}).items():
        name = normalized_name(name)
        if name in groups:
            raise ValueError("ambiguous source extra")
        groups[name] = set()
        inherited[name] = set()
        for value in requirements:
            row = requirement_identity(value)
            if row[0] == normalized_name(project["name"]):
                if row[2] or row[3]:
                    raise ValueError("conditional self-extra is not qualified")
                inherited[name].update(row[1])
            else:
                groups[name].add(row)
    resolved = set()

    def resolve_group(name, active):
        if name not in groups or name in active:
            raise ValueError("unknown or cyclic source extra")
        if name not in resolved:
            for child in inherited[name]:
                resolve_group(child, active | {name})
                groups[name].update(groups[child])
            resolved.add(name)

    for name in groups:
        resolve_group(name, set())
    expected = set(core)
    for extra, requirements in groups.items():
        extra_marker = marker_identity("extra == '" + extra + "'")
        for name, extras, specifier, marker in requirements:
            if marker:
                parts = list(marker[1:]) if marker[0] == "and" else [marker]
                marker = ("and", *sorted(set([*parts, extra_marker])))
            else:
                marker = extra_marker
            expected.add((name, extras, specifier, marker))
    entries = {
        group: dict(values) for group, values in project.get("entry-points", {}).items()
    }
    for key, group in (("scripts", "console_scripts"), ("gui-scripts", "gui_scripts")):
        if project.get(key):
            if group in entries:
                raise ValueError("ambiguous source entry-point group")
            entries[group] = dict(project[key])
    return {
        "requires_python": specifier_identity(project.get("requires-python", "")),
        "extras": set(groups),
        "requirements": expected,
        "entries": entries,
    }


def metadata_source_identity(wheel_raw, sdist_raw, entry_points, project):
    expected = declared_metadata(project)
    for raw in (wheel_raw, sdist_raw):
        headers = BytesParser().parsebytes(raw)
        if headers.get_all("License-File") != ["LICENSE"]:
            raise ValueError("source License-File declaration differs")
        if headers.get_all("Metadata-Version") not in [
            [x] for x in ("2.1", "2.2", "2.3", "2.4")
        ]:
            raise ValueError("unsupported generated metadata version")
        python = headers.get_all("Requires-Python", [])
        if len(python) != (1 if expected["requires_python"] else 0) or (
            python and specifier_identity(python[0]) != expected["requires_python"]
        ):
            raise ValueError("source Requires-Python differs")
        extras = headers.get_all("Provides-Extra", [])
        normalized_extras = {normalized_name(x) for x in extras}
        if (
            len(extras) != len(normalized_extras)
            or normalized_extras != expected["extras"]
        ):
            raise ValueError("source extras differ")
        requirements = [
            requirement_identity(x) for x in headers.get_all("Requires-Dist", [])
        ]
        if (
            len(requirements) != len(set(requirements))
            or set(requirements) != expected["requirements"]
        ):
            raise ValueError("source runtime requirements differ")
        if headers.get_all("Dynamic"):
            raise ValueError("dynamic artifact metadata is not qualified")
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try:
        parser.read_string(
            entry_points.decode("utf-8") if entry_points is not None else ""
        )
    except (UnicodeDecodeError, configparser.Error) as error:
        raise ValueError("invalid entry-point metadata") from error
    actual = {name: dict(parser.items(name, raw=True)) for name in parser.sections()}
    if parser.defaults() or actual != expected["entries"]:
        raise ValueError("source entry points differ")
    return {
        "runtime_requirements": len(expected["requirements"]),
        "extras": len(expected["extras"]),
        "entry_point_groups": len(expected["entries"]),
    }


def source_payload_identity(wheel_raw, sdist_raw, commit, source_root=Path(".")):
    entries = git_tree(commit, source_root)
    if not {"pyproject.toml", ".gitignore", "LICENSE"}.issubset(entries):
        raise ValueError("public selection authority is missing")
    if any(
        entries[name][0] not in {"100644", "100755"}
        for name in ("pyproject.toml", ".gitignore", "LICENSE")
    ):
        raise ValueError("public selection authority is not regular")
    manifest = []
    with GitBodies(source_root) as git:
        project = tomllib.loads(git.body(entries["pyproject.toml"]).decode())
        wheel_expected, sdist_expected = selected_paths(
            entries, project, git.body(entries[".gitignore"])
        )
        with (
            zipfile.ZipFile(io.BytesIO(wheel_raw)) as wheel,
            tarfile.open(fileobj=io.BytesIO(sdist_raw), mode="r:gz") as sdist,
        ):
            names = wheel.namelist()
            actual = {
                name
                for name in names
                if name.startswith("scitex/") and not name.endswith("/")
            }
            if actual != set(wheel_expected):
                raise ValueError("whole wheel public source membership differs")
            owner = "scitex-" + project["project"]["version"] + ".dist-info/"
            generated = {
                owner + name
                for name in ("METADATA", "WHEEL", "RECORD", "entry_points.txt")
            }
            generated.add(owner + "licenses/LICENSE")
            if owner + "WHEEL" not in names:
                raise ValueError("wheel platform metadata is missing")
            wheel_platform_identity(wheel.read(owner + "WHEEL"))
            if owner + "licenses/LICENSE" not in names:
                raise ValueError("wheel license payload is missing")
            directories = {
                str(parent) + "/"
                for name in generated | actual
                for parent in PurePosixPath(name).parents
                if str(parent) != "."
            }
            if any(
                name not in generated and name not in actual and name not in directories
                for name in names
            ):
                raise ValueError("wheel contains undeclared payload")
            root_name = "scitex-" + project["project"]["version"]
            metadata_summary = metadata_source_identity(
                wheel.read(owner + "METADATA"),
                sdist.extractfile(root_name + "/PKG-INFO").read(),
                wheel.read(owner + "entry_points.txt")
                if owner + "entry_points.txt" in names
                else None,
                project["project"],
            )
            roots = {PurePosixPath(item.name).parts[0] for item in sdist.getmembers()}
            if len(roots) != 1 or roots != {"scitex-" + project["project"]["version"]}:
                raise ValueError("sdist source root differs")
            root = next(iter(roots))
            allowed_directories = {root} | {
                root + "/" + str(parent)
                for name in sdist_expected | {"PKG-INFO"}
                for parent in PurePosixPath(name).parents
                if str(parent) != "."
            }
            if any(
                item.name.rstrip("/") not in allowed_directories
                for item in sdist.getmembers()
                if item.isdir()
            ):
                raise ValueError("sdist contains undeclared directory")
            members = {
                item.name.removeprefix(root + "/"): item
                for item in sdist.getmembers()
                if not item.isdir() and item.name != root + "/PKG-INFO"
            }
            if set(members) != sdist_expected:
                raise ValueError("whole sdist public source membership differs")
            for name in sorted(sdist_expected):
                row = entries[name]
                body = git.body(row)
                item = members[name]
                if row[0] == "120000":
                    if (
                        not item.issym()
                        or PUBLIC_LINKS.get(name) != body.decode()
                        or item.linkname.encode() != body
                    ):
                        raise ValueError("sdist public link identity differs")
                elif not item.isfile() or sdist.extractfile(item).read() != body:
                    raise ValueError("sdist public source bytes differ")
                destination = name.removeprefix("src/")
                if destination in wheel_expected and wheel.read(destination) != body:
                    raise ValueError("wheel public source bytes differ")
                if (
                    name == "LICENSE"
                    and wheel.read(owner + "licenses/LICENSE") != body
                ):
                    raise ValueError("wheel license bytes differ")
                manifest.append(
                    {
                        "path": name,
                        "mode": row[0],
                        "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(),
                    }
                )
    return {
        "git_commit": commit,
        "metadata_source": metadata_summary,
        "wheel_public_members": len(wheel_expected),
        "sdist_public_members": len(sdist_expected),
        "source_membership_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest(),
    }


def check_source_layout(commit, source_root=Path(".")):
    """Refuse dirty/unowned traversal before the backend reads source files."""
    source_root = source_root.absolute()
    entries = git_tree(commit, source_root)
    if git_read(["rev-parse", "HEAD"], source_root).decode().strip() != commit:
        raise ValueError("checkout and release commit differ")
    if git_read(
        ["status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching"],
        source_root,
    ):
        raise ValueError("release source checkout is dirty")
    with GitBodies(source_root) as git:
        project = tomllib.loads(git.body(entries["pyproject.toml"]).decode())
        _, selected = selected_paths(entries, project, git.body(entries[".gitignore"]))
        for name in selected | {
            name for name, row in entries.items() if row[0] == "160000"
        }:
            path = source_root / name
            mode = entries[name][0]
            if mode == "160000" and not path.exists() and not path.is_symlink():
                continue
            for parent in path.parents:
                if parent == source_root.parent:
                    break
                if not stat.S_ISDIR(parent.lstat().st_mode):
                    raise ValueError("source ancestor link refused")
            if mode == "160000":
                if path.is_symlink() or (
                    path.exists() and (not path.is_dir() or any(path.iterdir()))
                ):
                    raise ValueError("unowned gitlink subtree refused")
            elif mode == "120000":
                if not path.is_symlink() or os.readlink(path).encode() != git.body(
                    entries[name]
                ):
                    raise ValueError("source literal link differs")
            elif not stat.S_ISREG(path.lstat().st_mode):
                raise ValueError("source payload is not regular")


def artifact_proof(directory, tag, commit, run, attempt, source_root=Path(".")):
    if os.environ.get("SCITEX_CI_SIF_SHA256") != SIF_SHA256:
        raise ValueError("release image configuration differs")
    if (
        not TAG.fullmatch(tag)
        or not SHA.fullmatch(commit)
        or not run.isdigit()
        or not attempt.isdigit()
    ):
        raise ValueError("release identity is malformed")
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("artifact directory is unsafe")
    files = sorted(path for path in directory.iterdir() if path.name != PROOF)
    if (
        len(files) != 2
        or sum(path.name.endswith(".whl") for path in files) != 1
        or sum(path.name.endswith(".tar.gz") for path in files) != 1
    ):
        raise ValueError("release requires exactly one wheel and one sdist")
    rows = []
    payloads = {}
    for path in files:
        if (
            not path.name.startswith("scitex-" + tag[1:] + "-")
            and path.name != "scitex-" + tag[1:] + ".tar.gz"
        ):
            raise ValueError("artifact filename version differs")
        raw = regular_bytes(path)
        payloads["wheel" if path.name.endswith(".whl") else "sdist"] = raw
        identity = (
            wheel_identity(raw, tag[1:])
            if path.name.endswith(".whl")
            else sdist_identity(raw, tag[1:])
        )
        rows.append(
            {
                "name": path.name,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                **identity,
            }
        )
    source_identity = source_payload_identity(
        payloads["wheel"], payloads["sdist"], commit, source_root
    )
    return {
        "schema": "scitex-release/v1",
        "workflow": "pypi-publish-and-github-release-on-tag.yml",
        "sif_sha256": os.environ.get("SCITEX_CI_SIF_SHA256", ""),
        "repository": REPOSITORY,
        "tag": tag,
        "commit": commit,
        "run": run,
        "attempt": attempt,
        "files": rows,
        "source_membership": source_identity,
    }


def main(query=api):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=["resolve", "check-source", "write-proof", "verify-proof"]
    )
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit")
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--revalidate", action="store_true")
    args = parser.parse_args()
    if args.mode == "resolve":
        member_admission(query)
        identity = resolve(args.tag, query)
        if (
            os.environ.get("GITHUB_EVENT_NAME") == "push"
            and os.environ.get("GITHUB_SHA") != identity["commit"]
        ):
            raise ValueError("push event and tag commit differ")
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            for key, value in identity.items():
                stream.write(key + "=" + value + "\n")
        print(json.dumps(identity))
        return
    if args.mode == "check-source":
        check_source_layout(args.commit or "")
        print("Exact clean public source layout verified")
        return
    actual = git_read(["rev-parse", "HEAD"], Path(".")).decode().strip()
    if actual != args.commit:
        raise ValueError("checkout and release commit differ")
    proof = artifact_proof(
        args.dist,
        args.tag,
        args.commit or "",
        os.environ.get("GITHUB_RUN_ID", ""),
        os.environ.get("GITHUB_RUN_ATTEMPT", ""),
    )
    path = args.dist / PROOF
    if args.mode == "write-proof":
        with os.fdopen(
            os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
        ) as stream:
            json.dump(proof, stream, indent=2)
    elif json.loads(regular_bytes(path)) != proof:
        raise ValueError("artifact proof or byte identity differs")
    if args.revalidate:
        member_admission(query)
        if resolve(args.tag, query) != {
            "tag": args.tag,
            "commit": args.commit,
            "version": args.tag[1:],
        }:
            raise ValueError("release tag identity changed")
    print(json.dumps(proof))


if __name__ == "__main__":
    main()
