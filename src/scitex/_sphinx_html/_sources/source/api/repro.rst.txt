Repro Module (``stx.repro``)
============================

Reproducibility utilities: random state management, ID generation,
timestamps, and array hashing.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx

   # Fix all random seeds (numpy, torch, random, ...)
   rng = stx.repro.get()           # Global manager (seed=42)
   rng = stx.repro.reset(seed=123) # Reset with new seed

   # Named generators for deterministic results
   data_gen = rng.get_np_generator("data")
   data = data_gen.random(100)  # Same seed+name = same result

   # Unique identifiers
   stx.repro.gen_id()
   # → "2026Y-02M-13D-14h30m15s_a3Bc9xY2"

   stx.repro.gen_timestamp()
   # → "2026-0213-1430"

   # Verify reproducibility
   rng.verify(data, "train_data")  # First: caches hash
   rng.verify(data, "train_data")  # Later: verifies match

RandomStateManager
------------------

Central class for managing random states across libraries.

.. code-block:: python

   rng = stx.repro.RandomStateManager(seed=42)

   # Named generators (same name + seed = deterministic)
   np_gen = rng.get_np_generator("experiment")
   torch_gen = rng.get_torch_generator("model")

   # Checkpoint and restore
   rng.checkpoint("before_training")
   rng.restore("before_training.pkl")

   # Temporary seed change
   with rng.temporary_seed(999):
       noise = rng.get_np_generator("noise").random(10)

Automatically fixes seeds for: ``random``, ``numpy``, ``torch`` (+ CUDA),
``tensorflow``, ``jax``.

Available Functions
-------------------

- ``get(verbose)`` -- Get or create global RandomStateManager singleton
- ``reset(seed, verbose)`` -- Reset global instance with new seed
- ``fix_seeds(seed, ...)`` -- Legacy function (use RandomStateManager instead)
- ``gen_id(time_format, N)`` -- Generate unique timestamp + random ID
- ``gen_timestamp()`` -- Generate timestamp string for file naming
- ``hash_array(array_data)`` -- SHA256 hash of numpy array (16 chars)

API Reference
-------------

.. automodule:: scitex.repro
   :members:
