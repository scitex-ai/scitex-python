#!/usr/bin/env python3
"""
Machine Learning Example with Checkpointing

This example demonstrates using the RNG module in ML workflows:
- Data splitting and augmentation
- Model initialization
- Training with checkpoints
- Reproducible evaluation
- Handling PyTorch/TensorFlow if available

The example works with pure NumPy but shows how to integrate with ML frameworks.
"""

import numpy as np
import scitex as stx
from pathlib import Path
import time
from scitex.logging import getLogger

logger = getLogger(__name__)

# Try to import ML frameworks (optional)
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.info("PyTorch not available - using NumPy-only example")


class SimpleNeuralNetwork:
    """Simple neural network implementation in NumPy."""

    def __init__(self, input_dim, hidden_dim, output_dim, rng):
        """Initialize network with reproducible weights."""
        self.rng = rng

        # Initialize weights using named generators
        init_gen = self.rng("weight_init")

        # Xavier/Glorot initialization
        self.W1 = init_gen.normal(0, np.sqrt(2/input_dim),
                                 size=(input_dim, hidden_dim))
        self.b1 = np.zeros(hidden_dim)

        self.W2 = init_gen.normal(0, np.sqrt(2/hidden_dim),
                                 size=(hidden_dim, output_dim))
        self.b2 = np.zeros(output_dim)

        # Verify initialization is reproducible
        self.rng.verify(self.W1.flatten(), "initial_W1")
        self.rng.verify(self.W2.flatten(), "initial_W2")

        logger.info(f"Initialized network: {input_dim} → {hidden_dim} → {output_dim}")

    def forward(self, X):
        """Forward pass."""
        # Hidden layer with ReLU
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)  # ReLU

        # Output layer
        self.z2 = self.a1 @ self.W2 + self.b2

        # Softmax for classification
        exp_scores = np.exp(self.z2 - np.max(self.z2, axis=1, keepdims=True))
        self.probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

        return self.probs

    def compute_loss(self, X, y):
        """Compute cross-entropy loss."""
        probs = self.forward(X)
        n_samples = X.shape[0]

        # Cross-entropy loss
        log_probs = -np.log(probs[range(n_samples), y] + 1e-8)
        loss = np.mean(log_probs)

        return loss

    def backward(self, X, y, learning_rate=0.01):
        """Backward pass with gradient descent."""
        n_samples = X.shape[0]

        # Gradient of output layer
        delta2 = self.probs.copy()
        delta2[range(n_samples), y] -= 1
        delta2 /= n_samples

        dW2 = self.a1.T @ delta2
        db2 = np.sum(delta2, axis=0)

        # Gradient of hidden layer
        delta1 = delta2 @ self.W2.T
        delta1[self.z1 <= 0] = 0  # ReLU gradient

        dW1 = X.T @ delta1
        db1 = np.sum(delta1, axis=0)

        # Update weights
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

    def predict(self, X):
        """Make predictions."""
        probs = self.forward(X)
        return np.argmax(probs, axis=1)

    def accuracy(self, X, y):
        """Calculate accuracy."""
        predictions = self.predict(X)
        return np.mean(predictions == y)


