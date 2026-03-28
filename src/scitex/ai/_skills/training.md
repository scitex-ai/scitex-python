---
description: Training helpers — EarlyStopping with direction control and LearningCurveLogger for multi-phase metric tracking and visualization.
---

# Training Helpers

## EarlyStopping

Stops training when a monitored metric does not improve after a given patience period. Also saves model checkpoints at each improvement.

```python
class EarlyStopping:
    def __init__(
        self,
        patience: int = 7,
        verbose: bool = False,
        delta: float = 1e-5,
        direction: str = "minimize",
    )
```

### Parameters
- `patience` — Steps to wait after last improvement before stopping. Default: `7`
- `verbose` — Print counter progress and stop messages. Default: `False`
- `delta` — Minimum change to qualify as improvement. Default: `1e-5`
- `direction` — `"minimize"` (lower is better, e.g. loss) or `"maximize"` (higher is better, e.g. accuracy). Default: `"minimize"`

### Attributes
- `best_score` — Best score seen so far
- `counter` — Steps without improvement
- `best_i_global` — Global step index of the best score
- `models_spaths_dict` — Dict of `{model: save_path}` at the best checkpoint

### Calling `__call__`

```python
def __call__(
    self,
    current_score: float,
    models_spaths_dict: Dict,
    i_global: int,
) -> bool
```

- `current_score` — Current validation metric value
- `models_spaths_dict` — `{pytorch_model: "/path/to/checkpoint.pth"}` — saved via `stx.io.save(model.state_dict(), path)` on improvement
- `i_global` — Current global iteration index

Returns `True` when training should stop, `False` otherwise.

### Example

```python
import scitex as stx

early_stopping = stx.ai.EarlyStopping(
    patience=10,
    verbose=True,
    direction="minimize",
)

for i_global in range(max_iters):
    val_loss = evaluate(model)
    should_stop = early_stopping(
        current_score=val_loss,
        models_spaths_dict={model: "./checkpoints/best_model.pth"},
        i_global=i_global,
    )
    if should_stop:
        break

print(f"Best loss: {early_stopping.best_score:.6f} at step {early_stopping.best_i_global}")
```

---

## LearningCurveLogger

Records and visualizes training metrics across Training/Validation/Test phases. Metrics ending in `_plot` are plotted; all others are stored but not plotted.

```python
class LearningCurveLogger:
    def __init__(self)
```

### Calling `__call__`

```python
def __call__(
    self,
    dict_to_log: Dict[str, Any],
    step: str,
) -> None
```

- `dict_to_log` — Dictionary of metrics. Keys ending in `_plot` are included in visualizations. Required metadata keys: `"i_fold"`, `"i_epoch"`, `"i_global"`, and optionally `"i_batch"`
- `step` — Training phase string: `"Training"`, `"Validation"`, or `"Test"`

### plot_learning_curves()

```python
def plot_learning_curves(
    self,
    title: Optional[str] = None,
    max_n_ticks: int = 4,
    linewidth: float = 1,
    scattersize: float = 3,
    yscale: str = "linear",
    spath: Optional[str] = None,
) -> matplotlib.figure.Figure
```

Delegates to `scitex.ai.plt.plot_learning_curve`.

### dfs property

```python
logger.dfs  # Dict[str, pd.DataFrame] — one DataFrame per phase
```

### get_x_of_i_epoch()

```python
def get_x_of_i_epoch(
    self,
    x: str,
    step: str,
    i_epoch: int,
) -> np.ndarray
```

Retrieve values of metric `x` for a specific epoch in a given step.

### print()

```python
def print(self, step: str) -> None
```

Prints epoch-averaged metrics for the given step.

### Example

```python
import scitex as stx

lc_logger = stx.ai.LearningCurveLogger()
i_global = 0

for i_epoch in range(max_epochs):
    for step, dataloader in [("Validation", dl_val), ("Training", dl_tra)]:
        for i_batch, (X, T) in enumerate(dataloader):
            logits = model(X)
            loss = loss_fn(logits, T)
            if step == "Training":
                loss.backward()
                optimizer.step()

            lc_logger(
                {
                    "loss_plot": float(loss),
                    "balanced_ACC_plot": float(bacc),
                    "pred_proba": pred_proba.detach().cpu().numpy(),
                    "true_class": T.cpu().numpy(),
                    "i_fold": 0,
                    "i_epoch": i_epoch,
                    "i_batch": i_batch,
                    "i_global": i_global,
                },
                step,
            )
            i_global += 1

        lc_logger.print(step)

fig = lc_logger.plot_learning_curves(
    title="Training Progress",
    spath="./learning_curve.jpg",
)
```

### Note on `_plot` suffix convention

Keys ending in `_plot` appear in the learning curve figure. Other keys (e.g. `"pred_proba"`, `"true_class"`) are stored in `logged_dict` for downstream use (e.g. computing epoch metrics) but not plotted.
