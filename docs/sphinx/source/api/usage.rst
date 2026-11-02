Usage templates (``scitex.usage``)
==================================

``show`` emits the same prefix-free template text that it returns. Query
``topics`` for the installed template inventory instead of assuming that a
particular snippet exists in every template package release.

.. code-block:: python

   from scitex.usage import show, topics

   available = topics()
   text = show("session-minimal")

.. automodule:: scitex.usage
   :members: show, topics
