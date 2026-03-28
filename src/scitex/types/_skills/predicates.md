---
description: Check whether a list is homogeneously typed with is_listed_X() and is_list_of_type().
---

# List Type Predicates

## is_listed_X

Check if a value is a list (or tuple) where every element is of the same expected type `X`.

```python
is_listed_X(obj, X: type) -> bool
```

```python
import scitex as stx

stx.types.is_listed_X([1, 2, 3], int)        # True
stx.types.is_listed_X([1, 2.0, 3], int)      # False — 2.0 is float
stx.types.is_listed_X(["a", "b"], str)        # True
stx.types.is_listed_X([], str)                # True — empty list
```

---

## is_list_of_type

Alias for `is_listed_X` with a more explicit name.

```python
is_list_of_type(obj, expected_type: type) -> bool
```

```python
import scitex as stx
import numpy as np

arrays = [np.array([1, 2]), np.array([3, 4])]
stx.types.is_list_of_type(arrays, np.ndarray)  # True
```
