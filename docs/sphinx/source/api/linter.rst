Linter (``scitex_dev.linter``)
==============================

The AST linter belongs to ``scitex-dev``. The former ``scitex-linter``
package and ``scitex.linter`` Python import are retired. Install the public
owner with ``pip install scitex-dev``; the umbrella already requires it.

CLI
---

.. code-block:: bash

   scitex-dev linter validate-files my_script.py
   scitex-dev linter validate-files my_script.py --severity warning
   scitex-dev linter list-rules --json
   scitex-dev linter list-rules-all --json

``list-rules`` reports built-in rules; ``list-rules-all`` also discovers
installed leaf plugins. Rule inventories change with the installed providers,
so query them instead of relying on a fixed count or copied rule table.
Use ``scitex-dev linter --help`` for the installed command surface.

Python
------

.. code-block:: python

   from scitex_dev.linter import list_rules

   rules = list_rules()
   structure_rules = list_rules(category="structure")

The CLI handles file validation; the public Python ``list_rules`` function
returns built-in and installed plugin rules. See
:doc:`/api/scitex.linter` for the owner API. The documentation URL is retained
for existing links; it does not restore the retired umbrella Python import.
