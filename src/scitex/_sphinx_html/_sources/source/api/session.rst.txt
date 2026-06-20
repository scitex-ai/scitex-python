Session Decorator (``@stx.session``)
=====================================

The ``@stx.session`` decorator is the primary entry point for SciTeX
scripts. It wraps a function to provide automatic CLI generation,
output directory management, configuration injection, and provenance tracking.

Basic Usage
-----------

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(
       data_path="data.csv",       # CLI: --data-path data.csv
       threshold=0.5,              # CLI: --threshold 0.7
       CONFIG=stx.INJECTED,        # Auto-injected session config
       plt=stx.INJECTED,           # Pre-configured matplotlib
       logger=stx.INJECTED,        # Session logger
   ):
       """Analyze experimental data."""
       data = stx.io.load(data_path)
       result = process(data, threshold)
       stx.io.save(result, "output.csv")
       return 0  # exit code (0 = success)

   if __name__ == "__main__":
       main()  # No arguments triggers CLI mode

Run from the command line:

.. code-block:: bash

   python my_script.py --data-path experiment.csv --threshold 0.3
   python my_script.py --help  # Shows all parameters with defaults

How It Works
------------

.. image:: ../_static/session_lifecycle.png
   :width: 60%
   :align: center
   :alt: Session lifecycle: main() → Parse CLI → Create dir → Load config → Execute → SUCCESS or ERROR

When ``main()`` is called **without arguments**, the decorator:

1. **Parses CLI arguments** from the function signature (type hints and defaults become ``argparse`` options)
2. **Creates a session directory** under ``script_out/RUNNING/{session_id}/``
3. **Loads configuration** from ``./config/*.yaml`` files into ``CONFIG``
4. **Injects globals** (``CONFIG``, ``plt``, ``COLORS``, ``logger``, ``rngg``) into the function
5. **Redirects stdout/stderr** to log files
6. **Executes the function** with parsed arguments
7. **Moves output** from ``RUNNING/`` to ``FINISHED_SUCCESS/`` (or ``FINISHED_ERROR/``)

When called **with arguments** (e.g., ``main(data_path="x.csv")``), the decorator
is bypassed and the function runs directly -- useful for testing and notebooks.

Output Directory Structure
--------------------------

Each run produces a self-contained output directory:

.. code-block:: text

   my_script_out/
   +-- FINISHED_SUCCESS/
   |   +-- 2026Y-02M-13D-14h30m15s_Z5MR/
   |       +-- CONFIGS/
   |       |   +-- CONFIG.yaml     # Frozen configuration
   |       |   +-- CONFIG.pkl      # Pickled config
   |       +-- logs/
   |       |   +-- stdout.log      # Captured stdout
   |       |   +-- stderr.log      # Captured stderr
   |       +-- output.csv          # Your saved files
   |       +-- sine.png            # Your saved figures
   |       +-- sine.csv            # Auto-exported figure data
   +-- FINISHED_ERROR/
   |   +-- ...                     # Runs that returned non-zero
   +-- RUNNING/
       +-- ...                     # Currently active sessions

The session ID format is ``YYYY-MM-DD-HH:MM:SS_XXXX`` where ``XXXX`` is
a random 4-character suffix for uniqueness.

Injected Parameters
-------------------

Use ``stx.INJECTED`` as the default value to receive auto-injected objects:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter Name
     - Type
     - Description
   * - ``CONFIG``
     - ``DotDict``
     - Session config with ``ID``, ``SDIR_RUN``, ``FILE``, ``ARGS``, plus all ``./config/*.yaml`` values
   * - ``plt``
     - module
     - ``matplotlib.pyplot`` configured for the session (Agg backend, style settings)
   * - ``COLORS``
     - ``DotDict``
     - Color palette for consistent plotting
   * - ``logger``
     - Logger
     - SciTeX logger writing to session log files
   * - ``rngg``
     - ``RandomStateManager``
     - Reproducibility manager (seeds fixed by default)

Only request the parameters you need:

.. code-block:: python

   @stx.session
   def main(n=100, CONFIG=stx.INJECTED):
       """Minimal example -- only CONFIG injected."""
       print(f"Session ID: {CONFIG.ID}")
       print(f"Output dir: {CONFIG.SDIR_RUN}")
       return 0

CONFIG Object
-------------

The injected ``CONFIG`` is a ``DotDict`` supporting both dictionary and
dot-notation access:

.. code-block:: python

   CONFIG["MODEL"]["hidden_size"]   # dict-style
   CONFIG.MODEL.hidden_size         # dot-style (equivalent)

It contains:

.. code-block:: python

   CONFIG.ID             # "2026Y-02M-13D-14h30m15s_Z5MR"
   CONFIG.PID            # Process ID
   CONFIG.FILE           # Path to the script
   CONFIG.SDIR_OUT       # Base output directory
   CONFIG.SDIR_RUN       # Current session's output directory
   CONFIG.START_DATETIME # When the session started
   CONFIG.ARGS           # Parsed CLI arguments as dict
   CONFIG.EXIT_STATUS    # 0 (success), 1 (error), or None

Any YAML files in ``./config/`` are merged into CONFIG:

.. code-block:: yaml

   # ./config/EXPERIMENT.yaml
   learning_rate: 0.001
   batch_size: 32

.. code-block:: python

   # Accessible as:
   CONFIG.EXPERIMENT.learning_rate  # 0.001
   CONFIG.EXPERIMENT.batch_size     # 32

Decorator Options
-----------------

.. code-block:: python

   @stx.session(verbose=True, agg=False, notify=True, sdir_suffix="v2")
   def main(...):
       ...

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Option
     - Type
     - Default
     - Description
   * - ``verbose``
     - bool
     - ``False``
     - Enable verbose logging
   * - ``agg``
     - bool
     - ``True``
     - Use matplotlib Agg backend (set ``False`` for interactive plots)
   * - ``notify``
     - bool
     - ``False``
     - Send notification when session completes
   * - ``sdir_suffix``
     - str
     - ``None``
     - Append suffix to output directory name

Best Practices
--------------

1. **One session per script** -- each ``.py`` file should have one ``@stx.session`` function
2. **Return 0 for success** -- the return value becomes the exit status
3. **Save outputs with** ``stx.io.save`` -- files go into the session directory and are provenance-tracked
4. **Put config in YAML** -- use ``./config/*.yaml`` instead of hardcoding parameters
5. **Use** ``stx.repro.fix_seeds()`` -- already called by default via ``rngg``

API Reference
-------------

.. automodule:: scitex.session
   :members:
   :no-undoc-members:
   :exclude-members: _InjectedSentinel
