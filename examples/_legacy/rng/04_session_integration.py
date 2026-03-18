#!/usr/bin/env python3
"""
Session Integration Example

This example demonstrates how the RNG module integrates with stx.session.start():
- Automatic RNG setup through session
- Using RNG with other session components
- Temporary seed contexts
- Integration with configuration system

This shows the recommended way to use RNG in SciTeX projects.
"""

import numpy as np
import scitex as stx
from pathlib import Path
from scitex.logging import getLogger

# Logger will be reconfigured by session.start()
logger = getLogger(__name__)


def example_with_session_start():
    """Demonstrate RNG usage through session.start()."""
    logger.info("="*60)
    logger.info("RNG WITH SESSION.START()")
    logger.info("="*60)

    # Session.start() returns multiple utilities including RNG
    CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(
        __file__,
        seed=42,  # Sets up RNG with this seed
        SHOW_PLOTS=False,
        SAVE_PLOTS=True
    )

    logger.info("Session started with automatic RNG setup")
    logger.info(f"CONFIG.seed: {CONFIG.seed}")
    logger.info(f"RNG seed: {rng.seed}")

    # Use RNG for different purposes
    # 1. Data generation
    data_gen = rng("data")
    train_data = data_gen.normal(0, 1, size=(100, 10))
    logger.info(f"Generated training data: shape={train_data.shape}")

    # 2. Model initialization
    model_gen = rng("model")
    weights = model_gen.uniform(-0.1, 0.1, size=(10, 5))
    logger.info(f"Initialized model weights: shape={weights.shape}")

    # 3. Sampling
    sample_gen = rng("sampling")
    indices = sample_gen.choice(100, size=20, replace=False)
    logger.info(f"Sampled {len(indices)} indices from training data")

    # 4. Verify reproducibility
    data_reproducible = rng.verify(train_data, "session_train_data")
    weights_reproducible = rng.verify(weights, "session_weights")

    if data_reproducible and weights_reproducible:
        logger.success("Session-based RNG is reproducible")

    # Use with plotting (plt from session)
    if plt:
        plt.subplots(1, 2, figsize=(10, 4))

        # Plot 1: Data distribution
        plt.subplot(1, 2, 1)
        plt.hist(train_data.flatten(), bins=30, alpha=0.7, color='blue')
        plt.title("Training Data Distribution")
        plt.xlabel("Value")
        plt.ylabel("Frequency")

        # Plot 2: Weight distribution
        plt.subplot(1, 2, 2)
        plt.hist(weights.flatten(), bins=20, alpha=0.7, color='green')
        plt.title("Initial Weights Distribution")
        plt.xlabel("Value")
        plt.ylabel("Frequency")

        plt.tight_layout()

        # Save plot (using CONFIG paths)
        plot_path = Path(CONFIG.ODIR) / "rng_distributions.png"
        plt.savefig(plot_path)
        logger.info(f"Saved plot to {plot_path}")
        plt.close()

    return CONFIG, rng


def example_with_temporary_seed():
    """Demonstrate temporary seed context manager."""
    logger.info("\n" + "="*60)
    logger.info("TEMPORARY SEED CONTEXT")
    logger.info("="*60)

    # Get RNG from session
    CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(seed=42)

    # Generate some data with main seed
    main_gen = rng("main")
    data1 = main_gen.random(5)
    logger.info(f"With main seed (42): {data1}")

    # Use temporary seed for specific operation
    with rng.temporary_seed(123):
        import random
        temp_value = random.random()
        logger.info(f"With temporary seed (123): {temp_value}")

    # Back to main seed
    data2 = main_gen.random(5)
    logger.info(f"Back to main seed: {data2}")

    # Verify that main generator continues from where it left off
    logger.info("Note: main generator continues its sequence after temp seed")


def example_multi_experiment_reproducibility():
    """Run multiple experiments with different seeds from config."""
    logger.info("\n" + "="*60)
    logger.info("MULTI-EXPERIMENT REPRODUCIBILITY")
    logger.info("="*60)

    results = {}

    # Run experiments with different seeds
    for exp_id, seed in enumerate([42, 123, 456], 1):
        logger.info(f"\n>>> Experiment {exp_id} (seed={seed})")

        # Start session with specific seed
        CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(
            seed=seed,
            SHOW_PLOTS=False
        )

        # Run experiment
        data_gen = rng("experiment")
        exp_data = data_gen.normal(0, 1, size=100)

        # Store results
        mean = exp_data.mean()
        std = exp_data.std()
        results[seed] = {'mean': mean, 'std': std}

        logger.info(f"  Results: mean={mean:.4f}, std={std:.4f}")

        # Verify reproducibility
        rng.verify(exp_data, f"experiment_{seed}")

    # Summary
    logger.info("\n" + "-"*40)
    logger.info("Summary of experiments:")
    for seed, res in results.items():
        logger.info(f"  Seed {seed}: mean={res['mean']:.4f}, std={res['std']:.4f}")

    # Re-run one experiment to verify reproducibility
    logger.info("\n>>> Re-running Experiment 1 to verify reproducibility")
    CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(seed=42)
    data_gen = rng("experiment")
    exp_data_repeat = data_gen.normal(0, 1, size=100)

    mean_repeat = exp_data_repeat.mean()
    logger.success(f"Reproducible: {np.isclose(mean_repeat, results[42]['mean'])}")