class MLExperiment:
    """Machine learning experiment with reproducible randomness."""

    def __init__(self, seed=42):
        """Initialize ML experiment."""
        self.rng = stx.rng.RandomStateManager(seed=seed)
        self.history = {'train_loss': [], 'val_loss': [],
                       'train_acc': [], 'val_acc': []}

    def generate_dataset(self, n_samples=1000, n_features=20, n_classes=3):
        """Generate synthetic classification dataset."""
        logger.info(f"Generating dataset: {n_samples} samples, {n_features} features, {n_classes} classes")

        data_gen = self.rng("dataset")

        # Generate clustered data
        X = []
        y = []

        samples_per_class = n_samples // n_classes

        for class_idx in range(n_classes):
            # Each class has a different center
            center = data_gen.normal(0, 2, size=n_features)

            # Generate samples around center
            class_samples = data_gen.normal(center, 0.5,
                                           size=(samples_per_class, n_features))
            X.append(class_samples)
            y.extend([class_idx] * samples_per_class)

        X = np.vstack(X)
        y = np.array(y)

        # Shuffle data
        shuffle_gen = self.rng("shuffle")
        indices = np.arange(len(y))
        shuffle_gen.shuffle(indices)
        X = X[indices]
        y = y[indices]

        # Verify dataset reproducibility
        self.rng.verify(X.flatten()[:100], "dataset_sample")

        return X, y

    def split_data(self, X, y, train_ratio=0.6, val_ratio=0.2):
        """Split data into train/val/test sets reproducibly."""
        logger.info(f"Splitting data: {train_ratio:.0%} train, {val_ratio:.0%} val, {1-train_ratio-val_ratio:.0%} test")

        n_samples = len(y)
        n_train = int(n_samples * train_ratio)
        n_val = int(n_samples * val_ratio)

        # Data is already shuffled
        X_train = X[:n_train]
        y_train = y[:n_train]

        X_val = X[n_train:n_train + n_val]
        y_val = y[n_train:n_train + n_val]

        X_test = X[n_train + n_val:]
        y_test = y[n_train + n_val:]

        logger.info(f"  Train: {len(y_train)} samples")
        logger.info(f"  Val:   {len(y_val)} samples")
        logger.info(f"  Test:  {len(y_test)} samples")

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

    def augment_batch(self, X, augmentation_strength=0.1):
        """Apply data augmentation to a batch."""
        aug_gen = self.rng("augmentation")

        # Add Gaussian noise
        noise = aug_gen.normal(0, augmentation_strength, size=X.shape)
        X_aug = X + noise

        # Random scaling
        scale = aug_gen.uniform(0.9, 1.1, size=(X.shape[0], 1))
        X_aug = X_aug * scale

        return X_aug

    def train_model(self, model, train_data, val_data,
                   epochs=10, batch_size=32, learning_rate=0.01,
                   checkpoint_freq=5):
        """Train model with checkpointing."""
        X_train, y_train = train_data
        X_val, y_val = val_data

        n_batches = len(X_train) // batch_size

        logger.info(f"Training for {epochs} epochs, {n_batches} batches per epoch")

        batch_gen = self.rng("batch_sampling")

        for epoch in range(epochs):
            epoch_losses = []

            # Shuffle training data each epoch
            indices = np.arange(len(y_train))
            batch_gen.shuffle(indices)
            X_train_shuffled = X_train[indices]
            y_train_shuffled = y_train[indices]

            # Mini-batch training
            for batch_idx in range(n_batches):
                start_idx = batch_idx * batch_size
                end_idx = start_idx + batch_size

                X_batch = X_train_shuffled[start_idx:end_idx]
                y_batch = y_train_shuffled[start_idx:end_idx]

                # Apply augmentation
                if epoch > 0:  # Skip augmentation for first epoch
                    X_batch = self.augment_batch(X_batch, augmentation_strength=0.05)

                # Forward and backward pass
                loss = model.compute_loss(X_batch, y_batch)
                model.backward(X_batch, y_batch, learning_rate)

                epoch_losses.append(loss)

            # Evaluate on full sets
            train_loss = model.compute_loss(X_train, y_train)
            train_acc = model.accuracy(X_train, y_train)
            val_loss = model.compute_loss(X_val, y_val)
            val_acc = model.accuracy(X_val, y_val)

            # Store history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)

            logger.info(f"Epoch {epoch+1}/{epochs}: "
                       f"train_loss={train_loss:.3f}, train_acc={train_acc:.3f}, "
                       f"val_loss={val_loss:.3f}, val_acc={val_acc:.3f}")

            # Checkpoint
            if (epoch + 1) % checkpoint_freq == 0:
                checkpoint_path = self.save_checkpoint(model, epoch + 1)
                logger.info(f"  Saved checkpoint at epoch {epoch + 1}")

        return model

    def save_checkpoint(self, model, epoch):
        """Save model and RNG checkpoint."""
        # Save RNG state
        rng_checkpoint = self.rng.checkpoint(f"ml_experiment_epoch_{epoch}")

        # Save model weights (in practice, use proper serialization)
        model_checkpoint = Path.home() / ".scitex" / "rng" / f"model_epoch_{epoch}.npz"
        np.savez(model_checkpoint,
                W1=model.W1, b1=model.b1,
                W2=model.W2, b2=model.b2)

        logger.info(f"  Checkpoint saved: {rng_checkpoint.name}, {model_checkpoint.name}")
        return rng_checkpoint, model_checkpoint

    def load_checkpoint(self, model, rng_checkpoint, model_checkpoint):
        """Load model and RNG from checkpoint."""
        # Restore RNG state
        self.rng.restore(rng_checkpoint)

        # Load model weights
        weights = np.load(model_checkpoint)
        model.W1 = weights['W1']
        model.b1 = weights['b1']
        model.W2 = weights['W2']
        model.b2 = weights['b2']

        logger.info("Checkpoint loaded successfully")
        return model


