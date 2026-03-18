#!/usr/bin/env python3
"""
Basic Usage Example for SciTeX RNG Module

This example demonstrates the fundamental features of the RNG module:
- Creating and using a RandomStateManager
- Getting named generators for different purposes
- Ensuring reproducibility across runs

Run this example multiple times - you should get identical output each time!
"""

import numpy as np
import scitex as stx
from scitex.logging import getLogger

logger = getLogger(__name__)


def main():
    """Demonstrate basic RNG usage."""

    # Method 1: Create a standalone RandomStateManager
    logger.info("Method 1: Direct RandomStateManager creation")
    rng = stx.rng.RandomStateManager(seed=42)

    # Get named generators for different purposes
    # Each name gets its own deterministic seed derived from the main seed
    data_gen = rng("data")
    model_gen = rng("model")
    augment_gen = rng("augment")

    # Generate some random data
    train_data = data_gen.random((5, 3))
    logger.info(f"Training data shape: {train_data.shape}")
    logger.info(f"First 3 values: {train_data.flat[:3]}")

    # Generate model weights
    weights = model_gen.normal(loc=0, scale=0.1, size=(3, 2))
    logger.info(f"Model weights shape: {weights.shape}")
    logger.info(f"Weight mean: {weights.mean():.4f}, std: {weights.std():.4f}")

    # Generate augmentation noise
    noise = augment_gen.uniform(-0.01, 0.01, size=(5, 3))
    augmented_data = train_data + noise
    logger.info(f"Augmented data differs by max: {np.abs(train_data - augmented_data).max():.6f}")

    # Method 2: Using the global instance
    logger.info("\nMethod 2: Global RandomStateManager")
    global_rng = stx.rng.get()  # Gets or creates global instance

    # Generate some data with global instance
    global_data = global_rng("experiment").random(10)
    logger.info(f"Global data first 3 values: {global_data[:3]}")

    # Method 3: Reset global with new seed
    logger.info("\nMethod 3: Reset global instance")
    reset_rng = stx.rng.reset(seed=123)
    new_data = reset_rng("experiment").random(10)
    logger.info(f"After reset, first 3 values: {new_data[:3]}")

    # Demonstrate that named generators are independent
    logger.info("\nDemonstrating generator independence:")
    rng2 = stx.rng.RandomStateManager(seed=42)

    # Generate from "data" multiple times
    data1 = rng2("data").random(3)
    data2 = rng2("data").random(3)  # Continues from where data1 left off

    # Generate from "model" - independent sequence
    model1 = rng2("model").random(3)

    logger.info(f"data generator - call 1: {data1}")
    logger.info(f"data generator - call 2: {data2}")
    logger.info(f"model generator - call 1: {model1}")
    logger.info("Notice: 'model' values are different from 'data' values")

    # Demonstrate reproducibility
    logger.info("\nReproducibility check:")
    rng3 = stx.rng.RandomStateManager(seed=42)
    data3 = rng3("data").random(3)
    logger.success(f"Same seed, same name → same values: {np.allclose(data1, data3)}")

    return train_data, weights


if __name__ == "__main__":
    # Run the example
    train_data, weights = main()

    # Run again to show reproducibility
    logger.info("\n" + "="*60)
    logger.info("Running again to demonstrate reproducibility...")
    logger.info("="*60)
    train_data2, weights2 = main()

    # Verify reproducibility
    logger.info("\n" + "="*60)
    logger.success(f"Training data identical: {np.allclose(train_data, train_data2)}")
    logger.success(f"Weights identical: {np.allclose(weights, weights2)}")
    logger.info("✓ Perfect reproducibility achieved!")
