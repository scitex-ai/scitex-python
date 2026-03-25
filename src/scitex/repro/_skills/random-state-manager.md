---
description: Cross-framework seed fixing, named generators, reproducibility verification, checkpoint/restore, and temporary seed contexts.
---

# stx.repro — RandomStateManager

`RandomStateManager` fixes random seeds across all installed frameworks simultaneously and provides named, independent generators per concept.

## Construction and seed fixing

```python
from scitex.repro import RandomStateManager

rng = RandomStateManager(seed=42, verbose=True)
# Fixes seeds for: os.environ PYTHONHASHSEED, random, numpy,
#                  torch (+ CUDA cudnn.deterministic), tensorflow, jax
```

When `verbose=True`, logs which modules were seeded:
```
RandomStateManager initialized with seed 42
Fixed random seeds for: random, numpy, torch+cuda, tensorflow
```

## Named generators

Each name gets an independent, deterministically-seeded NumPy generator derived from `seed + md5(name)`:

```python
data_gen  = rng.get_np_generator("data")    # numpy.random.Generator
model_gen = rng.get_np_generator("model")

data    = data_gen.random(100)
weights = model_gen.normal(size=(10, 10))

# rng(name) is a callable shorthand (backward compat)
data_gen = rng("data")
```

For PyTorch generators:
```python
torch_gen = rng.get_torch_generator("augment")
x = torch.randn(5, 5, generator=torch_gen)
```

For scikit-learn (integer random state):
```python
rs = rng.get_sklearn_random_state("split")
X_train, X_test = train_test_split(X, random_state=rs)
```

## verify — reproducibility checking

`verify` hashes an object and compares it to a cached value. First call caches; subsequent calls assert equality.

```python
data = data_gen.random(100)
rng.verify(data, "train_data")   # First run: caches hash
# Second run:
rng.verify(data, "train_data")   # Verified → True
                                  # Different → raises ValueError + prints diff

rng.verify(data)                  # Auto-names from caller filename + line number
```

Supported types: `np.ndarray`, `torch.Tensor`, `tf.Tensor`, `jax.Array`, `pd.DataFrame/Series`, `list/tuple`, `dict`, and any `str(obj)`.

Hashes are stored in `~/.scitex/rng/<name>.json`.

```python
rng.clear_cache()                 # Remove all cached hashes
rng.clear_cache("train_data")     # Remove specific
rng.clear_cache("exp_*")          # Glob pattern
```

## checkpoint / restore

Save and restore all named generator states:

```python
ckpt_path = rng.checkpoint("mid_training")   # Saves to ~/.scitex/rng/mid_training.pkl
# ... do things ...
rng.restore(ckpt_path)                        # Restores seeds + all generator states
```

## temporary_seed context manager

Temporarily override `random` and `numpy` seeds, then restore:

```python
with rng.temporary_seed(99):
    sample = data_gen.random(10)   # Uses seed 99 context
# Original random states restored
```

## Global singleton helpers

```python
from scitex.repro import get, reset

rng = get()            # Get or create global instance (seed=42)
rng = reset(seed=123)  # Replace global instance with new seed
```
