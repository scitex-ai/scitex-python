---
name: stx.types
description: Type aliases (ArrayLike, ColorLike) and runtime type-checking guards for scientific Python code.
---

# stx.types — Skills Index

Shared type annotations and runtime guards for array-like inputs, matplotlib colors, and homogeneous lists.

## Sub-skills

| File | Description |
|------|-------------|
| [type-aliases-and-guards.md](type-aliases-and-guards.md) | ArrayLike, ColorLike, is_array_like(), is_listed_X(), is_list_of_type() |

## Quick Reference

```python
from scitex.types import ArrayLike, ColorLike, is_array_like, is_listed_X

def process(data: ArrayLike, color: ColorLike) -> None:
    assert is_array_like(data)
    assert is_listed_X([1, 2, 3], int)
```
