Gen Module (``stx.gen``)
========================

General utilities for path management, shell commands, and system operations.

.. note::

   Session management has moved to ``@stx.session`` (see :doc:`/core_concepts`).
   The ``scitex.gen.start()`` / ``scitex.gen.close()`` pattern is deprecated.

Quick Reference
---------------

.. code-block:: python

    import scitex as stx

    # Timestamped output directories
    path = stx.gen.mk_spath("./results")
    # → ./results/20260213_143022/

    # Run shell commands
    stx.gen.run("ls -la")

    # Clipboard operations
    stx.gen.copy("text to clipboard")
    text = stx.gen.paste()

    # String to valid path
    stx.gen.title2path("My Experiment #1")
    # → "my_experiment_1"

API Reference
-------------

.. automodule:: scitex.gen
   :members:
   :show-inheritance:
