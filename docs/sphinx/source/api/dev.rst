Developer tools (``scitex.dev``)
================================

The umbrella delegates developer tooling to the public ``scitex-dev`` package.
Its CLI and installed Python API are the authority; the umbrella does not
implement separate ecosystem management or lint engines.

Discover the installed tools
----------------------------

.. code-block:: bash

   scitex-dev --help
   scitex-dev ecosystem list --json
   scitex-dev list-python-apis
   scitex-dev docs --help

The registry is extensible and changes between releases, so query it rather
than relying on a fixed package count. The AST linter also belongs to this
package; see :doc:`linter` for its current commands and public Python owner.

Source checks
-------------

The project auditor checks a named distribution against an explicit checkout:

.. code-block:: bash

   scitex-dev ecosystem audit-project scitex-io --path /path/to/scitex-io

Replace the distribution and path with the package being reviewed. This
reports findings; it does not install dependencies or repair source code.
Use ``scitex-dev ecosystem --help`` for the available maintenance commands.

Structured results
------------------

The public result type uses ``success``, ``error`` and ``error_code``:

.. code-block:: python

   from scitex_dev import Result

   passed = Result(success=True, data={"accuracy": 0.95})
   failed = Result(success=False, error="File missing", error_code="NOT_FOUND")

Developer APIs have distinct input contracts: for example, ``get_docs``
selects package documentation rather than resolving an arbitrary Python
symbol, and ``bulk_rename`` accepts a ``RenameConfig`` object. Inspect the
installed API before using a maintenance operation; the old convenience
examples ``ecosystem_sync``, ``ecosystem_commit`` and ``reload`` are not
public functions in the current owner.

API reference
-------------

.. automodule:: scitex.dev
   :members:
   :no-undoc-members:
   :show-inheritance:
