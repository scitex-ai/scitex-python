Plot Gallery
============

``stx.plt`` wraps matplotlib axes with data-tracking methods.
All ``plot_*`` methods record data for automatic CSV export.

Generate the full gallery locally:

.. code-block:: python

   import scitex as stx
   stx.plt.gallery.generate(output_dir="./gallery")

Line Plots
----------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/line/stx_line.png
          :width: 100%

          ``ax.plot_line(x, y)``

     - .. figure:: _static/gallery/line/stx_shaded_line.png
          :width: 100%

          ``ax.plot_shaded_line(x, y_mean, y_std)``

   * - .. figure:: _static/gallery/line/plot.png
          :width: 100%

          ``ax.plot(x, y)`` (standard matplotlib)

     - .. figure:: _static/gallery/line/step.png
          :width: 100%

          ``ax.step(x, y)``

Statistical Plots
-----------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/statistical/stx_mean_std.png
          :width: 100%

          ``ax.plot_mean_std(groups)``

     - .. figure:: _static/gallery/statistical/stx_mean_ci.png
          :width: 100%

          ``ax.plot_mean_ci(groups)``

   * - .. figure:: _static/gallery/statistical/stx_median_iqr.png
          :width: 100%

          ``ax.plot_median_iqr(groups)``

     - .. figure:: _static/gallery/statistical/stx_errorbar.png
          :width: 100%

          ``ax.plot_errorbar(x, y, yerr)``

Distribution Plots
------------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/distribution/stx_kde.png
          :width: 100%

          ``ax.plot_kde(data)``

     - .. figure:: _static/gallery/distribution/stx_ecdf.png
          :width: 100%

          ``ax.plot_ecdf(data)``

   * - .. figure:: _static/gallery/distribution/stx_joyplot.png
          :width: 100%

          ``ax.plot_joyplot(groups)``

     - .. figure:: _static/gallery/distribution/hist.png
          :width: 100%

          ``ax.hist(data)``

Categorical Plots
-----------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/categorical/stx_violin.png
          :width: 100%

          ``ax.plot_violin(groups)``

     - .. figure:: _static/gallery/categorical/stx_box.png
          :width: 100%

          ``ax.plot_box(groups)``

   * - .. figure:: _static/gallery/categorical/stx_bar.png
          :width: 100%

          ``ax.plot_bar(labels, values)``

     - .. figure:: _static/gallery/categorical/stx_barh.png
          :width: 100%

          ``ax.plot_barh(labels, values)``

Scatter Plots
-------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/scatter/stx_scatter.png
          :width: 100%

          ``ax.plot_scatter(x, y)``

     - .. figure:: _static/gallery/scatter/scatter.png
          :width: 100%

          ``ax.scatter(x, y)`` (standard matplotlib)

Heatmaps and Grids
-------------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/grid/stx_heatmap.png
          :width: 100%

          ``ax.plot_heatmap(matrix)``

     - .. figure:: _static/gallery/grid/stx_conf_mat.png
          :width: 100%

          ``ax.plot_conf_mat(cm)``

   * - .. figure:: _static/gallery/grid/stx_image.png
          :width: 100%

          ``ax.plot_image(img)``

     - .. figure:: _static/gallery/grid/stx_imshow.png
          :width: 100%

          ``ax.plot_imshow(data)``

Area Plots
----------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/area/stx_fill_between.png
          :width: 100%

          ``ax.plot_fill_between(x, y1, y2)``

     - .. figure:: _static/gallery/area/stx_fillv.png
          :width: 100%

          ``ax.plot_fillv(x_start, x_end)``

Special Plots
-------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/special/stx_raster.png
          :width: 100%

          ``ax.plot_raster(spike_times)``

     - .. figure:: _static/gallery/special/stx_rectangle.png
          :width: 100%

          ``ax.plot_rectangle(xy, w, h)``

Contour and Vector Plots
-------------------------

.. list-table::
   :widths: 50 50

   * - .. figure:: _static/gallery/contour/stx_contour.png
          :width: 100%

          ``ax.plot_contour(x, y, z)``

     - .. figure:: _static/gallery/vector/quiver.png
          :width: 100%

          ``ax.quiver(x, y, u, v)``
