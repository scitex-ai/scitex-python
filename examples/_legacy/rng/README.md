# SciTeX RNG Examples

This directory contains examples demonstrating the SciTeX RNG module for reproducible random number generation.

## Examples

### 1. basic_usage.py
Introduction to core RNG functionality:
- Creating RandomStateManager
- Getting named generators
- Verifying reproducibility
- Using global instance

```bash
python examples/rng/basic_usage.py
```

### 2. scientific_experiment.py
Complete scientific workflow with reproducibility:
- Synthetic data generation
- Train/test splitting
- Checkpointing and restoration
- Reproducibility verification

```bash
python examples/rng/scientific_experiment.py
```

### 3. machine_learning.py
ML training with reproducible randomness:
- Neural network initialization
- Dropout and batch sampling
- Checkpointing during training
- Temporary seeds for debugging

```bash
python examples/rng/machine_learning.py
```

### 4. session_integration.py
Integration with scitex.session.start():
- Getting RNG from session
- Workflow components with RNG
- Verification and checkpointing
- Cross-session reproducibility

```bash
python examples/rng/session_integration.py
```

### 5. multi_library.py
Automatic handling of multiple libraries:
- Python random module
- NumPy (old and new API)
- PyTorch (CPU and CUDA)
- TensorFlow
- JAX
- Python hash (PYTHONHASHSEED)

```bash
python examples/rng/multi_library.py
```

## Key Features Demonstrated

- **Named Generators**: Independent random streams that survive code changes
- **Automatic Seed Fixing**: All libraries fixed with one initialization
- **Verification System**: Detect when reproducibility breaks
- **Checkpointing**: Save and restore exact random states
- **Session Integration**: Seamless use with stx.session.start()
- **Multi-Library Support**: Handles Python, NumPy, PyTorch, TensorFlow, JAX

## Running All Examples

```bash
cd examples/rng
for script in *.py; do
    echo "Running $script..."
    python "$script"
    echo ""
done
```

## Learn More

See the main RNG documentation at `/src/scitex/rng/README.md` for detailed API reference and best practices.
