#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/_runner.py

from __future__ import annotations

"""Execution engine for SciTeX workspace modules.

Imports a module .py file, locates the @stx.module decorated function,
calls it with injected parameters, collects outputs, and serializes the
results to an output directory.

Can be invoked as::

    python -m scitex.module._runner <module_path> --project-path <path> --output-dir <dir>
"""

import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any

from ._decorator import _inject_params
from ._renderer import render_outputs

logger = logging.getLogger(__name__)


def discover_module_func(module_path: str | Path) -> Any:
    """Import a .py file and return the first @stx.module decorated callable.

    Args:
        module_path: Filesystem path to the module .py file.

    Returns
    -------
        The decorated wrapper function (has ``_is_stx_module`` attribute).

    Raises
    ------
        FileNotFoundError: If the path does not exist.
        ValueError: If no @stx.module function is found in the file.
    """
    module_path = Path(module_path)
    if not module_path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")

    spec = importlib.util.spec_from_file_location(
        f"stx_module_{module_path.stem}", str(module_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for attr_name in dir(mod):
        obj = getattr(mod, attr_name)
        if callable(obj) and getattr(obj, "_is_stx_module", False):
            return obj

    raise ValueError(f"No @stx.module decorated function found in {module_path}")


def run_module(
    module_path: str | Path,
    project_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Execute a module and write serialized results to *output_dir*.

    Args:
        module_path: Path to the module .py file.
        project_path: Path to the SciTeX project directory.
        output_dir: Directory where result JSON and artifacts are written.

    Returns
    -------
        Dict with keys ``manifest``, ``outputs``, ``error``.
    """
    module_path = Path(module_path)
    project_path = Path(project_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wrapper = discover_module_func(module_path)
    manifest = wrapper._manifest
    original_fn = wrapper._func

    # Prepare injectable values
    injectables = _build_injectables(project_path)
    kwargs = _inject_params(original_fn, injectables)

    # Execute
    error_msg = ""
    outputs_rendered: list[dict] = []
    try:
        _result, outputs = wrapper(**kwargs)
        outputs_rendered = render_outputs(outputs)
    except Exception as exc:
        logger.exception("Module execution failed: %s", exc)
        error_msg = str(exc)

    result = {
        "manifest": manifest.to_dict(),
        "outputs": outputs_rendered,
        "error": error_msg,
    }

    # Write result JSON
    result_path = output_dir / "result.json"
    result_path.write_text(json.dumps(result, indent=2, default=str))
    logger.info("Module output written to %s", result_path)

    return result


def _build_injectables(project_path: Path) -> dict[str, Any]:
    """Build the dict of values available for INJECTED parameter injection.

    Args:
        project_path: The project directory path to inject.

    Returns
    -------
        Dict mapping parameter names to their injectable values.
    """
    injectables: dict[str, Any] = {
        "project": project_path,
    }

    # Inject matplotlib.pyplot if available
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        injectables["plt"] = plt
    except ImportError:
        pass

    # Inject a logger
    injectables["logger"] = logging.getLogger("stx.module.user")

    return injectables


# -- CLI entry point ---------------------------------------------------------


def _cli_main() -> None:
    """Entry point for ``python -m scitex.module._runner``."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a SciTeX workspace module.")
    parser.add_argument("module_path", help="Path to the module .py file")
    parser.add_argument(
        "--project-path",
        required=True,
        help="Path to the SciTeX project directory",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for output JSON and artifacts",
    )
    args = parser.parse_args()

    result = run_module(args.module_path, args.project_path, args.output_dir)
    if result["error"]:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {len(result['outputs'])} output(s) written")


if __name__ == "__main__":
    _cli_main()


# EOF
