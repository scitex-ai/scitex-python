<!-- ---
!-- Timestamp: 2025-11-05 20:36:46
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-code/docs/session_decorator_guide.md
!-- --- -->

# SciTeX Session Decorator Guide

## Overview

The `@session` decorator provides a simplified way to create SciTeX scripts with automatic session management, eliminating the need for boilerplate code.

## Quick Start

### Before (Old Way - 60+ lines of boilerplate)

```python
#!/usr/bin/env python3
import argparse
import scitex as stx

def main(args):
    data = stx.io.load(args.data_path)
    result = process(data, args.threshold)
    stx.io.save(result, "output.csv")
    return 0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True)
    parser.add_argument('--threshold', type=float, default=0.5)
    return parser.parse_args()

def run_session():
    global CONFIG, sys, plt
    args = parse_args()
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys, plt, args=args, file=__FILE__,
        sdir_suffix=None, verbose=False, agg=True,
    )
    exit_status = main(args)
    stx.session.close(CONFIG, verbose=False, exit_status=exit_status)

if __name__ == '__main__':
    run_session()
```

### After (New Way - Simple and Clean)

```python
#!/usr/bin/env python3
from scitex.session import session
import scitex as stx

@session
def analyze(data_path: str, CONFIG=stx.session.INJECTED):
    """Analyze data file."""
    data = stx.io.load(data_path)
    result = process(data, CONFIG.ANALYSIS.THRESHOLD)  # config/ANALYSIS.yaml
    stx.io.save(result, "output.csv")
    return 0
```

```yaml
# config/ANALYSIS.yaml
THRESHOLD: 0.5
```

**80% less boilerplate!**

## Where parameters live

Analysis parameters (thresholds, window sizes, sample counts, seeds) go in
`config/*.yaml`, not in function signature defaults or on the command line.
The session loads `./config/*.yaml` (resolved against the working directory)
into the injected `CONFIG`: the file stem is the namespace and keys are
upper-cased, so `config/ANALYSIS.yaml` with `THRESHOLD: 0.5` is read as
`CONFIG.ANALYSIS.THRESHOLD`. CLI arguments are for inputs such as file paths
or subject IDs. There is no CLI override for `CONFIG` values: edit the YAML,
and each run freezes the values it used in `CONFIGS/CONFIG.yaml`.

In `project-type: research` projects, `scitex-dev` >= 0.64.0 lint rule
STX-S008 warns on numeric signature defaults and other hard-coded parameters.

## Features

### Automatic CLI Generation

The decorator automatically generates CLI arguments from your function signature:

- Function parameters → `--parameter-name` CLI arguments
- Type hints → argument types
- Default values → optional arguments
- Docstrings → help text

### Automatic Session Management

Handles all session lifecycle:

- Output directory creation (`script_out/RUNNING/ID-function_name/`)
- Logging configuration (stdout/stderr to log files)
- Random seed management
- Matplotlib configuration
- Cleanup on exit (moves to `FINISHED_SUCCESS/` or `FINISHED_ERROR/`)
- Error handling

## Usage Examples

### 1. Simple Function (No Arguments)

```python
from scitex.session import session
import scitex as stx

@session
def hello():
    """Simple hello world with session management."""
    print("Hello from scitex session!")
    stx.io.save({"message": "hello"}, "hello.json")
    return 0
```

Run: `python script.py`

### 2. Function with Arguments

```python
@session
def analyze(
    data_path: str,
    output_name: str = "results.csv",
    verbose: bool = False,
    CONFIG=stx.session.INJECTED,
):
    """Analyze data file.

    Args:
        data_path: Path to input data file
        output_name: Name for output file
        verbose: Print detailed information
    """
    if verbose:
        print(f"Loading data from {data_path}")

    data = load_data(data_path)
    result = process(data, CONFIG.ANALYSIS.THRESHOLD)  # config/ANALYSIS.yaml
    stx.io.save(result, output_name)

    return 0
```

Run (from the directory that holds `config/`):
```bash
python script.py --help  # See auto-generated help and CONFIG values
python script.py --data-path data.csv --verbose
```

### 3. With Session Options

```python
@session(verbose=True, notify=True, agg=True)
def process_dataset(input_dir: str, CONFIG=stx.session.INJECTED):
    """Process dataset with custom session settings."""
    n_samples = CONFIG.DATASET.N_SAMPLES  # config/DATASET.yaml
    print(f"Processing {n_samples} samples from {input_dir}")
    # Your code here
    return 0
```

### 4. Visualization Example

