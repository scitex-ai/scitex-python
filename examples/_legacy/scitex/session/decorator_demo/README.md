# Session Decorator Demo

## Overview

This demo showcases the new `@session` decorator for simplified SciTeX session management. It performs the same analysis as `../scitex_session_demo` but with **80% less boilerplate code**.

## What This Demo Does

1. Generates synthetic data (linear relationship with noise)
2. Saves raw data
3. Creates visualization with regression line
4. Computes statistics
5. Saves results

## Usage

### Basic Usage

```bash
# Run with default parameters
python scripts/session_decorator_demo.py

# Show help (auto-generated from function signature!)
python scripts/session_decorator_demo.py --help

# Custom parameters
python scripts/session_decorator_demo.py --n-samples 200 --verbose
```

### Available Options

- `--n-samples`: Number of samples to generate (default: 100)
- `--verbose`: Enable verbose output (default: False)

## Output Structure

```
session_decorator_demo_out/
├── RUNNING/
│   └── 2025Y-11M-05D-XXhXXmXXs_XXXX-main/
│       ├── CONFIGS/
│       │   ├── CONFIG.pkl
│       │   └── CONFIG.yaml
│       ├── logs/
│       │   ├── stdout.log
│       │   └── stderr.log
│       ├── sample_data.npy
│       ├── visualization.jpg
│       └── results.json
└── FINISHED_SUCCESS/  (after completion)
    └── 2025Y-11M-05D-XXhXXmXXs_XXXX-main/
        └── (same files)
```

## Code Comparison

### Old Way (scitex_session_demo.py) - 189 lines

```python
#!/usr/bin/env python3
import argparse
import scitex as stx

def main(args):
    # Your analysis code
    x, y = generate_sample_data(args.n_samples)
    # ... more code ...
    return 0

def parse_args():
    parser = argparse.ArgumentParser(description="SciTeX Framework Demo Script")
    parser.add_argument("--n-samples", "-n", type=int, default=100, ...)
    parser.add_argument("--verbose", "-v", action="store_true", ...)
    return parser.parse_args()

def run_main():
    global CONFIG, CC, sys, plt, rng
    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys, plt, args=args, file=__FILE__,
        sdir_suffix=None, verbose=args.verbose, agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG, verbose=args.verbose, notify=False,
        message="Demo completed", exit_status=exit_status,
    )

if __name__ == "__main__":
    run_main()
```

### New Way (session_decorator_demo.py) - 158 lines (with comments)

```python
#!/usr/bin/env python3
from scitex.session import session
import scitex as stx

@session(verbose=True, agg=True)
def main(n_samples: int = 100, verbose: bool = False):
    """Main execution function.

    Args:
        n_samples: Number of samples to generate
        verbose: Enable verbose output
    """
    # Your analysis code
    x, y = generate_sample_data(n_samples)
    # ... more code ...
    return 0

if __name__ == "__main__":
    main()
```

## Key Improvements

### 1. No More Boilerplate

**Before:**
- Manual `parse_args()` function (15+ lines)
- Manual `run_main()` function (20+ lines)
- Global variable declarations
- Manual session.start() and session.close()

**After:**
- Just add `@session` decorator
- Parameters become CLI arguments automatically
- Session management is automatic

### 2. Type Hints → CLI Arguments

The decorator automatically converts function parameters to CLI arguments:

```python
@session
def main(n_samples: int = 100, verbose: bool = False):
    pass
```

Automatically creates:
```bash
python script.py --n-samples 200 --verbose
```

### 3. Auto-Generated Help

```bash
$ python scripts/session_decorator_demo.py --help

usage: session_decorator_demo.py [-h] [--n-samples N_SAMPLES] [--verbose]

Main execution function with @session decorator.

This demonstrates the simplified session management approach.
No need for parse_args(), run_main(), or manual session.start()/close()!

options:
  -h, --help            show this help message and exit
  --n-samples N_SAMPLES
                        (default: 100)
  --verbose             (default: False)
```

### 4. Session Variables Available

These are automatically available in your function:

- `CONFIG`: Configuration dictionary
- `plt`: Configured matplotlib
- `CC`: Color cycle
- `rng`: Random state manager

### 5. Automatic Error Handling

- Exceptions are caught and logged
- Output moves to `FINISHED_ERROR/` on failure
- Output moves to `FINISHED_SUCCESS/` on success

## Line Count Comparison

| Metric | Old Way | New Way | Reduction |
|--------|---------|---------|-----------|
| Total lines | 189 | 158 | 16% |
| Boilerplate | ~60 | ~5 | 92% |
| Core logic | ~130 | ~130 | Same |
| Functions to write | 4 (main, parse_args, run_main, helpers) | 1 (main + helpers) | 75% |

## Benefits

1. **Simpler**: Less code to write and maintain
2. **Cleaner**: Focus on analysis, not infrastructure
3. **Safer**: Automatic error handling
4. **Consistent**: Same structure across all scripts
5. **Self-documenting**: CLI help from docstrings
6. **Type-safe**: Type hints enforce correct CLI types

## When to Use Old vs New

### Use `@session` Decorator (New Way) When:
- ✅ Writing analysis scripts
- ✅ Prototyping
- ✅ Simple to moderate complexity
- ✅ Standard CLI arguments

### Use Traditional Approach (Old Way) When:
- ✅ Need custom argparse features (subparsers, actions)
- ✅ Very complex initialization
- ✅ Need fine-grained control over session lifecycle
- ✅ Legacy scripts (both work side-by-side!)

## Migration Path

To migrate existing scripts:

1. Import decorator:
   ```python
   from scitex.session import session
   ```

2. Add decorator to main:
   ```python
   @session
   def main(param1: type, param2: type = default):
       # Your code (use param1, param2 directly instead of args.param1)
       pass
   ```

3. Remove:
   - `parse_args()` function
   - `run_main()` function
   - Global declarations
   - `if __name__ == '__main__'` boilerplate (just keep `main()` call)

4. Update function signature to use direct parameters instead of `args` object

## Summary

The `@session` decorator makes SciTeX scripts:
- 📉 80% less boilerplate
- 📈 More readable
- 🚀 Faster to write
- 🎯 Easier to maintain
- ✨ More Pythonic

Try it for your next analysis script!
