Linting with SciTeX Dev
=======================

``scitex-dev`` owns the linter engine and discovers rule providers from
installed SciTeX packages. The umbrella exposes its CLI under
``scitex dev linter``.

CLI
---

.. code-block:: bash

   scitex dev linter --help
   scitex dev linter list-rules --json
   scitex dev linter validate-files path/to/script.py

``validate-files`` inspects Python source without running the target script.
Use the installed command's help for filters and output options.

The standalone provider exposes the same commands under ``scitex-dev linter``.

Python API
----------

.. code-block:: python

   from scitex_dev import linter

   rules = linter.list_rules()

The rule inventory includes installed plugin providers, so it depends on the
environment. Providers register through ``scitex_dev.linter.plugins``; each
package owns its domain rules.

Migration and compatibility
---------------------------

Use ``scitex_dev.linter`` or the umbrella's ``scitex.dev.linter`` delegation
instead of ``scitex.linter``. Install the current development-tool provider
rather than the retired standalone ``scitex-linter`` package.

The umbrella and Dev releases must have compatible provider declarations.
For example, legacy umbrella 2.29.3 declares rules now built into Dev 0.62.26;
that combination refuses rule discovery. This source's umbrella no longer
advertises that legacy provider. Dependency installation alone does not prove
that an installed provider set can load.

See the `SciTeX Dev repository <https://github.com/scitex-ai/scitex-dev>`_
for the owning implementation and reference documentation.
