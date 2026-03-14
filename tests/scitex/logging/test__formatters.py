# Add your tests here
import importlib.util
import logging
import os
import sys

import pytest

# Import _formatters directly without triggering scitex.logging.__init__
_formatters_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "src",
    "scitex",
    "logging",
    "_formatters.py",
)
spec = importlib.util.spec_from_file_location("_formatters", _formatters_path)
_formatters = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_formatters)

SciTeXConsoleFormatter = _formatters.SciTeXConsoleFormatter
SciTeXFileFormatter = _formatters.SciTeXFileFormatter
FORMAT_TEMPLATES = _formatters.FORMAT_TEMPLATES
# Note: FORCE_COLOR is evaluated at module load time, so we test via subprocess


class TestSciTeXConsoleFormatter:
    """Tests for SciTeXConsoleFormatter."""

    def test_basic_format(self):
        """Test basic message formatting without newlines."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Hello world",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        assert "INFO: Hello world" in result

    def test_leading_newline_extracted(self):
        """Test that leading newlines are moved before the prefix."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="\n============",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        # Leading newline should be before prefix
        assert result.startswith("\n")
        assert "INFO: ============" in result
        # Should NOT have "INFO: \n"
        assert "INFO: \n" not in result

    def test_multiple_leading_newlines(self):
        """Test multiple leading newlines are preserved."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="\n\n\nTriple newline",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        assert result.startswith("\n\n\n")
        assert "INFO: Triple newline" in result

    def test_internal_newlines_get_prefix(self):
        """Test that each line in multi-line message gets the level prefix."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Line 1\nLine 2\nLine 3",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        lines = result.split("\n")
        # Each line should have the INFO: prefix
        assert lines[0] == "INFO: Line 1"
        assert lines[1] == "INFO: Line 2"
        assert lines[2] == "INFO: Line 3"

    def test_combined_leading_and_internal_newlines(self):
        """Test both leading and internal newlines handled correctly."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="\nFirst\nSecond",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        assert result.startswith("\n")
        lines = result.split("\n")
        assert lines[0] == ""  # Leading newline
        assert lines[1] == "INFO: First"
        assert lines[2] == "INFO: Second"  # Each line gets prefix

    def test_empty_continuation_lines_stay_empty(self):
        """Test that empty lines in multi-line messages stay empty (no prefix)."""
        formatter = SciTeXConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Line 1\n\nLine 3",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        lines = result.split("\n")
        assert lines[0] == "INFO: Line 1"
        assert lines[1] == ""  # Empty line stays empty
        assert lines[2] == "INFO: Line 3"

    def test_indent_level_applied(self):
        """Test that indent level is applied correctly."""
        formatter = SciTeXConsoleFormatter(indent_width=2)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Indented message",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        record.indent = 2
        result = formatter.format(record)
        assert "INFO:     Indented message" in result  # 4 spaces (2 levels * 2 width)


class TestSciTeXFileFormatter:
    """Tests for SciTeXFileFormatter."""

    def test_file_format_includes_timestamp(self):
        """Test that file formatter includes timestamp."""
        formatter = SciTeXFileFormatter()
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="File log message",
            args=(),
            exc_info=None,
        )
        record.levelname = "INFO"
        result = formatter.format(record)
        assert "test.module" in result
        assert "INFO" in result
        assert "File log message" in result


class TestFormatTemplates:
    """Tests for format templates."""

    def test_all_templates_exist(self):
        """Test that all expected templates are defined."""
        expected = ["minimal", "default", "detailed", "debug", "full"]
        for template in expected:
            assert template in FORMAT_TEMPLATES

    def test_templates_contain_message(self):
        """Test that all templates include message placeholder."""
        for name, template in FORMAT_TEMPLATES.items():
            assert "%(message)s" in template, f"Template '{name}' missing message"


class TestForceColor:
    """Tests for SCITEX_FORCE_COLOR environment variable."""

    @pytest.fixture(autouse=True)
    def setup_pythonpath(self):
        """Set up PYTHONPATH for subprocess tests."""
        project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
        self.project_root = os.path.abspath(project_root)
        self.src_dir = os.path.join(self.project_root, "src")
        existing_pythonpath = os.environ.get("PYTHONPATH", "")
        if existing_pythonpath:
            self.pythonpath = f"{self.src_dir}:{existing_pythonpath}"
        else:
            self.pythonpath = self.src_dir

    def test_force_color_env_parsing(self):
        """Test that FORCE_COLOR environment variable values are parsed correctly."""
        import subprocess

        # Test that FORCE_COLOR=1 enables colors in piped output
        result = subprocess.run(
            [
                "python",
                "-c",
                """
