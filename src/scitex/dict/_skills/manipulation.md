---
description: Safely merge dicts with safe_merge(), remove keys with pop_keys(), replace values with replace(), flatten nested dicts with flatten(), accumulate lists with listed_dict(), and serialize with to_str().
---

# Dict Manipulation

## safe_merge

Merge two dicts, raising `KeyError` on duplicate keys (no silent overwrite).

```python
safe_merge(base: dict, update: dict) -> dict
```

```python
import scitex as stx

merged = stx.dict.safe_merge({"a": 1}, {"b": 2})
# {"a": 1, "b": 2}

# Raises KeyError — 'a' exists in both
stx.dict.safe_merge({"a": 1}, {"a": 99})
```

---

## pop_keys

Return a new dict with specified keys removed.

```python
pop_keys(d: dict, keys: list) -> dict
```

```python
import scitex as stx

d = {"a": 1, "b": 2, "c": 3}
cleaned = stx.dict.pop_keys(d, ["b", "c"])
# {"a": 1}
```

---

## replace

Return a new dict with values replaced by a mapping.

```python
replace(d: dict, replacements: dict) -> dict
```

```python
import scitex as stx

d = {"status": "ok", "code": 200}
updated = stx.dict.replace(d, {"ok": "success"})
# {"status": "success", "code": 200}
```

---

## flatten

Flatten a nested dict into a single-level dict with dotted keys.

```python
flatten(d: dict, sep: str = ".") -> dict
```

```python
import scitex as stx

nested = {"model": {"hidden": 256, "layers": 4}, "lr": 0.001}
flat = stx.dict.flatten(nested)
# {"model.hidden": 256, "model.layers": 4, "lr": 0.001}
```

---

## listed_dict

A dict subclass that auto-creates lists on first access and appends values.

```python
import scitex as stx

acc = stx.dict.listed_dict()
for epoch in range(3):
    acc["loss"].append(0.5 / (epoch + 1))
    acc["acc"].append(0.8 + epoch * 0.05)

print(acc["loss"])  # [0.5, 0.25, 0.167]
```

---

## to_str

Serialize a dict to a formatted string.

```python
to_str(d: dict, sep: str = ", ", kv_sep: str = "=") -> str
```

```python
import scitex as stx

d = {"lr": 0.001, "epochs": 100}
s = stx.dict.to_str(d)
# "lr=0.001, epochs=100"
```
