---
name: stx.session
description: Experiment session management with auto-organized outputs, config injection, and reproducibility tracking.
---

# stx.session

The `stx.session` module manages the full lifecycle of a reproducible experiment:
output directories, logging, matplotlib configuration, YAML config loading, CLI
generation, and clean teardown. The primary interface is the `@stx.session`
decorator.

## Sub-skills

### Core Usage
- [decorator.md](decorator.md) — `@stx.session` decorator: behavior, options, direct vs CLI mode, full script template
- [cli-generation.md](cli-generation.md) — Auto-ArgumentParser from function signatures: type mapping, short forms, `Literal` choices, `--help` epilog

### Session Internals
- [lifecycle.md](lifecycle.md) — `start()` / `close()` / `running2finished()`: what each does, output directory structure, CONFIG keys
- [config.md](config.md) — CONFIG DotDict: YAML namespacing, session keys, CLI args, debug mode, persistence
- [injected-globals.md](injected-globals.md) — The five injected objects (CONFIG, plt, COLORS, rngg, logger): origin, usage, INJECTED sentinel

### Advanced
- [session-manager.md](session-manager.md) — `SessionManager` class: tracking concurrent sessions, global singleton, clew hooks

## Quick Reference

```python
import scitex as stx

# Primary API: decorator
@stx.session
def main(
    data_path: str,
    threshold: float = 0.5,
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Analyze data. Becomes --help description."""
    logger.info(f"Output: {CONFIG.SDIR_RUN}")
    stx.io.save(process(data_path, threshold), "result.csv")
    return 0  # exit code

if __name__ == "__main__":
    main()  # no args -> CLI mode with full session management

# Manual API
import sys, matplotlib.pyplot as plt
CONFIG, sys.stdout, sys.stderr, plt, COLORS, rng = stx.session.start(sys, plt)
# ... experiment code ...
stx.session.close(CONFIG)

# Session manager
manager = stx.session.SessionManager()
active = manager.get_active_sessions()
```

## Public API

| Symbol | Description |
|---|---|
| `stx.session` / `@stx.session` | Decorator (also callable as `stx.session(verbose=True)`) |
| `stx.session.start(...)` | Manual session start; returns `(CONFIG, stdout, stderr, plt, COLORS, rng)` |
| `stx.session.close(CONFIG, ...)` | Manual session close; promotes dir to `FINISHED_*` |
| `stx.session.running2finished(CONFIG, exit_status)` | Move output dir from `RUNNING/` to `FINISHED_*/` |
| `stx.session.run(func, ...)` | Explicit alternative to decorator |
| `stx.session.SessionManager` | Class for tracking multiple sessions |
| `stx.session.INJECTED` | Sentinel to mark decorator-injected parameters |
| `stx.INJECTED` | Same sentinel, re-exported from `scitex.__init__` |
