#!/usr/bin/env python3
"""
Example showing how to properly use RNG with pandas DataFrames for reproducible sampling.

This demonstrates the correct way to ensure reproducibility when:
1. Loading and filtering data
2. Random sampling from DataFrames
3. Verifying reproducibility
"""

import pandas as pd
import numpy as np
import scitex as stx


def generate_small_hash_table_wrong(n_samples=10):
    """
    WRONG: Uses np.random directly, breaking reproducibility.
    """
    data = {
        'patient_id': ['P001'] * 20 + ['P002'] * 20,
        'seizure_type': ['seizure'] * 10 + ['interictal_control'] * 10 +
                       ['seizure'] * 10 + ['interictal_control'] * 10,
        'value': np.random.random(40)  # WRONG: Uses global numpy random
    }
    df = pd.DataFrame(data)

    # WRONG: Uses np.random.permutation directly
    rand_indices = np.random.permutation(len(df))[:n_samples]
    return df.iloc[rand_indices]


def generate_small_hash_table_correct(rng, n_samples=10):
    """
    CORRECT: Uses RNG instance for all random operations.
    """
    # Get a named generator for this specific task
    data_gen = rng("data_generation")
    sample_gen = rng("sampling")

    # Generate data using RNG
    data = {
        'patient_id': ['P001'] * 20 + ['P002'] * 20,
        'seizure_type': ['seizure'] * 10 + ['interictal_control'] * 10 +
                       ['seizure'] * 10 + ['interictal_control'] * 10,
        'value': data_gen.random(40)  # CORRECT: Uses RNG generator
    }
    df = pd.DataFrame(data)

    # CORRECT: Use RNG for sampling
    rand_indices = sample_gen.permutation(len(df))[:n_samples]
    return df.iloc[rand_indices]


def main():
    """Demonstrate correct vs incorrect usage."""

    print("=" * 60)
    print("WRONG WAY - Using np.random directly")
    print("=" * 60)

    # Even with RNG initialized, using np.random directly breaks reproducibility
    rng1 = stx.rng.RandomStateManager(seed=42, verbose=True)

    # First run
    df_wrong1 = generate_small_hash_table_wrong(n_samples=5)
    print("\nFirst run - caching:")
    try:
        rng1.verify(df_wrong1, "wrong_method", verbose=True)
    except ValueError as e:
        print(f"Error (expected on second run): {e}")

    # Second run - will likely fail
    print("\nSecond run - likely to fail:")
    df_wrong2 = generate_small_hash_table_wrong(n_samples=5)
    try:
        result = rng1.verify(df_wrong2, "wrong_method", verbose=True)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"❌ Failed as expected: Reproducibility broken!")

    print("\n" + "=" * 60)
    print("CORRECT WAY - Using RNG instance")
    print("=" * 60)

    # Create new RNG for correct method
    rng2 = stx.rng.RandomStateManager(seed=42, verbose=True)

    # First run
    print("\nFirst run - caching:")
    df_correct1 = generate_small_hash_table_correct(rng2, n_samples=5)
    result1 = rng2.verify(df_correct1, "correct_method", verbose=True)
    print(f"Result: {result1}")
    print(f"Sample data:\n{df_correct1.head()}")

    # Create fresh RNG with same seed
    print("\nSecond run with fresh RNG (same seed):")
    rng3 = stx.rng.RandomStateManager(seed=42, verbose=False)
    df_correct2 = generate_small_hash_table_correct(rng3, n_samples=5)
    result2 = rng2.verify(df_correct2, "correct_method", verbose=True)
    print(f"Result: {result2}")

    # Verify data is identical
    print(f"\nDataFrames are identical: {df_correct1.equals(df_correct2)}")

    print("\n" + "=" * 60)
    print("KEY LESSONS:")
    print("=" * 60)
    print("1. Always use RNG instance for random operations")
    print("2. Use named generators: rng('name')")
    print("3. Never use np.random.* directly")
    print("4. Pass RNG to functions that need randomness")
    print("5. Verification with verbose=True will raise error on mismatch")


if __name__ == "__main__":
    main()
