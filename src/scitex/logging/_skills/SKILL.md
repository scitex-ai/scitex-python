---
name: stx.logging
description: Enhanced logging with custom levels (success/fail), simultaneous console and file output, structured exceptions, warning system, stream capture, and Claude Code JSONL log analysis.
user-invocable: false
---

# stx.logging

`stx.logging` extends Python's standard `logging` module for scientific workflows. It is auto-configured on `import scitex`.

## Sub-skills

### Logger
- [logger.md](logger.md) — `SciTeXLogger`: extended log methods with `success()`, `fail()`, `indent`, `sep`, `c` (color), `pprint` kwargs; `logger.to()` for scoped file logging

### Configuration
- [configure.md](configure.md) — `configure()`, `set_level()`, `get_level()`, `enable_file_logging()`, `get_log_path()`, environment variables, format templates

### Context Managers
- [context.md](context.md) — `log_to_file(path, level, mode)`: temporarily attach a file handler to the root logger for a `with` block

### Stream Capture
- [tee.md](tee.md) — `Tee` class and `tee(sys)` function: duplicate stdout/stderr to both console and log files; progress bar filtering for stderr

### Warnings
- [warnings.md](warnings.md) — `warn()`, `filterwarnings()`, `resetwarnings()`, `warn_deprecated()`, `warn_performance()`, `warn_data_loss()`; warning categories: `UnitWarning`, `StyleWarning`, `SciTeXDeprecationWarning`, `PerformanceWarning`, `DataLossWarning`

### Errors
- [errors.md](errors.md) — full exception hierarchy under `SciTeXError`; structured errors with `context` dicts and `suggestion` strings; validation helpers `check_path()`, `check_file_exists()`, `check_shape_compatibility()`

### LLM Session Logs
- [llm.md](llm.md) — `stx.logging.llm`: parse Claude Code JSONL files into `ClaudeCodeSession`; HTML rendering, DAG/Mermaid export, action extraction, shell script replay, multi-session dashboard; CLI via `python -m scitex.logging.llm`

## Minimal usage

```python
import scitex as stx

logger = stx.logging.getLogger(__name__)

logger.info("Processing started")
logger.success("Experiment complete")
logger.fail("Validation failed")

with stx.logging.log_to_file("./logs/run.log"):
    logger.info("This also goes to run.log")

stx.logging.configure(level="debug", enable_file=True)
```
