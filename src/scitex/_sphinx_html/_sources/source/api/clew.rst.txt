Clew Module (``stx.clew``)
==========================

Hash-based provenance tracking for reproducible science. Clew (Ariadne's
thread) records file hashes during ``@stx.session`` runs and traces
dependency chains back to source.

How It Works
------------

1. ``@stx.session`` starts a tracking session
2. ``stx.io.load()`` records input file hashes
3. ``stx.io.save()`` records output file hashes
4. Session close computes a combined hash of all inputs/outputs
5. Later, ``stx.clew`` can verify nothing has changed

.. code-block:: python

   import scitex as stx

   # Automatic -- just use @stx.session + stx.io
   @stx.session
   def main():
       data = stx.io.load("input.csv")      # Tracked as input
       result = process(data)
       stx.io.save(result, "output.png")     # Tracked as output
       return 0

   # Verify later
   stx.clew.status()                         # Like git status
   stx.clew.run("session_id")                # Verify by hash
   stx.clew.chain("output.png")              # Trace to source

CLI Commands
------------

.. code-block:: bash

   scitex clew status                  # Show changed files
   scitex clew list                    # List all tracked runs
   scitex clew run <session_id>        # Verify a specific run
   scitex clew chain <file>            # Trace dependency chain
   scitex clew stats                   # Database statistics

Verification Levels
-------------------

- **CACHE** -- Hash comparison only (fast). Checks if files match stored hashes.
- **RERUN** -- Re-execute scripts and compare outputs (thorough). Catches logic errors.

.. code-block:: python

   # Fast: hash comparison
   result = stx.clew.run("session_id")

   # Thorough: re-execute and compare
   result = stx.clew.run("session_id", from_scratch=True)

Dependency Chains
-----------------

Clew traces ``parent_session`` links to build a DAG from final output
back to original source:

.. code-block:: python

   chain = stx.clew.chain("final_figure.png")
   # Shows: source.py → intermediate.csv → analysis.py → final_figure.png

   # Visualize as Mermaid DAG
   stx.clew.mermaid("session_id")

Verification Statuses
---------------------

- ``VERIFIED`` -- Files match expected hashes
- ``MISMATCH`` -- Files differ from stored hashes
- ``MISSING`` -- Files no longer exist
- ``UNKNOWN`` -- No prior tracking data

Key Functions
-------------

- ``status()`` -- Show changed items (like ``git status``)
- ``run(session_id)`` -- Verify a specific run
- ``chain(target_file)`` -- Trace dependency chain
- ``list_runs(limit, status)`` -- List tracked runs
- ``stats()`` -- Database statistics

API Reference
-------------

.. automodule:: scitex.clew
   :members:
