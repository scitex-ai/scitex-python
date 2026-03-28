---
description: Versioned file management — increment_version generates the next version path, find_latest locates the highest existing version.
---

# Versioned File Management

Both functions work with a versioning convention: `<fname><version_prefix><NNN><ext>`, where `<NNN>` is a zero-padded 3-digit integer (e.g. `model_v001.pkl`, `model_v002.pkl`, ...).

---

## increment_version

Scan a directory for existing versioned files and return the path for the **next** version.

```python
increment_version(
    dirname: str | Path,
    fname: str,
    ext: str,
    version_prefix: str = "_v",
) -> Path
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dirname` | `str` or `Path` | required | Directory to scan and where the new file will be placed |
| `fname` | `str` | required | Base filename without version number or extension |
| `ext` | `str` | required | File extension including the dot (e.g. `".pkl"`) |
| `version_prefix` | `str` | `"_v"` | String inserted between `fname` and the version number |

**Returns** `Path` — full path for the next version file. The file is **not created**; only the path is returned.

**Version numbering**
- If no existing versioned files are found, starts at `001`.
- The version number is always formatted with at least 3 digits (`001`, `002`, ..., `100`, ...).

**Examples**

```python
import scitex as stx

# Suppose ./models/ contains: model_v001.pkl, model_v002.pkl, model_v003.pkl

next_path = stx.path.increment_version("./models", "model", ".pkl")
# Path('./models/model_v004.pkl')

# First version — no existing files
next_path = stx.path.increment_version("./checkpoints", "run", ".pt")
# Path('./checkpoints/run_v001.pt')

# Custom prefix
next_path = stx.path.increment_version("./results", "exp", ".csv", version_prefix="-run")
# Pattern matched: exp-run001.csv, exp-run002.csv, ...
# Returns: Path('./results/exp-run003.csv')

# Typical save workflow
import pickle
model = train()
save_path = stx.path.increment_version("./models", "classifier", ".pkl")
save_path.parent.mkdir(parents=True, exist_ok=True)
with open(save_path, "wb") as f:
    pickle.dump(model, f)
```

---

## find_latest

Scan a directory for versioned files and return the path to the **highest** existing version.

```python
find_latest(
    dirname: str | Path,
    fname: str,
    ext: str,
    version_prefix: str = "_v",
) -> str | None
```

**Parameters**

Same as `increment_version`.

**Returns** `str` path to the file with the highest version number, or `None` if no matching versioned files exist.

**Note**: Returns a `str` (from `glob`), not a `Path`. Cast with `Path(...)` if needed.

**Examples**

```python
import scitex as stx

# Suppose ./models/ contains: model_v001.pkl, model_v003.pkl

latest = stx.path.find_latest("./models", "model", ".pkl")
# './models/model_v003.pkl'

if latest is None:
    print("No versioned files found")
else:
    import pickle
    with open(latest, "rb") as f:
        model = pickle.load(f)

# Load latest checkpoint to resume training
from pathlib import Path
ckpt = stx.path.find_latest("./checkpoints", "run", ".pt")
if ckpt:
    resume_training(checkpoint_path=Path(ckpt))
```

---

## Relationship between the two functions

```
find_latest  -> highest existing version (load/inspect)
increment_version -> next version path (save new artifact)
```

Both functions in `_increment_version.py` are the canonical implementations; `_version.py` contains an older string-returning variant that delegates to the same logic.
