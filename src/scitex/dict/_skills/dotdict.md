# DotDict — Attribute-Style Dictionary Access (stx.dict)

`DotDict` is a dictionary subclass that allows attribute-style access for string keys that are valid Python identifiers, while also supporting item-style access for any key type (integers, hyphenated strings, etc.).

## Creating a DotDict

```python
from scitex.dict import DotDict

# From a plain dict (nested dicts are converted recursively)
d = DotDict({
    "model": {"lr": 1e-3, "epochs": 100},
    "data":  {"n_samples": 1000},
})

# Attribute access (for valid identifiers)
print(d.model.lr)      # 1e-3
print(d.data.n_samples) # 1000

# Item access (for any key)
print(d["model"]["epochs"])  # 100
d[42] = "integer key"
print(d[42])  # "integer key"
```

## Modifying Values

```python
d = DotDict({"x": 1, "nested": {"a": 10}})

d.x = 99
d["x"] = 99
d.nested.a = 20
del d.x
```

## Conversion and Serialization

```python
# Convert back to plain dict (hides private keys starting with _)
plain = d.to_dict()
plain_with_private = d.to_dict(include_private=True)

# Pretty-print
print(repr(d))         # uses pprint.pformat
print(str(d))          # JSON-formatted string

# pformat method with custom options
print(d.pformat(indent=4, width=120))

# IPython / Jupyter: _repr_pretty_ is defined for nice display
```

## Standard Dict Methods

`DotDict` supports the full standard dict interface:

```python
d.keys()
d.values()
d.items()
len(d)
"key" in d
for key in d: ...

d.get("key", default)
d.setdefault("key", default)
d.pop("key")
d.update({"new_key": "value"})
d.copy()  # shallow copy
```

## Tab Completion

`DotDict.__dir__()` includes all string keys that are valid identifiers, so tab completion works in IPython and Jupyter.

## Equality and Boolean

```python
d1 = DotDict({"a": 1})
d2 = DotDict({"a": 1})

d1 == d2        # True
d1 == {"a": 1}  # True (compares against plain dict)
bool(d1)        # True (non-empty)
bool(DotDict()) # False (empty)
```

## Typical Use Case: Config Files

```python
import scitex as stx

CONFIG = stx.io.load_configs()
# CONFIG is a DotDict — access nested config with dot notation:
print(CONFIG.TRAINING.lr)
print(CONFIG.DATA.n_samples)
```
