<!-- ---
!-- Timestamp: 2025-11-10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/examples/scitex_session_demo/README.md
!-- --- -->

# SciTeX Session Demo

This example demonstrates two ways to use SciTeX session management.

## Overview

SciTeX session provides automatic:
- Output directory organization
- Logging configuration
- Matplotlib setup
- Reproducibility (RNG management)
- Configuration management
- Error handling and cleanup

## Two Approaches

### 1. Manual Session Management (`scitex_session_demo.py`)

Traditional approach with explicit session control:

```python
def run_main():
    """Initialize scitex framework, run main function, and cleanup."""
    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys, plt, args=args, file=__FILE__, verbose=args.verbose, agg=True
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG, verbose=args.verbose, notify=False,
        message="Demo completed", exit_status=exit_status
    )

if __name__ == "__main__":
    run_main()
```

**When to use:**
- Need fine-grained control over session lifecycle
- Complex custom argument parsing
- Integration with existing code structure
- Multiple entry points

### 2. Decorator Approach (`scitex_session_demo_decorator.py`)

Modern approach using `@stx.session.session` decorator:

```python
@stx.session.session(verbose=False, agg=True)
def demo(n_samples: int = 100, show_config: bool = False):
    """SciTeX session decorator demonstration."""
    # Session variables automatically available:
    # CONFIG, plt, CC, rng

    logger.info(f"Session ID: {CONFIG['ID']}")
    # ... your code ...
    return 0

if __name__ == "__main__":
    demo()  # No arguments = CLI mode
```

**When to use:**
- New scripts/projects
- Want automatic CLI generation
- Prefer cleaner, more concise code
- Don't need complex custom parsing

## Key Differences

| Feature | Manual | Decorator |
|---------|--------|-----------|
| Code lines | ~40 boilerplate | ~5 lines |
| CLI parsing | Manual `argparse` | Auto-generated from signature |
| Session variables | Manual assignment | Auto-injected as globals |
| Error handling | Manual try/except | Automatic |
| Type hints | Optional | Used for CLI types |
| Multiple functions | Flexible | One per script |

## Session Variables

Both approaches provide these global variables:

- **CONFIG** (dict): Session configuration with ID, SDIR, paths, etc.
- **plt** (module): matplotlib.pyplot configured for session
- **CC** (CustomColors): Custom colors for consistent plotting
- **rng** (RandomStateManager): Reproducible random number generation

## Usage Examples

### Manual Version
```bash
python scripts/scitex_session_demo.py --n-samples 100 --verbose
python scripts/scitex_session_demo.py -n 200 -v
```

### Decorator Version
```bash
python scripts/scitex_session_demo_decorator.py --n-samples 100
python scripts/scitex_session_demo_decorator.py --n-samples 200 --show-config
python scripts/scitex_session_demo_decorator.py --help
```

## Output Structure

Both produce organized outputs:

```
scripts/
├── scitex_session_demo_out/
│   ├── sample_data.npy              # Output files at ROOT level
│   ├── visualization.jpg
│   ├── results.json
│   └── FINISHED_SUCCESS/            # Session metadata here
│       └── 2026Y-01M-20D-...-main/
│           ├── CONFIGS/
│           │   ├── CONFIG.pkl
│           │   └── CONFIG.yaml
│           └── logs/
│               ├── stdout.log       # print() captured
│               └── stderr.log       # errors captured
└── data/                            # Central navigation via symlinks
    ├── sample_data.npy -> ../scitex_session_demo_out/sample_data.npy
    └── visualization.jpg -> ../scitex_session_demo_out/visualization.jpg
```

**Key**: Output files go to `script_out/` ROOT, not inside session directories.
Use `symlink_to="./data"` for centralized access across multiple scripts.

## Recommendation

**For new scripts:** Use the decorator approach (`@stx.session.session`)
- Less boilerplate
- Automatic CLI generation
- Cleaner code
- Modern Python practices

**For existing code or complex requirements:** Use manual session management
- More control
- Custom parsing
- Gradual migration
- Multiple entry points

## Advanced Decorator Usage

### With Options
```python
@stx.session.session(verbose=True, notify=True, sdir_suffix="custom_name")
def process(input_file: str, threshold: float = 0.5, debug: bool = False):
    """Process data file."""
    # CONFIG, plt, CC, rng available
    data = stx.io.load(input_file)
    result = analyze(data, threshold, debug)
    stx.io.save(result, "output.csv")
    return 0
```

### Type Hints
```python
from pathlib import Path

@stx.session.session
def analyze(data_path: Path, output_name: str, n_iter: int = 1000):
    """Analyze data with specified iterations."""
    # CLI: --data-path, --output-name, --n-iter
    # Types: Path, str, int automatically handled
    pass
```

## See Also

- [SciTeX Session Documentation](../../src/scitex/session/README.md)
- [SciTeX I/O Documentation](../../src/scitex/io/README.md)
- [SciTeX Logging Documentation](../../src/scitex/logging/README.md)

<!-- EOF -->
