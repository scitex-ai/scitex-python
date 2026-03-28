# Bridge Protocol Versioning (stx.bridge)

The bridge protocol system ensures forward and backward compatibility when cross-module data is serialized and later loaded by a different version of SciTeX.

## Current Version

```python
from scitex.bridge import BRIDGE_PROTOCOL_VERSION
print(BRIDGE_PROTOCOL_VERSION)  # "1.0.0"
```

Protocol versioning follows semantic versioning:
- **MAJOR** — breaking interface change
- **MINOR** — new bridge functions added (backward compatible)
- **PATCH** — bug fixes (backward compatible)

## check_protocol_compatibility

```python
from scitex.bridge import check_protocol_compatibility

# Data saved by v1.0.0, loaded by current version (also 1.0.0)
is_compat, warning = check_protocol_compatibility("1.0.0")
# (True, None)

# Data from older minor (1.1.0 loading 1.0.0 data) — OK
is_compat, warning = check_protocol_compatibility("1.0.0", "1.1.0")
# (True, None)

# Data newer than current — warn but still load
is_compat, warning = check_protocol_compatibility("1.2.0", "1.0.0")
# (True, "Data version newer than current: data v1.2.0, current v1.0.0. Some features may be ignored.")

# Major mismatch — incompatible
is_compat, warning = check_protocol_compatibility("2.0.0")
# (False, "Major version mismatch: data v2.0.0, current v1.0.0")
```

## ProtocolInfo

Dataclass that carries protocol metadata in serialized objects:

```python
from scitex.bridge import ProtocolInfo

info = ProtocolInfo(
    version="1.0.0",
    source_module="stats",
    target_module="plt",
    coordinate_system="axes",
)

d = info.to_dict()
# {"bridge_protocol_version": "1.0.0", "source_module": "stats",
#  "target_module": "plt", "coordinate_system": "axes"}

restored = ProtocolInfo.from_dict(d)
```

## add_protocol_metadata / extract_protocol_metadata

Tag any dict with protocol metadata before serializing, then verify when loading:

```python
from scitex.bridge import add_protocol_metadata, extract_protocol_metadata

data = {"p_value": 0.01, "effect_size": 0.85}

# Annotate before saving
tagged = add_protocol_metadata(data, source_module="stats", target_module="vis")
# tagged["_bridge_protocol"]["bridge_protocol_version"] == "1.0.0"

# Extract and check when loading
info = extract_protocol_metadata(tagged)
if info:
    is_compat, msg = check_protocol_compatibility(info.version)
    if not is_compat:
        raise RuntimeError(f"Incompatible bridge data: {msg}")
```

## Coordinate Systems Reference

```python
from scitex.bridge import COORDINATE_SYSTEMS

# "axes"  — normalized 0-1 axes coords (plt / matplotlib annotations)
# "data"  — actual x/y values (vis / FigureModel)
# "figure" — normalized 0-1 figure coords (suptitle, figure-level)
# "mm"    — physical millimeters (publication layouts)
# "px"    — pixels (canvas, GUI)

print(COORDINATE_SYSTEMS["axes"]["description"])
# "Normalized axes coordinates (0-1)"
```
