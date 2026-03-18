Capture Module (``stx.capture``)
=================================

Screenshot capture and screen monitoring utilities. Useful for
documenting GUI states, recording experiment progress, and
automated visual testing.

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Take a screenshot
   img = stx.capture.snap()

   # Save it
   stx.io.save(img, "screenshot.png")

Key Functions
-------------

``snap(region=None)``
^^^^^^^^^^^^^^^^^^^^^

Capture a screenshot of the entire screen or a specific region.

.. code-block:: python

   # Full screen
   img = stx.capture.snap()

   # Specific region (x, y, width, height)
   img = stx.capture.snap(region=(0, 0, 800, 600))

``monitor(interval=1.0, duration=None, output_dir=".")``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Capture screenshots at regular intervals. Useful for monitoring
long-running GUI processes.

.. code-block:: python

   # Capture every 5 seconds for 1 minute
   stx.capture.monitor(interval=5.0, duration=60, output_dir="./captures")

``crop(image, region)``
^^^^^^^^^^^^^^^^^^^^^^^

Crop a captured image to a specific region.

.. code-block:: python

   img = stx.capture.snap()
   cropped = stx.capture.crop(img, region=(100, 100, 400, 300))
   stx.io.save(cropped, "cropped.png")

Use Cases
---------

Documenting experiment results displayed in a GUI:

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(CONFIG=stx.INJECTED):
       run_experiment_gui()
       img = stx.capture.snap()
       stx.io.save(img, "final_state.png")
       return 0

API Reference
-------------

.. automodule:: scitex.capture
   :members:
   :no-undoc-members:
   :show-inheritance:
