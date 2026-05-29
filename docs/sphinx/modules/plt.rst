PLT Module (``stx.plt``)
========================

Publication-ready figures powered by `figrecipe <https://github.com/ywatanabe1989/figrecipe>`_.

.. note::

   ``stx.plt`` wraps matplotlib via the **figrecipe** package, adding
   mm-based layout, data-tracking axes, auto CSV export, and reproducible
   YAML recipes. The standalone package can also be used directly:
   ``pip install figrecipe``.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx

   # Create figure (returns FigWrapper, AxisWrapper)
   fig, ax = stx.plt.subplots()
   fig, axes = stx.plt.subplots(2, 2)

   # Data-tracking plot methods (all record data for CSV export)
   ax.plot_line(x, y, label="signal")
   ax.plot_scatter(x, y, alpha=0.5)
   ax.plot_bar(labels, values)
   ax.plot_heatmap(matrix)
   ax.plot_violin(groups)
   ax.plot_box(groups)
   ax.plot_kde(data)

   # Axis helper (xlabel, ylabel, title in one call)
   ax.set_xyt("Time (s)", "Amplitude (mV)", "EEG Signal")

   # Save (auto-exports CSV + YAML recipe)
   stx.io.save(fig, "figure.png")

Plot Types (47)
---------------

All ``ax.plot_*`` methods track their input data so it can be exported as CSV.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Category
     - Types
   * - **Line & Curve**
     - ``plot``, ``step``, ``fill``, ``fill_between``, ``fill_betweenx``, ``errorbar``, ``stackplot``, ``stairs``
   * - **Scatter & Points**
     - ``scatter``
   * - **Bar & Categorical**
     - ``bar``, ``barh``
   * - **Distribution**
     - ``hist``, ``hist2d``, ``boxplot``, ``violinplot``, ``ecdf``
   * - **2D Image & Matrix**
     - ``imshow``, ``matshow``, ``pcolor``, ``pcolormesh``, ``hexbin``, ``spy``
   * - **Contour & Surface**
     - ``contour``, ``contourf``, ``tricontour``, ``tricontourf``, ``tripcolor``, ``triplot``
   * - **Spectral & Signal**
     - ``specgram``, ``psd``, ``csd``, ``cohere``, ``angle_spectrum``, ``magnitude_spectrum``, ``phase_spectrum``, ``acorr``, ``xcorr``
   * - **Vector & Flow**
     - ``quiver``, ``barbs``, ``streamplot``
   * - **Special**
     - ``pie``, ``stem``, ``eventplot``, ``loglog``, ``semilogx``, ``semilogy``, ``graph``

Standard matplotlib methods (``ax.plot``, ``ax.scatter``, etc.) also work
and are tracked.

MM-Based Layout
---------------

Figures use millimeter dimensions for precise control:

.. code-block:: python

   fig, ax = stx.plt.subplots(
       axes_width_mm=80,
       axes_height_mm=60,
   )

   # Multi-panel with exact spacing
   fig, axes = stx.plt.subplots(
       nrows=2, ncols=3,
       axes_width_mm=50,
       axes_height_mm=40,
   )

Axis Helpers
------------

.. code-block:: python

   # Set xlabel, ylabel, title in one call
   ax.set_xyt("X Label", "Y Label", "Title")

   # Automatic axis label formatting with units
   ax.set_xyt("Frequency (Hz)", "Power (dB)", "Power Spectrum")

Figure Composition
------------------

Combine multiple figures into panels:

.. code-block:: python

   # Compose panels A, B, C
   stx.plt.compose(
       sources=["fig_a.png", "fig_b.png", "fig_c.png"],
       output_path="combined.png",
       layout="horizontal",
       panel_labels=True,
   )

Statistical Annotations
-----------------------

Add significance brackets to figures:

.. code-block:: python

   # In the declarative spec
   stat_annotations:
     - x1: 0
       x2: 1
       y: 5.5
       text: "***"
     - x1: 0
       x2: 2
       y: 6.5
       p_value: 0.02
       style: stars

Reproducible Figures
--------------------

When saved via ``stx.io.save``, figures get a ``.yaml`` recipe.
Reproduce any figure from its recipe:

.. code-block:: python

   stx.plt.reproduce("figure.yaml", output_path="reproduced.png")

Style Presets
-------------

.. code-block:: python

   import figrecipe as fr

   fr.load_style("SCITEX")       # Publication defaults
   fr.load_style("MATPLOTLIB")   # Standard matplotlib

See the :doc:`/gallery` for visual examples.

API Reference
-------------

See :doc:`/api/scitex.plt` for the auto-generated Python API.