```python
@session
def create_plots(CONFIG=stx.session.INJECTED, rngg=stx.session.INJECTED):
    """Create one plot per channel; sizes come from config/PLOTS.yaml."""
    params = CONFIG.PLOTS  # N_PLOTS: 5, N_POINTS: 100

    data = rngg("demo").standard_normal((params.N_POINTS, params.N_PLOTS))

    for i in range(params.N_PLOTS):
        fig, ax = stx.plt.subplots()
        ax.plot(data[:, i])
        ax.set_title(f"Plot {i+1}")
        stx.io.save(fig, f"plot_{i+1:02d}.png")

    return 0
```

Run: `python script.py` (to change the number of plots, edit `config/PLOTS.yaml`)

## Supported Types

The decorator supports these type hints:

```python
@session
def example(
    text: str,           # String argument
    number: int,         # Integer
    ratio: float,        # Float
    flag: bool = False,  # Boolean flag (--flag)
):
    pass
```

CLI usage:
```bash
python script.py \
    --text "hello" \
    --number 42 \
    --ratio 0.5 \
    --flag  # Boolean: present = True
```

Numeric types are supported, but numbers that shape a result belong in
`config/*.yaml` (see [Where parameters live](#where-parameters-live)).

## Session Options

```python
@session(
    verbose=True,        # Enable verbose logging
    agg=True,           # Use matplotlib Agg backend
    notify=True,        # Send notification on completion
    sdir_suffix="exp1"  # Custom output directory suffix
)
def analyze():
    pass
```

## Accessing Session Variables

Session variables are automatically available in your function:

```python
@session
def analyze(data_path: str):
    # These are automatically available:
    # - CONFIG: Configuration dictionary
    # - plt: Configured matplotlib.pyplot
    # - CC: Color cycle dictionary
    # - rng: RandomStateManager for reproducible random numbers

    print(f"Session ID: {CONFIG['ID']}")
    print(f"Output directory: {CONFIG['SDIR_RUN']}")

    # Use rng for reproducible random numbers
    random_data = rng.numpy.randn(100, 10)

    return 0
```

## Direct Function Calls

You can still call the decorated function directly (not via CLI):

```python
@session
def analyze(data_path: str):
    pass

# Call directly in code (bypasses session management)
result = analyze._func(data_path="data.csv")
```

## Return Values

Functions can return:
- `0`: Success (moves to `FINISHED_SUCCESS/`)
- `1`: Error (moves to `FINISHED_ERROR/`)
- `None` or anything else: Finished (moves to `FINISHED/`)

## Output Structure

When you run a decorated function, outputs are automatically organized:

```
script_name_out/
├── RUNNING/
│   └── 2025Y-11M-05D-20h31m52s_HTFn-function_name/
│       ├── CONFIGS/
│       │   ├── CONFIG.pkl
│       │   └── CONFIG.yaml
│       └── logs/
│           ├── stdout.log
│           └── stderr.log
└── FINISHED_SUCCESS/  # or FINISHED_ERROR/
    └── 2025Y-11M-05D-20h31m52s_HTFn-function_name/
        └── (same structure)
```

## Migration Guide

To migrate existing scripts:

1. Import the decorator:
   ```python
   from scitex.session import session
   ```

2. Replace the boilerplate:
   ```python
   # Remove: parse_args(), run_session(), if __name__ == '__main__'

   # Change this:
   def main(args):
       # code using args.param1, args.param2

   # To this:
   @session
   def main(param1: type, param2: type = default):
       # code using param1, param2 directly
   ```

3. Update function signature to use parameters directly instead of `args` object

## Comparison with Old Method

| Feature              | Old Way  | New Way      |
|----------------------|----------|--------------|
| Lines of boilerplate | 60+      | 0            |
| argparse setup       | Manual   | Automatic    |
| Type hints           | Optional | Used for CLI |
| Session management   | Manual   | Automatic    |
| Error handling       | Manual   | Automatic    |
| Learning curve       | Steep    | Gentle       |

## When NOT to Use the Decorator

Use the traditional approach when you need:
- Custom argparse configuration (subparsers, custom actions)
- Complex session initialization
- Fine-grained control over session lifecycle

## Troubleshooting

### Import Error

If you get `TypeError: '_LazyModule' object is not callable`:

```python
# Wrong:
import scitex as stx
@stx.session  # This won't work due to lazy loading

# Right:
from scitex.session import session
@session
```

### Type Hints Not Working

Make sure to use proper type hints:

```python
# Wrong:
def analyze(data_path):  # No type hint

# Right:
def analyze(data_path: str):  # Type hint provided
```

## Summary

The `@session` decorator:
- ✅ Reduces boilerplate by 80%
- ✅ Makes code more readable
- ✅ Auto-generates CLI from function signatures
- ✅ Handles all session management automatically
- ✅ Maintains backward compatibility (old method still works)
- ✅ Perfect for quick scripts and prototypes
- ✅ Production-ready with proper error handling

Start using `@session` today and enjoy cleaner, more maintainable SciTeX scripts!

<!-- EOF -->
