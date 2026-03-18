#!/usr/bin/env python3
# Timestamp: "2025-08-21 20:09:30 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/logging/__init__.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Modular logging utilities for SciTeX.

This module provides enhanced logging capabilities with both console and file output,
ensuring consistent logging across the SciTeX package.

Migration:
    # OLD (deprecated)
    from scitex import logging
    logger = logging.getLogger(__name__)

    # NEW (recommended)
    from scitex import logging
    logger = logging.getLogger(__name__)

Usage:
    from scitex import logging  # DEPRECATED
    logger = logging.getLogger(__name__)
    logger.success("Operation completed successfully")
    logger.fail("Operation failed")

    # Configure logging with file output
    logging.configure(level='info', enable_file=True)

    # Get current log file location
    log_file = logging.get_log_path()
"""

import logging as _logging

from . import llm
from ._config import (
    configure,
    enable_file_logging,
    get_level,
    get_log_path,
    is_file_logging_enabled,
    set_level,
)
from ._context import log_to_file

# Errors (exceptions)
from ._errors import (
    AuthenticationError,
    AxisError,
    BibTeXEnrichmentError,
    ConfigFileNotFoundError,
    ConfigKeyError,
    ConfigurationError,
    DataError,
    DOIResolutionError,
    DTypeError,
    EnrichmentError,
    FigureNotFoundError,
    FileFormatError,
    InvalidPathError,
    IOError,
    LoadError,
    ModelError,
    NNError,
    PathError,
    PathNotFoundError,
    PDFDownloadError,
    PDFExtractionError,
    PlottingError,
    SaveError,
    ScholarError,
    SciTeXError,
    SearchError,
    ShapeError,
    StatsError,
    TemplateError,
    TemplateViolationError,
    TestError,
    TranslatorError,
    check_file_exists,
    check_path,
    check_shape_compatibility,
)
from ._formatters import SciTeXConsoleFormatter as _SciTeXConsoleFormatter
from ._formatters import SciTeXFileFormatter as _SciTeXFileFormatter
from ._handlers import create_console_handler as _create_console_handler
from ._handlers import create_file_handler as _create_file_handler
from ._handlers import get_default_log_path as _get_default_log_path

# Import modular components
from ._levels import CRITICAL, DEBUG, ERROR, FAIL, INFO, SUCCESS, WARNING
from ._logger import SciTeXLogger as _SciTeXLogger
from ._logger import setup_logger_class as _setup_logger_class
from ._print_capture import PrintCapture as _PrintCapture
from ._print_capture import disable_print_capture as _disable_print_capture
from ._print_capture import enable_print_capture as _enable_print_capture
from ._print_capture import is_print_capture_enabled as _is_print_capture_enabled
from ._Tee import Tee, tee

# Warnings (like Python's warnings module)
from ._warnings import (
    DataLossWarning,
    PerformanceWarning,
    SciTeXDeprecationWarning,
    SciTeXWarning,
    StyleWarning,
    UnitWarning,
    filterwarnings,
    resetwarnings,
    warn,
    warn_data_loss,
    warn_deprecated,
    warn_performance,
)

# Re-export standard logging functions for compatibility
getLogger = _logging.getLogger
_basicConfig = _logging.basicConfig
_disable = _logging.disable

level_by_env = os.getenv("SCITEX_LOGGING_LEVEL", "INFO").upper()
level_map = {
    "DEBU": DEBUG,
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARN": WARNING,
    "WARNING": WARNING,
    "ERRO": ERROR,
    "ERROR": ERROR,
    "CRIT": CRITICAL,
    "CRITICAL": CRITICAL,
    "SUCC": SUCCESS,
    "SUCCESS": SUCCESS,
    "FAIL": FAIL,
}
level = level_map.get(level_by_env, INFO)

# Auto-configure logging on import with file logging enabled, print capture disabled by default
configure(level=level, enable_file=True, enable_console=True, capture_prints=False)

# Export public API
__all__ = [
    # Core logging functions
    "getLogger",
    # Log levels
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "SUCCESS",
    "FAIL",
    # LLM session logs
    "llm",
    # Configuration
    "configure",
    "set_level",
    "get_level",
    "enable_file_logging",
    "is_file_logging_enabled",
    "get_log_path",
    "Tee",
    "tee",
    # Context managers
    "log_to_file",
    # Warnings (like Python's warnings module)
    "SciTeXWarning",
    "UnitWarning",
    "StyleWarning",
    "SciTeXDeprecationWarning",
    "PerformanceWarning",
    "DataLossWarning",
    "warn",
    "filterwarnings",
    "resetwarnings",
    "warn_deprecated",
    "warn_performance",
    "warn_data_loss",
    # Errors (exceptions)
    "SciTeXError",
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigKeyError",
    "IOError",
    "FileFormatError",
    "SaveError",
    "LoadError",
    "ScholarError",
    "SearchError",
    "EnrichmentError",
    "PDFDownloadError",
    "DOIResolutionError",
    "PDFExtractionError",
    "BibTeXEnrichmentError",
    "TranslatorError",
    "AuthenticationError",
    "PlottingError",
    "FigureNotFoundError",
    "AxisError",
    "DataError",
    "ShapeError",
    "DTypeError",
    "PathError",
    "InvalidPathError",
    "PathNotFoundError",
    "TemplateError",
    "TemplateViolationError",
    "NNError",
    "ModelError",
    "StatsError",
    "TestError",
    # Validation helpers
    "check_path",
    "check_file_exists",
    "check_shape_compatibility",
]

# EOF