import os
os.environ['SCITEX_FORCE_COLOR'] = '1'
import importlib.util
spec = importlib.util.spec_from_file_location('_formatters',
    'src/scitex/logging/_formatters.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('FORCE_COLOR:', mod.FORCE_COLOR)
""",
            ],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..", "..", ".."),
        )
        assert "FORCE_COLOR: True" in result.stdout

    @pytest.mark.slow
    @pytest.mark.timeout(120)
    def test_force_color_adds_ansi_codes(self):
        """Test that FORCE_COLOR=1 adds ANSI color codes to piped output."""
        import subprocess

        result = subprocess.run(
            [
                "python",
                "-c",
                """
from scitex.logging import getLogger
logger = getLogger('test')
logger.warning('test warning')
""",
            ],
            env={
                **os.environ,
                "SCITEX_FORCE_COLOR": "1",
                "PYTHONPATH": self.pythonpath,
            },
            capture_output=True,
            text=True,
            cwd=self.project_root,
            timeout=90,
        )
        # ANSI color codes should be present (yellow for warning: \033[33m)
        # Logging output goes to stderr
        output = result.stdout + result.stderr
        assert "\033[33m" in output or "\x1b[33m" in output

    @pytest.mark.slow
    @pytest.mark.timeout(120)
    def test_no_force_color_no_ansi_codes(self):
        """Test that without FORCE_COLOR, piped output has no ANSI codes."""
        import subprocess

        # Create a clean environment without SCITEX_FORCE_COLOR but with PYTHONPATH
        env = {k: v for k, v in os.environ.items() if k != "SCITEX_FORCE_COLOR"}
        env["PYTHONPATH"] = self.pythonpath

        result = subprocess.run(
            [
                "python",
                "-c",
                """
from scitex.logging import getLogger
logger = getLogger('test')
logger.warning('test warning')
""",
            ],
            env=env,
            capture_output=True,
            text=True,
            cwd=self.project_root,
            timeout=90,
        )
        # ANSI color codes should NOT be present when piped without FORCE_COLOR
        # Logging output goes to stderr
        output = result.stdout + result.stderr
        assert "\033[33m" not in output
        assert "\x1b[33m" not in output

    def test_force_color_accepts_various_true_values(self):
        """Test that FORCE_COLOR accepts '1', 'true', 'yes' as true values."""
        import subprocess

        for value in ["1", "true", "TRUE", "yes", "YES"]:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
import os
os.environ['SCITEX_FORCE_COLOR'] = '{value}'
import importlib.util
spec = importlib.util.spec_from_file_location('_formatters',
    'src/scitex/logging/_formatters.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('FORCE_COLOR:', mod.FORCE_COLOR)
""",
                ],
                capture_output=True,
                text=True,
                cwd=os.path.join(os.path.dirname(__file__), "..", "..", ".."),
            )
            assert "FORCE_COLOR: True" in result.stdout, f"Failed for value: {value}"

    def test_force_color_false_values(self):
        """Test that FORCE_COLOR rejects invalid values."""
        import subprocess

        for value in ["0", "false", "no", ""]:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
