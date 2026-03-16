Decorators Module (``stx.decorators``)
=======================================

Function decorators for type conversion, batching, caching, and more.

Quick Reference
---------------

.. code-block:: python

   from scitex.decorators import torch_fn, batch_fn, cache_disk, timeout

   @torch_fn
   def process(x):
       """Auto-converts inputs to torch tensors, outputs back."""
       return x * 2

   @batch_fn
   def predict(data, batch_size=32):
       """Process data in batches with progress bar."""
       return model(data)

   @cache_disk
   def expensive_computation(params):
       """Results cached to disk for reuse."""
       return heavy_compute(params)

   @timeout(seconds=30)
   def risky_call():
       """Raises TimeoutError if exceeds 30s."""
       return external_api()

Type Conversion
---------------

Auto-convert between data frameworks:

- ``@torch_fn`` -- Inputs to PyTorch tensors, outputs back to original type
- ``@numpy_fn`` -- Inputs to NumPy arrays
- ``@pandas_fn`` -- Inputs to pandas objects
- ``@xarray_fn`` -- Inputs to xarray objects

Batch Processing
----------------

- ``@batch_fn`` -- Split input into batches with tqdm progress
- ``@batch_numpy_fn`` -- NumPy conversion + batching
- ``@batch_torch_fn`` -- PyTorch conversion + batching
- ``@batch_pandas_fn`` -- Pandas conversion + batching

Caching
-------

- ``@cache_mem`` -- In-memory function result caching
- ``@cache_disk`` -- Persistent disk-based caching
- ``@cache_disk_async`` -- Async disk caching

Utilities
---------

- ``@deprecated(reason, forward_to)`` -- Mark functions as deprecated
- ``@not_implemented`` -- Mark as not yet implemented
- ``@timeout(seconds)`` -- Enforce execution time limits
- ``@preserve_doc`` -- Preserve docstrings when wrapping

Auto-Ordering
-------------

.. code-block:: python

   from scitex.decorators import enable_auto_order

   enable_auto_order()
   # Now decorators are applied in optimal order regardless of code order

API Reference
-------------

.. automodule:: scitex.decorators
   :members:
