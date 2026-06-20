AI Module (``stx.ai``)
======================

Machine learning utilities for training, classification, and metrics
with PyTorch and scikit-learn.

Quick Reference
---------------

.. code-block:: python

   import scitex as stx

   # Training utilities
   from scitex.ai import LearningCurveLogger, EarlyStopping

   logger = LearningCurveLogger()
   stopper = EarlyStopping(patience=10, direction="minimize")

   for epoch in range(100):
       # ... training loop ...
       logger({"loss": loss, "acc": acc}, step="Training")
       if stopper(val_loss, {"model": model_path}, epoch):
           break

   logger.plot_learning_curves(spath="curves.png")

   # Classification
   from scitex.ai import ClassificationReporter, Classifier

   clf = Classifier()("SVC")
   reporter = ClassificationReporter(output_dir="./results")
   reporter.calculate_metrics(y_true, y_pred, y_proba)
   reporter.save_summary()

Training
--------

- ``LearningCurveLogger`` -- Track and visualize training/validation/test metrics across epochs
- ``EarlyStopping`` -- Monitor validation metrics and stop when improvement plateaus

Classification
--------------

- ``ClassificationReporter`` -- Unified reporter for single/multi-task classification (balanced accuracy, MCC, ROC-AUC, confusion matrices)
- ``Classifier`` -- Factory for scikit-learn classifiers (SVC, KNN, Logistic Regression, AdaBoost, ...)
- ``CrossValidationExperiment`` -- Cross-validation framework

Metrics
-------

Standardized ``calc_*`` functions:

- ``calc_bacc`` -- Balanced accuracy
- ``calc_mcc`` -- Matthews Correlation Coefficient
- ``calc_conf_mat`` -- Confusion matrix
- ``calc_roc_auc`` -- ROC-AUC score
- ``calc_pre_rec_auc`` -- Precision-Recall AUC
- ``calc_feature_importance`` -- Feature importance scores

Visualization
-------------

- ``plot_learning_curve`` -- Training/validation curves
- ``stx_conf_mat`` -- Confusion matrix heatmap
- ``plot_roc_curve`` -- ROC curve
- ``plot_pre_rec_curve`` -- Precision-Recall curve
- ``plot_feature_importance`` -- Feature importance bar plots

Other
-----

- ``MultiTaskLoss`` -- Multi-task learning loss weighting
- ``get_optimizer`` / ``set_optimizer`` -- Optimizer management
- ``GenAI`` -- Generative AI wrapper (lazy-loaded)
- Clustering: ``pca``, ``umap``

API Reference
-------------

.. automodule:: scitex.ai
   :members:
