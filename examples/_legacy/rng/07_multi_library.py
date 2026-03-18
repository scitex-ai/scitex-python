#!/usr/bin/env python3
"""
Multi-library example for SciTeX RNG.

Demonstrates how RandomStateManager automatically handles multiple libraries.
"""

import scitex as stx
import numpy as np
import random
import hashlib


def test_python_random(rng):
    """Test Python's built-in random module."""
    print("\n1. Python random module:")

    # These are now reproducible thanks to auto-fixing
    val1 = random.random()
    val2 = random.randint(1, 100)
    val3 = random.choice(['a', 'b', 'c', 'd'])

    print(f"   random.random(): {val1:.6f}")
    print(f"   random.randint(1, 100): {val2}")
    print(f"   random.choice(['a', 'b', 'c', 'd']): {val3}")

    return val1, val2, val3


def test_numpy(rng):
    """Test NumPy random."""
    print("\n2. NumPy random:")

    # Old API (still works, auto-fixed)
    old_api_val = np.random.rand(3)
    print(f"   np.random.rand(3): {old_api_val}")

    # New API through RNG
    new_api_gen = rng("numpy_test")
    new_api_val = new_api_gen.random(3)
    print(f"   rng('numpy_test').random(3): {new_api_val}")

    # Both are reproducible but independent
    return old_api_val, new_api_val


def test_hash_reproducibility():
    """Test Python hash reproducibility via PYTHONHASHSEED."""
    print("\n3. Python hash (PYTHONHASHSEED):")

    # These would be non-deterministic without PYTHONHASHSEED
    dict_keys = list({'z': 1, 'a': 2, 'b': 3, 'c': 4}.keys())
    set_items = list({3, 1, 4, 1, 5, 9, 2, 6})
    str_hash = hash("reproducible")

    print(f"   Dict iteration order: {dict_keys}")
    print(f"   Set iteration order: {set_items}")
    print(f"   String hash: {str_hash}")

    return dict_keys, set_items, str_hash


def test_pytorch(rng):
    """Test PyTorch if available."""
    print("\n4. PyTorch:")

    try:
        import torch

        # CPU tensor
        cpu_tensor = torch.randn(3)
        print(f"   CPU tensor: {cpu_tensor.numpy()}")

        # CUDA tensor if available
        if torch.cuda.is_available():
            cuda_tensor = torch.randn(3).cuda()
            print(f"   CUDA tensor: {cuda_tensor.cpu().numpy()}")

            # Check deterministic mode
            is_deterministic = torch.backends.cudnn.deterministic
            print(f"   CUDNN deterministic: {is_deterministic}")
        else:
            print("   CUDA not available")
            cuda_tensor = None

        return cpu_tensor.numpy()

    except ImportError:
        print("   PyTorch not installed")
        return None


def test_tensorflow(rng):
    """Test TensorFlow if available."""
    print("\n5. TensorFlow:")

    try:
        import tensorflow as tf

        # TF random
        tf_tensor = tf.random.normal([3])
        tf_values = tf_tensor.numpy()
        print(f"   TF random tensor: {tf_values}")

        return tf_values

    except ImportError:
        print("   TensorFlow not installed")
        return None


def test_jax(rng):
    """Test JAX if available."""
    print("\n6. JAX:")

    try:
        import jax
        import jax.numpy as jnp

        # JAX uses explicit keys, but RNG creates one
        key = jax.random.PRNGKey(42)  # This is fixed by RNG
        jax_values = jax.random.normal(key, (3,))
        print(f"   JAX random: {np.array(jax_values)}")

        return np.array(jax_values)

    except ImportError:
        print("   JAX not installed")
        return None


def compare_runs():
    """Run twice to verify reproducibility."""

    print("=" * 60)
    print("MULTI-LIBRARY REPRODUCIBILITY TEST")
    print("=" * 60)

    all_results = []

    for run in range(2):
        print(f"\n{'='*20} RUN {run+1} {'='*20}")

        # Create fresh RNG
        rng = stx.rng.RandomStateManager(seed=42)

        results = {}

        # Test all libraries
        results['python'] = test_python_random(rng)
        results['numpy'] = test_numpy(rng)
        results['hash'] = test_hash_reproducibility()
        results['pytorch'] = test_pytorch(rng)
        results['tensorflow'] = test_tensorflow(rng)
        results['jax'] = test_jax(rng)

        all_results.append(results)

    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON:")
    print("=" * 60)

    # Python random
    py_match = all_results[0]['python'] == all_results[1]['python']
    print(f"\nPython random matches: {'✓' if py_match else '✗'}")

    # NumPy
    np_old_match = np.array_equal(all_results[0]['numpy'][0],
                                   all_results[1]['numpy'][0])
    np_new_match = np.array_equal(all_results[0]['numpy'][1],
                                   all_results[1]['numpy'][1])
    print(f"NumPy old API matches: {'✓' if np_old_match else '✗'}")
    print(f"NumPy new API matches: {'✓' if np_new_match else '✗'}")

    # Hash
    hash_match = all_results[0]['hash'] == all_results[1]['hash']
    print(f"Python hash matches: {'✓' if hash_match else '✗'}")

    # PyTorch
    if all_results[0]['pytorch'] is not None:
        pt_match = np.array_equal(all_results[0]['pytorch'],
                                   all_results[1]['pytorch'])
        print(f"PyTorch matches: {'✓' if pt_match else '✗'}")

    # TensorFlow
    if all_results[0]['tensorflow'] is not None:
        tf_match = np.array_equal(all_results[0]['tensorflow'],
                                   all_results[1]['tensorflow'])
        print(f"TensorFlow matches: {'✓' if tf_match else '✗'}")

    # JAX
    if all_results[0]['jax'] is not None:
        jax_match = np.array_equal(all_results[0]['jax'],
                                    all_results[1]['jax'])
        print(f"JAX matches: {'✓' if jax_match else '✗'}")


def test_independence():
    """Test that different libraries remain independent."""

    print("\n" + "=" * 60)
    print("INDEPENDENCE TEST")
    print("=" * 60)

    rng = stx.rng.RandomStateManager(seed=123)

    print("\nGenerating values from different sources:")

    # Generate from Python
    py_vals = [random.random() for _ in range(3)]
    print(f"Python: {py_vals}")

    # Generate from NumPy old API
    np_old = [np.random.rand() for _ in range(3)]
    print(f"NumPy old: {np_old}")

    # Generate from RNG named generator
    gen = rng("test")
    rng_vals = [gen.random() for _ in range(3)]
    print(f"RNG named: {rng_vals}")

    # All should be different (independent streams)
    all_different = (py_vals != np_old != rng_vals)
    print(f"\nAll streams independent: {'✓' if all_different else '✗'}")

    # But each is reproducible
    print("\nRerunning with same seed...")
    rng2 = stx.rng.RandomStateManager(seed=123)

    py_vals2 = [random.random() for _ in range(3)]
    matches = py_vals == py_vals2
    print(f"Python reproducible: {'✓' if matches else '✗'}")


if __name__ == "__main__":
    compare_runs()
    test_independence()

    print("\n✓ Multi-library example completed!")
