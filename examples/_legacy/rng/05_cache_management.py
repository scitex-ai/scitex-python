#!/usr/bin/env python3
"""
Example demonstrating cache management for reproducibility verification.

Shows how to use the clear_cache() method to manage verification cache.
"""

import scitex as stx
import numpy as np


def demonstrate_cache_management():
    """Show cache management functionality."""
    print("=" * 60)
    print("Cache Management Example")
    print("=" * 60)

    # Initialize RNG
    rng = stx.rng.RandomStateManager(seed=42, verbose=False)

    # Generate some data
    print("\n1. Generating data...")
    data1 = rng.get_np_generator("experiment_1").random(100)
    data2 = rng.get_np_generator("experiment_2").random(100)
    data3 = rng.get_np_generator("test_1").random(100)
    data4 = rng.get_np_generator("test_2").random(100)

    # Verify data (creates cache)
    print("\n2. Verifying data (creating cache)...")
    rng.verify(data1, "experiment_1", verbose=False)
    rng.verify(data2, "experiment_2", verbose=False)
    rng.verify(data3, "test_1", verbose=False)
    rng.verify(data4, "test_2", verbose=False)
    print("   Cache files created for: experiment_1, experiment_2, test_1, test_2")

    # Clear specific cache
    print("\n3. Clearing specific cache entry...")
    count = rng.clear_cache("test_1")
    print(f"   Removed {count} cache file(s) for 'test_1'")

    # Clear with pattern
    print("\n4. Clearing cache with pattern...")
    count = rng.clear_cache("experiment_*")
    print(f"   Removed {count} cache file(s) matching 'experiment_*'")

    # Clear multiple specific entries
    print("\n5. Creating new cache and clearing multiple...")
    # Create new cache
    data5 = rng.get_np_generator("analysis_1").random(50)
    data6 = rng.get_np_generator("analysis_2").random(50)
    rng.verify(data5, "analysis_1", verbose=False)
    rng.verify(data6, "analysis_2", verbose=False)

    count = rng.clear_cache(["analysis_1", "analysis_2"])
    print(f"   Removed {count} cache file(s) for specific list")

    # Clear all cache
    print("\n6. Clearing all cache...")
    # First create some more cache
    rng.verify(data1, "final_1", verbose=False)
    rng.verify(data2, "final_2", verbose=False)

    count = rng.clear_cache()  # Clear all
    print(f"   Removed {count} cache file(s) (all cache cleared)")

    print("\n" + "=" * 60)


def demonstrate_verification_workflow():
    """Show typical verification workflow with cache management."""
    print("\n" + "=" * 60)
    print("Verification Workflow Example")
    print("=" * 60)

    # Initial run
    print("\n1. Initial run - creating baseline...")
    rng = stx.rng.RandomStateManager(seed=123, verbose=False)

    # Simulate experiment
    data = rng.get_np_generator("experiment").random(1000)
    processed = data * 2 + 1  # Some processing

    # Verify (first time - creates cache)
    result = rng.verify(processed, "processed_data", verbose=False)
    print(f"   First verification: {'Cached' if result else 'Failed'}")

    # Second run - should match
    print("\n2. Second run - verifying reproducibility...")
    rng2 = stx.rng.RandomStateManager(seed=123, verbose=False)

    data2 = rng2.get_np_generator("experiment").random(1000)
    processed2 = data2 * 2 + 1

    result = rng2.verify(processed2, "processed_data", verbose=False)
    print(f"   Reproducibility check: {'✓ Passed' if result else '✗ Failed'}")

    # Simulate broken reproducibility
    print("\n3. Testing broken reproducibility...")
    rng3 = stx.rng.RandomStateManager(seed=456, verbose=False)  # Different seed!

    data3 = rng3.get_np_generator("experiment").random(1000)
    processed3 = data3 * 2 + 1

    result = rng3.verify(processed3, "processed_data", verbose=False)
    print(f"   Reproducibility check: {'✓ Passed' if result else '✗ Failed (expected)'}")

    # Clear cache to start fresh
    print("\n4. Clearing cache for fresh start...")
    count = rng3.clear_cache("processed_data")
    print(f"   Cleared {count} cache file(s)")

    # New baseline after clearing
    result = rng3.verify(processed3, "processed_data", verbose=False)
    print(f"   New baseline created: {'Cached' if result else 'Failed'}")

    print("\n" + "=" * 60)


def main():
    """Run all demonstrations."""
    print("\nRNG Cache Management Examples")
    print("=" * 60)

    demonstrate_cache_management()
    demonstrate_verification_workflow()

    print("\nSummary")
    print("=" * 60)
    print("Use clear_cache() to manage verification cache:")
    print("  - rng.clear_cache()           # Clear all")
    print("  - rng.clear_cache('name')     # Clear specific")
    print("  - rng.clear_cache('pattern*') # Clear pattern")
    print("  - rng.clear_cache(['a', 'b']) # Clear multiple")
    print()
    print("This helps manage reproducibility verification")
    print("and reset baselines when needed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