import os
os.environ['SCITEX_FORCE_COLOR'] = '{value}'
import importlib.util
spec = importlib.util.spec_from_file_location('_formatters',
    'src/scitex/logging/_formatters.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('FORCE_COLOR:', mod.FORCE_COLOR)
""",
                ],
                capture_output=True,
                text=True,
                cwd=os.path.join(os.path.dirname(__file__), "..", "..", ".."),
            )
            assert "FORCE_COLOR: False" in result.stdout, f"Failed for value: {value}"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_formatters.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-10-11 00:17:43 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/logging/_formatters.py
# # ----------------------------------------
# from __future__ import annotations
# import os
#
# __FILE__ = "./src/scitex/logging/_formatters.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# __FILE__ = __file__
# """Custom formatters for SciTeX logging."""
#
# import logging
# import sys
#
# # Global format configuration via environment variable
# # Options: default, minimal, detailed, debug, full
# # SCITEX_LOG_FORMAT=debug python script.py
# LOG_FORMAT = os.getenv("SCITEX_LOG_FORMAT", "default")
#
# # Force color output even when stdout is not a TTY (e.g., when piping through tee)
# # SCITEX_FORCE_COLOR=1 python script.py | tee output.log
# FORCE_COLOR = os.getenv("SCITEX_FORCE_COLOR", "").lower() in ("1", "true", "yes")
#
# # Available format templates
# FORMAT_TEMPLATES = {
#     "minimal": "%(levelname)s: %(message)s",
#     "default": "%(levelname)s: %(message)s",
#     "detailed": "%(levelname)s: [%(name)s] %(message)s",
#     "debug": "%(levelname)s: [%(filename)s:%(lineno)d - %(funcName)s()] %(message)s",
#     "full": "%(asctime)s - %(levelname)s: [%(filename)s:%(lineno)d - %(name)s.%(funcName)s()] %(message)s",
# }
#
#
# class SciTeXConsoleFormatter(logging.Formatter):
#     """Custom formatter with color support and configurable format."""
#
#     # ANSI color codes for log levels
#     COLORS = {
#         "DEBU": "\033[90m",  # Grey
#         "INFO": "\033[90m",  # Grey
#         "SUCC": "\033[32m",  # Green
#         "WARN": "\033[33m",  # Yellow
#         "FAIL": "\033[91m",  # Light Red
#         "ERRO": "\033[31m",  # Red
#         "CRIT": "\033[35m",  # Magenta
#     }
#
#     # Color name to ANSI code mapping
#     COLOR_NAMES = {
#         "black": "\033[30m",
#         "red": "\033[31m",
#         "green": "\033[32m",
#         "yellow": "\033[33m",
#         "blue": "\033[34m",
#         "magenta": "\033[35m",
#         "cyan": "\033[36m",
#         "white": "\033[37m",
#         "grey": "\033[90m",
#         "light_red": "\033[91m",
#         "light_green": "\033[92m",
#         "light_yellow": "\033[93m",
#         "lightblue": "\033[94m",
#         "light_magenta": "\033[95m",
#         "light_cyan": "\033[96m",
#     }
#
#     RESET = "\033[0m"
#
#     def __init__(self, fmt=None, indent_width=2):
#         """
#         Initialize with format from global config.
#
#         Args:
#             fmt: Format template string
#             indent_width: Number of spaces per indent level (default: 2)
#         """
#         if fmt is None:
#             fmt = FORMAT_TEMPLATES.get(LOG_FORMAT, FORMAT_TEMPLATES["default"])
#         super().__init__(fmt)
#         self.indent_width = indent_width
#
#     def format(self, record):
#         # Handle leading newlines: extract and preserve them
#         msg = str(record.msg) if record.msg else ""
#         leading_newlines = ""
#         while msg.startswith("\n"):
#             leading_newlines += "\n"
#             msg = msg[1:]
#         record.msg = msg
#
#         # Apply indentation if specified in record
#         indent_level = getattr(record, "indent", 0)
#         if indent_level > 0:
#             indent = " " * (indent_level * self.indent_width)
#             record.msg = f"{indent}{record.msg}"
#
#         # Use parent formatter to apply template
#         formatted = super().format(record)
#
#         # Handle internal newlines: each line gets the level prefix
#         if "\n" in formatted:
#             lines = formatted.split("\n")
#             # First line already has prefix from parent formatter
#             # Add prefix to each continuation line
#             prefix = f"{record.levelname}: "
#             formatted = lines[0] + "\n" + "\n".join(
#                 prefix + line if line.strip() else line
#                 for line in lines[1:]
#             )
#
#         # Check if we can use colors (stdout is a tty and not closed, or forced)
#         try:
#             use_colors = FORCE_COLOR or (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())
#         except ValueError:
#             # stdout/stderr is closed
#             use_colors = FORCE_COLOR
#
#         if use_colors:
#             # Check for custom color override
#             custom_color = getattr(record, "color", None)
#
#             if custom_color and custom_color in self.COLOR_NAMES:
#                 # Use custom color
#                 color = self.COLOR_NAMES[custom_color]
#                 return f"{leading_newlines}{color}{formatted}{self.RESET}"
#             else:
#                 # Use default color for log level
#                 levelname = record.levelname
#                 if levelname in self.COLORS:
#                     color = self.COLORS[levelname]
#                     return f"{leading_newlines}{color}{formatted}{self.RESET}"
#
#         return f"{leading_newlines}{formatted}"
#
#
# class SciTeXFileFormatter(logging.Formatter):
#     """Custom formatter for file output without colors."""
#
#     def __init__(self):
#         super().__init__(
#             fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )
#
#
# __all__ = [
#     "SciTeXConsoleFormatter",
#     "SciTeXFileFormatter",
#     "LOG_FORMAT",
#     "FORMAT_TEMPLATES",
#     "FORCE_COLOR",
# ]
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_formatters.py
# --------------------------------------------------------------------------------
