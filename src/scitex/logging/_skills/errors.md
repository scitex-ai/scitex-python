---
description: SciTeX exception hierarchy — structured errors with context dicts and suggestions, covering IO, configuration, data, path, plotting, scholar, stats, and NN errors.
---

# Errors

All SciTeX exceptions inherit from `SciTeXError`. Each exception carries an optional `context` dict and `suggestion` string, printed as part of the error message.

## SciTeXError (base)

```python
SciTeXError(message, context=None, suggestion=None)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | str | required | Error description |
| `context` | dict or None | `None` | Key-value pairs printed as "Context:" section |
| `suggestion` | str or None | `None` | Suggested fix, printed as "Suggestion:" line |

## Exception hierarchy

```
SciTeXError
├── ConfigurationError
│   ├── ConfigFileNotFoundError(filepath)
│   └── ConfigKeyError(key, available_keys=None)
├── IOError
│   ├── FileFormatError(filepath, expected_format=None, actual_format=None)
│   ├── SaveError(filepath, reason)
│   └── LoadError(filepath, reason)
├── ScholarError
│   ├── SearchError(query, source, reason)
│   ├── EnrichmentError(paper_title, reason)
│   ├── PDFDownloadError(url, reason)
│   ├── DOIResolutionError(doi, reason)
│   ├── PDFExtractionError(filepath, reason)
│   ├── BibTeXEnrichmentError(bibtex_file, reason)
│   ├── TranslatorError(translator_name, reason)
│   └── AuthenticationError(provider, reason="")
├── PlottingError
│   ├── FigureNotFoundError(fig_id)
│   └── AxisError(message, axis_info=None)
├── DataError
│   ├── ShapeError(expected_shape, actual_shape, operation)
│   └── DTypeError(expected_dtype, actual_dtype, operation)
├── PathError
│   ├── InvalidPathError(path, reason)
│   └── PathNotFoundError(path)
├── TemplateError
│   └── TemplateViolationError(filepath, violation)
├── NNError
│   └── ModelError(model_name, reason)
└── StatsError
    └── TestError(test_name, reason)
```

## Import

```python
from scitex.logging import (
    SciTeXError,
    ConfigurationError, ConfigFileNotFoundError, ConfigKeyError,
    IOError, FileFormatError, SaveError, LoadError,
    ScholarError, SearchError, EnrichmentError,
    PDFDownloadError, DOIResolutionError, PDFExtractionError,
    BibTeXEnrichmentError, TranslatorError, AuthenticationError,
    PlottingError, FigureNotFoundError, AxisError,
    DataError, ShapeError, DTypeError,
    PathError, InvalidPathError, PathNotFoundError,
    TemplateError, TemplateViolationError,
    NNError, ModelError,
    StatsError, TestError,
)
```

## Validation helpers

```python
stx.logging.check_path(path)
```
Raises `InvalidPathError` if `path` is not a string or does not start with `"./"` or `"../"`.

```python
stx.logging.check_file_exists(filepath)
```
Raises `PathNotFoundError` if `os.path.exists(filepath)` is `False`.

```python
stx.logging.check_shape_compatibility(shape1, shape2, operation)
```
Raises `ShapeError` if `shape1 != shape2`.

## Examples

```python
from scitex.logging import SaveError, ShapeError, ConfigKeyError
import scitex as stx

# Raise a structured error
raise SaveError("./results/output.csv", "permission denied")
# SciTeX Error: Failed to save to ./results/output.csv: permission denied
# Context:
#   filepath: ./results/output.csv
#   reason: permission denied
# Suggestion: Check file permissions and disk space

# Shape validation
stx.logging.check_shape_compatibility((100, 3), (100, 4), "matrix multiply")
# Raises: ShapeError

# Config key missing
raise ConfigKeyError("experiment_name", available_keys=["lr", "batch_size"])
# SciTeX Error: Configuration key 'experiment_name' not found
# Context:
#   missing_key: experiment_name
#   available_keys: ['lr', 'batch_size']
# Suggestion: Add 'experiment_name' to your configuration file or check for typos

# Catch any SciTeX error
try:
    stx.logging.check_path("results/output.csv")  # missing leading ./
except stx.logging.InvalidPathError as e:
    print(e)
```