def example_config_integration():
    """Show how RNG integrates with configuration system."""
    logger.info("\n" + "="*60)
    logger.info("CONFIGURATION INTEGRATION")
    logger.info("="*60)

    # Create custom config
    import tempfile
    import yaml

    config_content = """
    # Experiment configuration
    experiment:
      seed: 2024
      n_samples: 500
      n_features: 20

    training:
      batch_size: 32
      learning_rate: 0.01
      epochs: 10

    data:
      noise_level: 0.1
      train_ratio: 0.7
    """

    # Write config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name

    logger.info(f"Created config file: {config_path}")

    # Start session with config file
    CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(
        config_path,
        seed=None  # Will use seed from config if available
    )

    # Access config values
    logger.info(f"Loaded configuration:")
    logger.info(f"  Seed: {CONFIG.get('experiment.seed', 42)}")
    logger.info(f"  Samples: {CONFIG.get('experiment.n_samples', 100)}")
    logger.info(f"  Features: {CONFIG.get('experiment.n_features', 10)}")

    # Use config values with RNG
    n_samples = CONFIG.get('experiment.n_samples', 100)
    n_features = CONFIG.get('experiment.n_features', 10)
    noise_level = CONFIG.get('data.noise_level', 0.1)

    # Generate data based on config
    data_gen = rng("config_data")
    X = data_gen.normal(0, 1, size=(n_samples, n_features))
    noise = data_gen.normal(0, noise_level, size=n_samples)

    logger.info(f"Generated data using config: X.shape={X.shape}")
    logger.info(f"Added noise with level={noise_level}")

    # Clean up
    Path(config_path).unlink()

    return CONFIG, rng


def example_parallel_experiments():
    """Show how to run parallel experiments with independent RNGs."""
    logger.info("\n" + "="*60)
    logger.info("PARALLEL EXPERIMENTS WITH INDEPENDENT RNGS")
    logger.info("="*60)

    # Main session
    CONFIG, stdout, stderr, plt, CC, rng_main = stx.session.start(seed=42)

    # Create independent RNGs for parallel experiments
    experiments = []
    for i in range(3):
        # Each experiment gets its own RNG with unique seed
        exp_seed = 1000 + i
        exp_rng = stx.rng.RandomStateManager(seed=exp_seed)

        # Run experiment
        data_gen = exp_rng("data")
        result = data_gen.normal(0, 1, size=50).mean()

        experiments.append({
            'id': i,
            'seed': exp_seed,
            'result': result,
            'rng': exp_rng
        })

        logger.info(f"Experiment {i}: seed={exp_seed}, result={result:.4f}")

    # Verify each experiment is reproducible independently
    logger.info("\nVerifying independent reproducibility:")
    for exp in experiments:
        # Re-create RNG with same seed
        verify_rng = stx.rng.RandomStateManager(seed=exp['seed'])
        verify_gen = verify_rng("data")
        verify_result = verify_gen.normal(0, 1, size=50).mean()

        matches = np.isclose(verify_result, exp['result'])
        logger.success(f"  Experiment {exp['id']}: reproducible = {matches}")


def main():
    """Run all session integration examples."""
    logger.info("="*60)
    logger.info("RNG MODULE - SESSION INTEGRATION EXAMPLES")
    logger.info("="*60)

    # Example 1: Basic session integration
    CONFIG, rng = example_with_session_start()

    # Example 2: Temporary seed context
    example_with_temporary_seed()

    # Example 3: Multi-experiment reproducibility
    example_multi_experiment_reproducibility()

    # Example 4: Configuration integration
    example_config_integration()

    # Example 5: Parallel experiments
    example_parallel_experiments()

    logger.info("\n" + "="*60)
    logger.success("All session integration examples completed!")
    logger.info("Key takeaways:")
    logger.info("  1. Use stx.session.start(seed=N) for automatic RNG setup")
    logger.info("  2. RNG integrates with CONFIG, plotting, and logging")
    logger.info("  3. Each named generator is independent and reproducible")
    logger.info("  4. Checkpoints allow resuming long experiments")
    logger.info("  5. Temporary seeds useful for specific operations")


if __name__ == "__main__":
    main()