def demonstrate_pytorch_integration():
    """Show how RNG works with PyTorch if available."""
    if not TORCH_AVAILABLE:
        logger.info("PyTorch not available - skipping PyTorch demonstration")
        return

    logger.info("\n" + "="*60)
    logger.info("PYTORCH INTEGRATION")
    logger.info("="*60)

    # RNG automatically sets PyTorch seeds
    rng = stx.rng.RandomStateManager(seed=42)

    # Create PyTorch model with reproducible initialization
    model = nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 3)
    )

    # Get initial weights
    initial_weight = model[0].weight.data.clone()

    # Create another model with same seed
    rng2 = stx.rng.RandomStateManager(seed=42)
    model2 = nn.Sequential(
        nn.Linear(10, 20),
        nn.ReLU(),
        nn.Linear(20, 3)
    )

    # Check reproducibility
    weights_match = torch.allclose(initial_weight, model2[0].weight.data)
    logger.success(f"PyTorch weights reproducible: {weights_match}")


def main():
    """Run complete ML example."""
    logger.info("="*60)
    logger.info("MACHINE LEARNING EXAMPLE WITH RNG MODULE")
    logger.info("="*60)

    # Initialize experiment
    exp = MLExperiment(seed=42)

    # Generate and split data
    X, y = exp.generate_dataset(n_samples=500, n_features=20, n_classes=3)
    train_data, val_data, test_data = exp.split_data(X, y)

    # Create model
    n_features = X.shape[1]
    n_classes = len(np.unique(y))
    model = SimpleNeuralNetwork(n_features, hidden_dim=50,
                               output_dim=n_classes, rng=exp.rng)

    # Train model
    model = exp.train_model(model, train_data, val_data,
                           epochs=10, batch_size=32, learning_rate=0.1)

    # Final evaluation
    X_test, y_test = test_data
    test_acc = model.accuracy(X_test, y_test)
    logger.info(f"\nFinal test accuracy: {test_acc:.3f}")

    # Verify reproducibility of final predictions
    predictions = model.predict(X_test)
    exp.rng.verify(predictions, "final_predictions")

    return exp, model


def demonstrate_checkpoint_resume():
    """Show how to resume training from checkpoint."""
    logger.info("\n" + "="*60)
    logger.info("CHECKPOINT RESUME DEMONSTRATION")
    logger.info("="*60)

    # Start training
    exp = MLExperiment(seed=42)
    X, y = exp.generate_dataset(n_samples=200, n_features=10, n_classes=2)
    train_data, val_data, test_data = exp.split_data(X, y)

    model = SimpleNeuralNetwork(10, 20, 2, exp.rng)

    # Train for 5 epochs
    logger.info("Training for 5 epochs...")
    model = exp.train_model(model, train_data, val_data,
                           epochs=5, checkpoint_freq=5)

    # Save checkpoint
    rng_ckpt, model_ckpt = exp.save_checkpoint(model, epoch=5)

    # Simulate interruption - create new experiment
    logger.info("\nSimulating interruption...")
    new_exp = MLExperiment(seed=999)  # Different seed
    new_model = SimpleNeuralNetwork(10, 20, 2, new_exp.rng)

    # Resume from checkpoint
    logger.info("Resuming from checkpoint...")
    new_exp.load_checkpoint(new_model, rng_ckpt, model_ckpt)

    # Continue training
    logger.info("Continuing training for 5 more epochs...")
    new_model = new_exp.train_model(new_model, train_data, val_data,
                                   epochs=5, checkpoint_freq=5)

    logger.success("Training resumed successfully from checkpoint!")


if __name__ == "__main__":
    # Run main ML experiment
    exp, model = main()

    # Show training history
    logger.info("\n" + "="*60)
    logger.info("TRAINING HISTORY")
    logger.info("="*60)
    logger.info("Epoch | Train Loss | Train Acc | Val Loss | Val Acc")
    logger.info("-" * 55)
    for i in range(len(exp.history['train_loss'])):
        logger.info(f"{i+1:5d} | {exp.history['train_loss'][i]:10.3f} | "
                   f"{exp.history['train_acc'][i]:9.3f} | "
                   f"{exp.history['val_loss'][i]:8.3f} | "
                   f"{exp.history['val_acc'][i]:7.3f}")

    # Demonstrate checkpoint resume
    demonstrate_checkpoint_resume()

    # Demonstrate PyTorch integration if available
    demonstrate_pytorch_integration()

    logger.info("\n" + "="*60)
    logger.success("All ML demonstrations completed!")
    logger.info("Run multiple times to verify reproducibility!")
