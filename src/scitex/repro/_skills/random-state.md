---
name: repro-random-state
description: Seed all random number generators simultaneously with RandomStateManager. Create named generators for different data streams, verify reproducibility, and use the global get()/reset() interface.
---

# Random State Management

## RandomStateManager

Manages seeded generators for numpy, PyTorch, TensorFlow, JAX, and Python's `random` module — all seeded from a single integer.

```python
import scitex as stx

rng = stx.repro.RandomStateManager(seed=42)
```

### Named generators

Call the instance with a name to get a deterministic numpy `Generator` for that stream.

```python
rng = stx.repro.RandomStateManager(seed=42)

data = rng("data").random(100)           # 100 uniform samples
noise = rng("noise").normal(size=(50,))  # 50 Gaussian samples
idx   = rng("split").integers(0, 1000, size=200)

# Same call always returns the same generator
assert (rng("data").random(100) == rng("data").random(100)).all()
```

### Integration with @stx.session

```python
@stx.session
def main(CONFIG=stx.INJECTED, rng=stx.INJECTED):
    X_train = rng("train_data").random((1000, 64))
    model_weights = rng("init").normal(size=(64, 32))
    return 0
```

### verify

Compute a fingerprint of an object and check that re-generation produces the same fingerprint.

```python
rng = stx.repro.RandomStateManager(seed=42)
data = rng("data").random(1000)
rng.verify(data, "data")   # asserts reproducibility
```

### Verbose mode

```python
rng = stx.repro.RandomStateManager(seed=42, verbose=True)
# Prints which backends were seeded (numpy, torch, etc.)
```

---

## get / reset

Module-level helpers for the global `RandomStateManager` singleton.

```python
stx.repro.get(seed: int = 42) -> RandomStateManager
    # Return (or create) the global instance

stx.repro.reset(seed: int = 42) -> RandomStateManager
    # Reset the global instance with a new seed
```

```python
import scitex as stx

rng = stx.repro.get(seed=123)
data = rng("experiment").random(50)
```
