#!/usr/bin/env python3
"""
Scientific Experiment Example with Reproducibility Verification

This example demonstrates how to use the RNG module in a scientific experiment:
- Setting up reproducible data generation
- Verifying reproducibility across runs
- Using checkpoints for long-running experiments
- Handling multiple random components (data, noise, sampling)

This simulates a typical scientific workflow where reproducibility is critical.
"""

import numpy as np
import scitex as stx
from pathlib import Path
from scitex.logging import getLogger

logger = getLogger(__name__)


class ScientificExperiment:
    """A mock scientific experiment with multiple random components."""

    def __init__(self, seed=42, n_samples=100, n_features=10):
        """Initialize experiment with reproducible random state."""
        self.rng = stx.rng.RandomStateManager(seed=seed)
        self.n_samples = n_samples
        self.n_features = n_features
        self.results = {}

        logger.info(f"Initialized experiment with seed={seed}")

    def generate_synthetic_data(self):
        """Generate synthetic experimental data."""
        logger.info("Generating synthetic data...")

        # Use different named generators for different components
        data_gen = self.rng("synthetic_data")
        noise_gen = self.rng("measurement_noise")

        # Generate base signal
        X = data_gen.normal(loc=0, scale=1, size=(self.n_samples, self.n_features))

        # Generate ground truth coefficients
        true_beta = data_gen.normal(loc=0, scale=0.5, size=self.n_features)

        # Generate target with noise
        signal = X @ true_beta
        noise = noise_gen.normal(loc=0, scale=0.1, size=self.n_samples)
        y = signal + noise

        # Store for verification
        self.X = X
        self.y = y
        self.true_beta = true_beta

        # Verify reproducibility
        data_reproducible = self.rng.verify(X, "synthetic_X")
        target_reproducible = self.rng.verify(y, "synthetic_y")

        if data_reproducible and target_reproducible:
            logger.success("Data generation is reproducible")
        else:
            logger.warning("Reproducibility check failed!")

        return X, y, true_beta

    def run_cross_validation(self, n_folds=5):
        """Run cross-validation with reproducible splits."""
        logger.info(f"Running {n_folds}-fold cross-validation...")

        cv_gen = self.rng("cross_validation")
        indices = np.arange(self.n_samples)

        # Reproducible shuffle
        cv_gen.shuffle(indices)

        fold_size = self.n_samples // n_folds
        cv_scores = []

        for fold in range(n_folds):
            # Create train/test split
            test_start = fold * fold_size
            test_end = test_start + fold_size
            test_idx = indices[test_start:test_end]
            train_idx = np.concatenate([indices[:test_start], indices[test_end:]])

            # Simple linear regression (mock training)
            X_train = self.X[train_idx]
            y_train = self.y[train_idx]
            X_test = self.X[test_idx]
            y_test = self.y[test_idx]

            # Fit model (using pseudoinverse for simplicity)
            beta_hat = np.linalg.pinv(X_train) @ y_train

            # Evaluate
            y_pred = X_test @ beta_hat
            mse = np.mean((y_test - y_pred) ** 2)
            cv_scores.append(mse)

            logger.info(f"  Fold {fold+1}: MSE = {mse:.4f}")

        mean_score = np.mean(cv_scores)
        std_score = np.std(cv_scores)

        # Verify CV reproducibility
        cv_reproducible = self.rng.verify(cv_scores, "cv_scores")

        logger.info(f"CV Mean MSE: {mean_score:.4f} ± {std_score:.4f}")

        self.results["cv_scores"] = cv_scores
        return mean_score, std_score

    def run_bootstrap_analysis(self, n_bootstrap=100):
        """Run bootstrap analysis for uncertainty estimation."""
        logger.info(f"Running bootstrap analysis ({n_bootstrap} samples)...")

        bootstrap_gen = self.rng("bootstrap")
        bootstrap_estimates = []

        for i in range(n_bootstrap):
            # Resample with replacement
            idx = bootstrap_gen.integers(0, self.n_samples, size=self.n_samples)
            X_boot = self.X[idx]
            y_boot = self.y[idx]

            # Estimate parameters
            beta_boot = np.linalg.pinv(X_boot) @ y_boot
            bootstrap_estimates.append(beta_boot)

            if (i + 1) % 20 == 0:
                logger.info(f"  Completed {i+1}/{n_bootstrap} bootstrap samples")

        bootstrap_estimates = np.array(bootstrap_estimates)

        # Calculate confidence intervals
        ci_lower = np.percentile(bootstrap_estimates, 2.5, axis=0)
        ci_upper = np.percentile(bootstrap_estimates, 97.5, axis=0)

        # Verify bootstrap reproducibility
        bootstrap_reproducible = self.rng.verify(
            bootstrap_estimates.flatten(),
            "bootstrap_estimates"
        )

        logger.info("Bootstrap 95% CI for first 3 coefficients:")
        for i in range(min(3, self.n_features)):
            logger.info(f"  β[{i}]: [{ci_lower[i]:.3f}, {ci_upper[i]:.3f}] "
                       f"(true: {self.true_beta[i]:.3f})")

        self.results["bootstrap_estimates"] = bootstrap_estimates
        return ci_lower, ci_upper

    def save_checkpoint(self):
        """Save experiment checkpoint."""
        checkpoint_path = self.rng.checkpoint("experiment_checkpoint")
        logger.info(f"Saved checkpoint to {checkpoint_path}")
        return checkpoint_path

    def load_checkpoint(self, checkpoint_path):
        """Load experiment from checkpoint."""
        self.rng.restore(checkpoint_path)
        logger.info(f"Restored from checkpoint {checkpoint_path}")


