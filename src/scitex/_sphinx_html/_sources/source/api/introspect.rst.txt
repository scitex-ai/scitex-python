Introspect Module (``stx.introspect``)
=======================================

IPython-like code inspection for exploring Python packages.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx

   # Function signature (like IPython's func?)
   stx.introspect.q("scitex.stats.test_ttest_ind")
   # → name, signature, parameters, return type

   # Full source code (like IPython's func??)
   stx.introspect.qq("scitex.stats.test_ttest_ind")
   # → complete source with line numbers

   # List module members (like enhanced dir())
   stx.introspect.dir("scitex.plt", filter="public", kind="functions")

   # Recursive API tree
   df = stx.introspect.list_api("scitex", max_depth=2)

IPython-Style Shortcuts
-----------------------

- ``q(dotted_path)`` -- Signature and parameters (like ``func?``)
- ``qq(dotted_path)`` -- Full source code (like ``func??``)
- ``dir(dotted_path, filter, kind)`` -- List members with filtering

Filters: ``"public"``, ``"private"``, ``"dunder"``, ``"all"``

Kinds: ``"functions"``, ``"classes"``, ``"data"``, ``"modules"``

Documentation
-------------

- ``get_docstring(path, format)`` -- Extract docstrings (``"raw"``, ``"parsed"``, ``"summary"``)
- ``get_exports(path)`` -- Get ``__all__`` exports
- ``find_examples(path)`` -- Find usage examples in tests/examples

Type Analysis
-------------

- ``get_type_hints_detailed(path)`` -- Full type annotation analysis
- ``get_class_hierarchy(path)`` -- Inheritance tree (MRO + subclasses)
- ``get_class_annotations(path)`` -- Class variable annotations

Code Analysis
-------------

- ``get_imports(path, categorize)`` -- All imports (AST-based, grouped by stdlib/third-party/local)
- ``get_dependencies(path, recursive)`` -- Module dependency tree
- ``get_call_graph(path, max_depth)`` -- Function call graph (with timeout protection)

API Tree
--------

.. code-block:: python

   # Generate full module tree as DataFrame
   df = stx.introspect.list_api("scitex", max_depth=3, docstring=True)

API Reference
-------------

.. automodule:: scitex.introspect
   :members:
