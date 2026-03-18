#!/usr/bin/env python3
"""
Example showing library-specific generator methods.

Demonstrates how to get appropriate random generators/seeds for different libraries.
"""

import scitex as stx
import numpy as np


def demonstrate_numpy():
    """Show NumPy generator usage."""
    print("=" * 60)
    print("NumPy Generators")
    print("=" * 60)

    rng = stx.rng.RandomStateManager(seed=42, verbose=False)

    # Get named NumPy generators
    data_gen = rng.get_np_generator("data")
    model_gen = rng.get_np_generator("model")

    # Use them
    data = data_gen.random((5, 3))
    weights = model_gen.normal(0, 0.1, size=(3, 2))
    permutation = data_gen.permutation(10)

    print(f"Data shape: {data.shape}")
    print(f"Weights shape: {weights.shape}")
    print(f"Permutation: {permutation}")
    print()


def demonstrate_sklearn():
    """Show scikit-learn random state usage."""
    print("=" * 60)
    print("Scikit-learn Random States")
    print("=" * 60)

    try:
        from sklearn.model_selection import train_test_split, KFold
        from sklearn.ensemble import RandomForestClassifier

        rng = stx.rng.RandomStateManager(seed=42, verbose=False)

        # Generate sample data
        np_gen = rng.get_np_generator("data")
        X = np_gen.random((100, 10))
        y = np_gen.integers(0, 2, size=100)

        # Use sklearn with named random states
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=rng.get_sklearn_random_state("split")
        )

        # Cross-validation with different seed
        kfold = KFold(
            n_splits=5,
            shuffle=True,
            random_state=rng.get_sklearn_random_state("cv")
        )

        # Model with its own seed
        model = RandomForestClassifier(
            n_estimators=10,
            random_state=rng.get_sklearn_random_state("model")
        )

        print(f"Train size: {X_train.shape}")
        print(f"Test size: {X_test.shape}")
        print(f"CV splits: {kfold.get_n_splits()}")
        print(f"Model: {model.__class__.__name__}")
        print()

    except ImportError:
        print("Scikit-learn not installed")
        print()


def demonstrate_pytorch():
    """Show PyTorch generator usage."""
    print("=" * 60)
    print("PyTorch Generators")
    print("=" * 60)

    try:
        import torch

        rng = stx.rng.RandomStateManager(seed=42, verbose=False)

        # Get named PyTorch generators
        model_gen = rng.get_torch_generator("model_init")
        dropout_gen = rng.get_torch_generator("dropout")

        # Use with torch functions
        weights = torch.randn(5, 3, generator=model_gen)
        dropout_mask = torch.rand(5, generator=dropout_gen) > 0.2

        print(f"Weights shape: {weights.shape}")
        print(f"Dropout mask shape: {dropout_mask.shape}")
        print(f"Dropout rate: {(~dropout_mask).float().mean():.2f}")
        print()

    except ImportError:
        print("PyTorch not installed")
        print()


def demonstrate_mixed_usage():
    """Show how different libraries work together."""
    print("=" * 60)
    print("Mixed Library Usage")
    print("=" * 60)

    rng = stx.rng.RandomStateManager(seed=42, verbose=False)

    # NumPy for data generation
    data_gen = rng.get_np_generator("data")
    X = data_gen.random((100, 10))
    y = data_gen.integers(0, 2, size=100)

    print(f"Generated data: X={X.shape}, y={y.shape}")

    # Scikit-learn for splitting
    try:
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=rng.get_sklearn_random_state("split")
        )
        print(f"Split data: train={X_train.shape}, test={X_test.shape}")
    except ImportError:
        print("Scikit-learn not installed, skipping split")

    # PyTorch for model initialization
    try:
        import torch

        model_gen = rng.get_torch_generator("model")
        weights = torch.randn(10, 5, generator=model_gen)
        print(f"Model weights: {weights.shape}")
    except ImportError:
        print("PyTorch not installed, skipping weights")

    print()


def demonstrate_reproducibility():
    """Show that named generators are reproducible."""
    print("=" * 60)
    print("Reproducibility Test")
    print("=" * 60)

    # First run
    rng1 = stx.rng.RandomStateManager(seed=123, verbose=False)

    gen1 = rng1.get_np_generator("test")
    np_vals1 = gen1.random(5)

    sklearn_seed1 = rng1.get_sklearn_random_state("test")

    # Second run with same seed
    rng2 = stx.rng.RandomStateManager(seed=123, verbose=False)

    gen2 = rng2.get_np_generator("test")
    np_vals2 = gen2.random(5)

    sklearn_seed2 = rng2.get_sklearn_random_state("test")

    # Check reproducibility
    print(f"NumPy values match: {np.array_equal(np_vals1, np_vals2)}")
    print(f"Sklearn seeds match: {sklearn_seed1 == sklearn_seed2}")

    # Show that different names give different results
    gen3 = rng2.get_np_generator("different")
    np_vals3 = gen3.random(5)
    print(f"Different name gives different values: {not np.array_equal(np_vals1, np_vals3)}")
    print()


def main():
    """Run all demonstrations."""
    print("\nLibrary-Specific Random Generators Example")
    print("=" * 60)
    print()

    demonstrate_numpy()
    demonstrate_sklearn()
    demonstrate_pytorch()
    demonstrate_mixed_usage()
    demonstrate_reproducibility()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("Use the appropriate method for each library:")
    print("  - rng.get_np_generator(name)       -> NumPy Generator")
    print("  - rng.get_sklearn_random_state(name) -> int for sklearn")
    print("  - rng.get_torch_generator(name)    -> torch.Generator")
    print()
    print("Each method ensures reproducible, independent random streams!")


if __name__ == "__main__":
    main()
