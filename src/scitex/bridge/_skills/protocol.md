---
name: bridge-protocol
description: Bridge protocol version management — check compatibility with check_protocol_compatibility(), attach version metadata with add_protocol_metadata(), and extract it with extract_protocol_metadata().
---

# Bridge Protocol

## BRIDGE_PROTOCOL_VERSION

Current protocol version string: `"1.0.0"`.

```python
import scitex as stx

print(stx.bridge.BRIDGE_PROTOCOL_VERSION)  # '1.0.0'
```

---

## check_protocol_compatibility

Verify that a saved object's protocol version is compatible with the current bridge.

```python
check_protocol_compatibility(metadata: dict) -> bool
```

```python
import scitex as stx

loaded = stx.io.load("saved_annotations.pkl")
if stx.bridge.check_protocol_compatibility(loaded.get("_bridge_meta", {})):
    # safe to use
    pass
```

---

## add_protocol_metadata / extract_protocol_metadata

Embed and retrieve protocol metadata in a dict object.

```python
add_protocol_metadata(data: dict) -> dict
extract_protocol_metadata(data: dict) -> ProtocolInfo
```

```python
import scitex as stx

annotations = {"x1": 0, "x2": 1, "symbol": "**"}
versioned = stx.bridge.add_protocol_metadata(annotations)
stx.io.save(versioned, "annotations.pkl")

# Later
loaded = stx.io.load("annotations.pkl")
info = stx.bridge.extract_protocol_metadata(loaded)
print(info.version)  # '1.0.0'
```

---

## COORDINATE_SYSTEMS

Dict describing the coordinate convention for each bridge type.

```python
import scitex as stx

print(stx.bridge.COORDINATE_SYSTEMS)
# {'plt': 'axes (0-1 normalized)', 'vis': 'data coordinates'}
```
