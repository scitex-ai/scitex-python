App Module (``stx.app``)
========================

Runtime SDK for SciTeX applications. Provides a unified interface for
file storage, configuration, and lifecycle management that works
identically in local and cloud environments.

.. note::

   ``stx.app`` delegates to the standalone
   `scitex-app <https://github.com/ywatanabe1989/scitex-app>`_ package.
   Install with: ``pip install scitex-app``.

Overview
--------

SciTeX applications are self-contained scientific tools that can run
locally or on the SciTeX cloud platform. The ``stx.app`` module
provides the runtime SDK that each application uses to interact with
its environment.

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Get current application info
   info = stx.app.get_info()

   # Access application preferences
   prefs = stx.app.get_prefs()

   # Check dependencies
   stx.app.check_deps()

Key Features
------------

**Unified File Storage**
   Read and write files through a single API that abstracts local
   filesystem and cloud storage.

   .. code-block:: python

      # These work identically locally and in the cloud
      stx.app.write_file("results/output.csv", data)
      content = stx.app.read_file("config/settings.yaml")

**Configuration Management**
   Application preferences are stored in a standard location and
   accessible via dot-notation.

   .. code-block:: python

      prefs = stx.app.get_prefs()
      print(prefs.theme)
      print(prefs.default_format)

      stx.app.set_prefs(theme="dark", default_format="pdf")

**Application Lifecycle**
   Query and manage the running application.

   .. code-block:: python

      info = stx.app.get_info()
      print(info.name)
      print(info.version)

      current = stx.app.get_current()    # Currently active app

**Dependency Checking**
   Verify that all required packages are available.

   .. code-block:: python

      missing = stx.app.check_deps()
      if missing:
          print(f"Missing: {missing}")

Creating an Application
-----------------------

Scaffold a new SciTeX application from a template:

.. code-block:: bash

   scitex template clone app my_tool

This creates a project with bridge-init configuration, MountPoint
definitions, and EventBus integration pre-configured.

API Reference
-------------

.. automodule:: scitex.app
   :members:
   :no-undoc-members:
   :show-inheritance:
