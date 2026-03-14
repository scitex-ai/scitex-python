Logging Module (``stx.logging``)
=================================

Unified logging with file/console output, custom warnings, exception
hierarchy, and stream redirection.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx
   from scitex import logging

   # Get a logger
   logger = logging.getLogger(__name__)
   logger.info("Processing data")
   logger.success("Analysis complete")   # Custom level (31)
   logger.fail("Model diverged")         # Custom level (35)

   # Configure globally
   logging.configure(level="DEBUG", log_file="./run.log")
   logging.set_level("WARNING")

   # Temporary file logging
   with logging.log_to_file("analysis.log"):
       logger.info("This goes to both console and file")

   # Warnings
   logging.warn("Large dataset", category=logging.PerformanceWarning)
   logging.warn_deprecated("old_func", "new_func", version="3.0")
   logging.filterwarnings("ignore", category=logging.UnitWarning)

Log Levels
----------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Level
     - Value
     - Description
   * - ``DEBUG``
     - 10
     - Detailed diagnostic information
   * - ``INFO``
     - 20
     - General operational messages
   * - ``WARNING``
     - 30
     - Something unexpected but not fatal
   * - ``SUCCESS``
     - 31
     - Custom: operation completed successfully
   * - ``FAIL``
     - 35
     - Custom: operation failed (non-fatal)
   * - ``ERROR``
     - 40
     - Serious problem
   * - ``CRITICAL``
     - 50
     - Program may not continue

Warning Categories
------------------

- ``SciTeXWarning`` -- Base warning class
- ``UnitWarning`` -- SI unit convention issues
- ``StyleWarning`` -- Formatting issues
- ``SciTeXDeprecationWarning`` -- Deprecated features
- ``PerformanceWarning`` -- Performance issues
- ``DataLossWarning`` -- Potential data loss

Exception Hierarchy
-------------------

All inherit from ``SciTeXError``:

- **I/O**: ``IOError``, ``FileFormatError``, ``SaveError``, ``LoadError``
- **Config**: ``ConfigurationError``, ``ConfigFileNotFoundError``, ``ConfigKeyError``
- **Path**: ``PathError``, ``InvalidPathError``, ``PathNotFoundError``
- **Data**: ``DataError``, ``ShapeError``, ``DTypeError``
- **Plotting**: ``PlottingError``, ``FigureNotFoundError``, ``AxisError``
- **Stats**: ``StatsError``, ``TestError``
- **Scholar**: ``ScholarError``, ``SearchError``, ``PDFDownloadError``, ``DOIResolutionError``
- **NN**: ``NNError``, ``ModelError``
- **Template**: ``TemplateError``, ``TemplateViolationError``

Stream Redirection
------------------

.. code-block:: python

   from scitex.logging import tee
   import sys

   # Redirect stdout/stderr to log files
   sys.stdout, sys.stderr = tee(sys, sdir="./output")

The ``@stx.session`` decorator handles this automatically.

API Reference
-------------

.. automodule:: scitex.logging
   :members:
