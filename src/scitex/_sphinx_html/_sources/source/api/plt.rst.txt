scitex.plt
==========

Figure and Axis Creation
------------------------

.. autofunction:: scitex.plt.subplots

.. autofunction:: scitex.plt.figure

Gallery
-------

.. automodule:: scitex.plt.gallery
   :members:
   :undoc-members:

Axis Methods
------------

The following methods are available on ``ax`` objects returned by ``stx.plt.subplots()``.

Line Plots
~~~~~~~~~~

.. code-block:: python

   fig, ax = stx.plt.subplots()

.. py:method:: ax.stx_line(values_1d, xx=None, track=True, id=None, **kwargs)

   Plot a simple line from 1D array.

   :param values_1d: Y values
   :param xx: Optional X values
   :param track: Track data for CSV export
   :param id: Identifier for tracking

.. py:method:: ax.stx_shaded_line(xs, ys_lower, ys_middle, ys_upper, color=None, label=None, track=True, id=None, **kwargs)

   Plot a line with shaded area between bounds.

   :param xs: X values
   :param ys_lower: Lower bound Y values
   :param ys_middle: Middle line Y values
   :param ys_upper: Upper bound Y values

Statistical Plots
~~~~~~~~~~~~~~~~~

.. py:method:: ax.stx_mean_std(values_2d, xx=None, sd=1, track=True, id=None, **kwargs)

   Plot mean line with standard deviation shading.

   :param values_2d: 2D array (samples x timepoints)
   :param xx: Optional X values
   :param sd: Number of standard deviations for shading

.. py:method:: ax.stx_mean_ci(values_2d, xx=None, perc=95, track=True, id=None, **kwargs)

   Plot mean line with confidence interval shading.

   :param values_2d: 2D array (samples x timepoints)
   :param xx: Optional X values
   :param perc: Confidence interval percentage (default: 95)

.. py:method:: ax.stx_median_iqr(values_2d, xx=None, track=True, id=None, **kwargs)

   Plot median line with interquartile range shading.

   :param values_2d: 2D array (samples x timepoints)
   :param xx: Optional X values

.. py:method:: ax.stx_errorbar(x, y, yerr=None, xerr=None, track=True, id=None, **kwargs)

   Error bar plot with scitex styling.

   :param x: X coordinates
   :param y: Y coordinates
   :param yerr: Y error values
   :param xerr: X error values

Distribution Plots
~~~~~~~~~~~~~~~~~~

.. py:method:: ax.stx_kde(values_1d, cumulative=False, fill=False, track=True, id=None, **kwargs)

   Plot kernel density estimate.

   :param values_1d: 1D array of values
   :param cumulative: Plot cumulative distribution
   :param fill: Fill under curve

.. py:method:: ax.stx_ecdf(values_1d, track=True, id=None, **kwargs)

   Plot empirical cumulative distribution function.

   :param values_1d: 1D array of values

.. py:method:: ax.hist(x, bins=10, range=None, align_bins=True, track=True, id=None, **kwargs)

   Plot histogram with bin alignment support.

   :param x: Input data
   :param bins: Number of bins or bin edges
   :param align_bins: Align bins with other histograms on same axis

Categorical Plots
~~~~~~~~~~~~~~~~~

.. py:method:: ax.stx_box(values_list, colors=None, track=True, id=None, **kwargs)

   Boxplot with scitex styling.

   :param values_list: List of arrays for each box
   :param colors: Optional colors for boxes

.. py:method:: ax.stx_violin(values_list, x=None, y=None, hue=None, labels=None, colors=None, half=False, track=True, id=None, **kwargs)

   Violin plot with scitex styling.

   :param values_list: List of arrays or DataFrame
   :param half: Show half violins

Scatter Plots
~~~~~~~~~~~~~

.. py:method:: ax.stx_scatter(x, y, track=True, id=None, **kwargs)

   Scatter plot with scitex styling.

   :param x: X coordinates
   :param y: Y coordinates

.. py:method:: ax.stx_scatter_hist(x, y, hist_bins=20, scatter_alpha=0.6, track=True, id=None, **kwargs)

   Scatter plot with marginal histograms.

   :param x: X coordinates
   :param y: Y coordinates
   :param hist_bins: Number of histogram bins

Bar Plots
~~~~~~~~~

.. py:method:: ax.stx_bar(x, height, track=True, id=None, **kwargs)

   Vertical bar plot with scitex styling.

   :param x: X coordinates
   :param height: Bar heights

.. py:method:: ax.stx_barh(y, width, track=True, id=None, **kwargs)

   Horizontal bar plot with scitex styling.

   :param y: Y coordinates
   :param width: Bar widths

Heatmaps
~~~~~~~~

.. py:method:: ax.stx_heatmap(values_2d, x_labels=None, y_labels=None, cmap="viridis", cbar_label="", show_annot=True, track=True, id=None, **kwargs)

   Plot annotated heatmap.

   :param values_2d: 2D array
   :param x_labels: Column labels
   :param y_labels: Row labels
   :param show_annot: Show value annotations

.. py:method:: ax.stx_conf_mat(conf_mat_2d, x_labels=None, y_labels=None, title="Confusion Matrix", track=True, id=None, **kwargs)

   Plot confusion matrix.

   :param conf_mat_2d: 2D confusion matrix array
   :param x_labels: Predicted class labels
   :param y_labels: True class labels

.. py:method:: ax.stx_image(arr_2d, track=True, id=None, **kwargs)

   Display 2D array as image.

   :param arr_2d: 2D array

Special Plots
~~~~~~~~~~~~~

.. py:method:: ax.stx_raster(spike_times_list, time=None, labels=None, colors=None, track=True, id=None, **kwargs)

   Plot spike raster.

   :param spike_times_list: List of spike time arrays per neuron
   :param time: Optional time array

.. py:method:: ax.stx_fillv(starts_1d, ends_1d, color="red", alpha=0.2, track=True, id=None, **kwargs)

   Fill vertical regions.

   :param starts_1d: Start positions
   :param ends_1d: End positions

.. py:method:: ax.stx_rectangle(xx, yy, width, height, track=True, id=None, **kwargs)

   Draw rectangle.

   :param xx: X position
   :param yy: Y position
   :param width: Rectangle width
   :param height: Rectangle height

.. py:method:: ax.stx_joyplot(arrays, track=True, id=None, **kwargs)

   Plot joyplot (ridgeline plot).

   :param arrays: List of arrays

Seaborn Wrappers
~~~~~~~~~~~~~~~~

.. py:method:: ax.sns_barplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_boxplot(data=None, x=None, y=None, strip=False, track=True, id=None, **kwargs)
.. py:method:: ax.sns_violinplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_stripplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_swarmplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_heatmap(*args, xyz=False, track=True, id=None, **kwargs)
.. py:method:: ax.sns_histplot(data=None, x=None, y=None, bins=10, track=True, id=None, **kwargs)
.. py:method:: ax.sns_kdeplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_scatterplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_lineplot(data=None, x=None, y=None, track=True, id=None, **kwargs)
.. py:method:: ax.sns_jointplot(*args, track=True, id=None, **kwargs)
.. py:method:: ax.sns_pairplot(*args, track=True, id=None, **kwargs)

Axis Utilities
~~~~~~~~~~~~~~

.. py:method:: ax.set_xyt(x=None, y=None, t=None)

   Set xlabel, ylabel, and title in one call.

.. py:method:: ax.hide_spines(*spines)

   Hide specified spines (top, right, bottom, left).