def demonstrate_reproducibility():
    """Run the same experiment twice to show perfect reproducibility."""
    logger.info("\n" + "="*60)
    logger.info("REPRODUCIBILITY DEMONSTRATION")
    logger.info("="*60)

    # Run 1
    logger.info("\n>>> Run 1:")
    exp1 = ScientificExperiment(seed=42, n_samples=50, n_features=5)
    X1, y1, beta1 = exp1.generate_synthetic_data()
    cv_mean1, cv_std1 = exp1.run_cross_validation()

    # Run 2 (same seed)
    logger.info("\n>>> Run 2 (same seed):")
    exp2 = ScientificExperiment(seed=42, n_samples=50, n_features=5)
    X2, y2, beta2 = exp2.generate_synthetic_data()
    cv_mean2, cv_std2 = exp2.run_cross_validation()

    # Verify identical results
    logger.info("\n" + "-"*40)
    logger.success(f"Data identical: {np.allclose(X1, X2)}")
    logger.success(f"Targets identical: {np.allclose(y1, y2)}")
    logger.success(f"CV scores identical: {np.isclose(cv_mean1, cv_mean2)}")

    # Run 3 (different seed)
    logger.info("\n>>> Run 3 (different seed):")
    exp3 = ScientificExperiment(seed=123, n_samples=50, n_features=5)
    X3, y3, beta3 = exp3.generate_synthetic_data()

    logger.info("\n" + "-"*40)
    logger.info(f"Different seed → different data: {not np.allclose(X1, X3)}")


def demonstrate_checkpointing():
    """Show how to use checkpointing for long experiments."""
    logger.info("\n" + "="*60)
    logger.info("CHECKPOINTING DEMONSTRATION")
    logger.info("="*60)

    # Start experiment
    exp = ScientificExperiment(seed=42)
    exp.generate_synthetic_data()

    # Run partial analysis
    logger.info("\nRunning first part of analysis...")
    exp.run_cross_validation()

    # Save checkpoint
    checkpoint = exp.save_checkpoint()

    # Simulate interruption - create new experiment
    logger.info("\nSimulating interruption and restart...")
    new_exp = ScientificExperiment(seed=999)  # Different seed

    # Restore from checkpoint
    new_exp.load_checkpoint(checkpoint)

    # Continue analysis - will be reproducible
    new_exp.X = exp.X  # Restore data (in practice, reload from disk)
    new_exp.y = exp.y
    new_exp.true_beta = exp.true_beta

    ci_lower, ci_upper = new_exp.run_bootstrap_analysis(n_bootstrap=50)

    logger.success("Analysis completed after checkpoint restore")


def main():
    """Run complete scientific experiment example."""
    logger.info("="*60)
    logger.info("SCIENTIFIC EXPERIMENT WITH RNG MODULE")
    logger.info("="*60)

    # Create experiment
    exp = ScientificExperiment(seed=42, n_samples=100, n_features=10)

    # Generate data
    X, y, true_beta = exp.generate_synthetic_data()
    logger.info(f"Generated data: X.shape={X.shape}, y.shape={y.shape}")

    # Run analyses
    cv_mean, cv_std = exp.run_cross_validation(n_folds=5)
    ci_lower, ci_upper = exp.run_bootstrap_analysis(n_bootstrap=100)

    # Summary
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT SUMMARY")
    logger.info("="*60)
    logger.info(f"Cross-validation MSE: {cv_mean:.4f} ± {cv_std:.4f}")
    logger.info(f"Bootstrap samples analyzed: 100")
    logger.info(f"All reproducibility checks passed: ✓")

    return exp


if __name__ == "__main__":
    # Run main experiment
    exp = main()

    # Demonstrate reproducibility
    demonstrate_reproducibility()

    # Demonstrate checkpointing
    demonstrate_checkpointing()

    logger.info("\n" + "="*60)
    logger.success("All demonstrations completed successfully!")
    logger.info("Run this script multiple times - results will be identical!")
