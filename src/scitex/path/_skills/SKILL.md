---
name: stx.path
description: Path manipulation utilities for finding files, decomposing paths, managing session output paths, versioning, symlinks, cleaning, and miscellaneous helpers.
---

# stx.path

The `stx.path` module provides path manipulation utilities for scientific computing workflows: finding files, creating session-organized output paths, managing symlinks, version-based file discovery, and path normalization.

Access via `import scitex as stx`, then `stx.path.<function>`.

## Sub-skills

### File and Directory Search
- [find.md](find.md) — `find_file`, `find_dir`, `find_git_root`: recursive search with glob patterns; auto-excludes `lib/`, `env/`, `build/` directories

### Path Decomposition
- [split.md](split.md) — `split`: decompose a path into `(directory: Path, stem: str, extension: str)` in one call

### Session-Relative Output Paths
- [spath.md](spath.md) — `mk_spath`, `get_spath`: derive output paths co-located with the calling script under `<script_stem>_out/`; optionally create directories

### Versioned File Management
- [version.md](version.md) — `increment_version`, `find_latest`: scan a directory for `<name>_v001.<ext>` style files and return the next version path or the current highest version

### Symlink Management
- [symlink.md](symlink.md) — `symlink`, `create_relative_symlink`, `is_symlink`, `readlink`, `resolve_symlinks`, `list_symlinks`, `fix_broken_symlinks`, `unlink_symlink`

### Path Cleaning
- [clean.md](clean.md) — `clean`: normalize a path string — resolves `./`/`../`, collapses `//`, replaces spaces with underscores

### Miscellaneous
- [misc.md](misc.md) — `getsize` (file size in bytes or `nan`), `this_path`/`get_this_path` (caller script path), `get_data_path_from_a_package` (locate package-bundled data files)

## Quick Reference

```python
import scitex as stx

# Find files
csv_files = stx.path.find_file("./data", "*.csv")
result_dirs = stx.path.find_dir(".", "*_out")
root = stx.path.find_git_root()

# Decompose a path
dirname, stem, ext = stx.path.split("/data/results/model_v001.pkl")
# dirname=Path('/data/results'), stem='model_v001', ext='.pkl'

# Session output path (next to the calling script)
out = stx.path.mk_spath("results.csv", makedirs=True)

# Versioned files
next_path = stx.path.increment_version("./models", "run", ".pkl")
latest = stx.path.find_latest("./models", "run", ".pkl")

# Symlinks
stx.path.symlink("/data/file.csv", "./link.csv")
stx.path.create_relative_symlink("../file.csv", "./link.csv")
links = stx.path.list_symlinks("./outputs", recursive=True)
result = stx.path.fix_broken_symlinks("./outputs", remove=True)
stx.path.unlink_symlink("./link.csv")

# Path cleaning
stx.path.clean('/home/user/./folder/../file.txt')
# '/home/user/file.txt'

# Misc
size = stx.path.getsize("large_file.h5")   # int bytes, or np.nan
script = stx.path.this_path()              # Path of calling script
```
