Config Module (``stx.config``)
===============================

YAML-based configuration with priority resolution and path management.

Priority Resolution
-------------------

All config values follow the same precedence:

.. code-block:: text

   direct argument > config/YAML > environment variable > default

Quick Reference
---------------

.. code-block:: python

   import scitex as stx

   # Get global config (reads ~/.scitex/config.yaml)
   config = stx.config.get_config()

   # Resolve with precedence
   log_level = config.resolve("logging.level", default="INFO")
   # Checks: direct → YAML → SCITEX_LOGGING_LEVEL env → "INFO"

   # Access nested values
   config.get_nested("scholar", "crossref_email")

   # Path management
   paths = stx.config.get_paths()
   paths.scholar        # ~/.scitex/scholar
   paths.cache          # ~/.scitex/cache

YAML Configuration
------------------

.. code-block:: yaml

   # ~/.scitex/config.yaml (or ./config/*.yaml for projects)
   logging:
     level: INFO

   scholar:
     crossref_email: ${CROSSREF_EMAIL:-user@example.com}

Environment variable substitution with ``${VAR:-default}`` syntax is
supported in YAML files.

Key Classes
-----------

- ``ScitexConfig`` -- YAML-based config with env var substitution and precedence resolution
- ``PriorityConfig`` -- Dict-based config resolver for programmatic use
- ``ScitexPaths`` -- Centralized path manager (all paths derive from ``~/.scitex/``)
- ``EnvVar`` -- Environment variable definition dataclass

Path Management
---------------

``ScitexPaths`` manages all SciTeX directories:

.. code-block:: python

   paths = stx.config.get_paths()
   paths.base       # ~/.scitex (SCITEX_DIR)
   paths.logs       # ~/.scitex/logs
   paths.cache      # ~/.scitex/cache
   paths.scholar    # ~/.scitex/scholar
   paths.rng        # ~/.scitex/rng
   paths.capture    # ~/.scitex/capture

Utility Functions
-----------------

- ``get_config(path)`` -- Get singleton ScitexConfig instance
- ``get_paths(base_dir)`` -- Get singleton ScitexPaths instance
- ``load_yaml(path)`` -- Load YAML with env var substitution
- ``load_dotenv(path)`` -- Load ``.env`` file
- ``get_scitex_dir()`` -- Get SCITEX_DIR with precedence

API Reference
-------------

.. automodule:: scitex.config
   :members:
