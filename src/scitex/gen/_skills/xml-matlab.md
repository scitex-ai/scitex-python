---
description: XML parsing and MATLAB .mat file loading utilities in stx.gen — xml2dict converts XML files to nested dicts, while mat2dict/mat2npa/dir2npy load .mat files into Python/NumPy structures.
---

# XML and MATLAB Utilities

---

## XML Parsing

### xml2dict

Parses an XML file into a nested Python dict.

```python
xml2dict(lpath_xml: str) -> XmlDictConfig
```

Returns an `XmlDictConfig` instance (a subclass of `dict`).

```python
import scitex as stx

cfg = stx.gen.xml2dict("/path/to/config.xml")
print(cfg["root"]["section"]["key"])
```

### XmlDictConfig

A `dict` subclass that recursively converts an `xml.etree.ElementTree` element and its children into a Python dict. Nested elements become nested dicts; repeated tags at the same level become an `XmlListConfig`.

```python
from xml.etree import cElementTree as ElementTree
from scitex.gen import XmlDictConfig

tree = ElementTree.parse("your_file.xml")
root = tree.getroot()
xmldict = XmlDictConfig(root)
# Use like a plain dict
value = xmldict["section"]["key"]
```

**Rules:**
- Element with a single child or children with **different** tags → `XmlDictConfig`
- Element with children that all share the **same** tag → `XmlListConfig`
- Element with text content (no children, no attributes) → stored as a string value
- Element attributes are merged into the dict

### XmlListConfig

A `list` subclass that converts a sequence of same-tagged XML elements into a Python list. Elements that have children are wrapped in `XmlDictConfig`; plain text elements are appended as strings.

```python
from scitex.gen import XmlListConfig
```

---

## MATLAB .mat File Utilities

Legacy helpers for loading MATLAB `.mat` files. Tries HDF5 format first (`h5py`), falls back to `scipy.io.loadmat`.

### mat2dict

```python
mat2dict(fname: str) -> dict
```

Returns a dict mapping variable names to their values. Adds a `"__hdf__"` key (`True`/`False`) indicating which backend was used.

```python
import scitex as stx

d = stx.gen.mat2dict("/data/recording.mat")
signal = d["eeg"]   # h5py Dataset or numpy array depending on format
is_hdf = d["__hdf__"]
```

### public_keys

```python
public_keys(d: dict) -> list
```

Returns keys from a mat2dict result that do not start with `_` (i.e., user variables, not MATLAB metadata).

```python
keys = stx.gen.public_keys(d)
```

### save_npa

```python
save_npa(fname: str, x: np.ndarray) -> None
```

Saves a numpy array to `fname` using `np.save`.

### mat2npy

```python
mat2npy(fname: str, typ: type) -> None
```

Loads the first variable from a `.mat` file and saves it as a `.npy` file alongside the original (`.mat` extension replaced).

> **Warning:** Contains `pdb.set_trace()` calls in `mat2npa` and `keys2npa` — these are legacy debugging artifacts. For production use, call `mat2dict` directly.

### dir2npy

```python
dir2npy(dir: str, typ: type, regex: str = "*") -> None
```

Converts all `regex + ".mat"` files in `dir` to `.npy` files. Changes the working directory to `dir` during execution.

```python
stx.gen.dir2npy("/data/eeg/", typ=np.float32, regex="*xdata")
```

---

## Recommended alternatives

For new code, prefer:
- XML → `stx.io.load("file.xml")` (if supported) or `xml2dict` directly
- MATLAB → `stx.io.load("file.mat")` which wraps both `h5py` and `scipy.io.loadmat`
