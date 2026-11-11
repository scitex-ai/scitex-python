"""Keep the reviewed source ignore policy independent of checkout location."""

from pathlib import Path


def source_excludes(root: Path, explicit: list[str]) -> list[str]:
    """Preserve Git ignore ordering, followed by explicit target exclusions.

    Hatchling 1.33 drops VCS patterns if an absolute project path matches an
    ignore pattern, for example a checkout under ``var/``. Derive the same
    policy directly from the project file so ignored private paths stay out.
    """
    ignore = root.resolve(strict=True) / ".gitignore"
    if ignore.is_symlink() or not ignore.is_file():
        raise ValueError("source ignore policy must be a contained regular file")
    if not isinstance(explicit, list) or any(not isinstance(p, str) for p in explicit):
        raise ValueError("explicit source exclusions must be a list of strings")
    patterns = [
        line for line in ignore.read_text(encoding="utf-8").splitlines() if line
    ]
    return [*patterns, *explicit]
