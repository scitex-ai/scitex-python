Utility ownership
=================

There is no public ``scitex.utils`` module. Use the focused owner for the
operation you need rather than a catch-all utility namespace:

* :doc:`/source/api/path` — path operations (``scitex.path`` / ``scitex-path``).
* :doc:`/source/api/str` — text operations (``scitex.str`` / ``scitex-str``).
* :doc:`/source/api/dict` — mapping helpers (``scitex.dict`` / ``scitex-dict``).
* :doc:`/source/api/introspect` — API inspection (``scitex.introspect`` /
  ``scitex-introspect``).

For package installation guidance, use
``from scitex.helpers import show_install_guide``.
