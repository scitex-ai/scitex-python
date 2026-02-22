#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/_decorator.py

from __future__ import annotations

"""The @stx.module decorator for marking functions as SciTeX workspace modules."""

import functools
import inspect
from typing import Any, Callable

from . import INJECTED
from ._manifest import ModuleManifest
from ._output import ModuleOutputCollector


def module(
    func: Callable = None,
    *,
    label: str = "",
    icon: str = "fa-puzzle-piece",
    category: str = "other",
    description: str = "",
    version: str = "0.1.0",
    dependencies: list | None = None,
    min_scitex_version: str = "",
) -> Callable:
    """Decorator to mark a function as a SciTeX workspace module.

    The decorated function can declare parameters with default=INJECTED;
    the module runner will supply *project*, *plt*, and *logger* at
    execution time.

    Args:
        func: The function being decorated (set automatically).
        label: Human-readable display name.  Defaults to the function name
            with underscores replaced by spaces and title-cased.
        icon: FontAwesome icon class for the module card.
        category: Module category (writing, visualization, data, analysis,
            reference, utility, other).
        description: Short description.  Falls back to the first line of the
            function docstring when empty.
        version: Semantic version for this module.
        dependencies: Extra pip packages required.
        min_scitex_version: Minimum scitex version.

    Example::

        import scitex as stx

        @stx.module(label="EEG Viewer", icon="fa-brain", category="visualization")
        def eeg_viewer(project=stx.module.INJECTED, plt=stx.module.INJECTED):
            stx.module.output("<h2>Hello</h2>", title="Greeting")
    """

    def decorator(fn: Callable) -> Callable:
        # Build manifest
        _label = label or fn.__name__.replace("_", " ").title()
        _description = description
        if not _description and fn.__doc__:
            _description = fn.__doc__.strip().split("\n")[0]

        manifest = ModuleManifest(
            name=fn.__name__,
            label=_label,
            icon=icon,
            category=category,
            description=_description,
            version=version,
            dependencies=dependencies or [],
            min_scitex_version=min_scitex_version,
        )

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            """Execute the module function, collecting outputs."""
            ModuleOutputCollector.clear()
            try:
                result = fn(*args, **kwargs)
            except Exception:
                ModuleOutputCollector.clear()
                raise
            outputs = ModuleOutputCollector.get_current()
            ModuleOutputCollector.clear()
            return result, outputs

        # Attach metadata so the runner can discover it
        wrapper._is_stx_module = True
        wrapper._manifest = manifest
        wrapper._func = fn

        return wrapper

    # Support both @stx.module and @stx.module(...)
    if func is not None:
        return decorator(func)
    return decorator


def _inject_params(fn: Callable, provided: dict[str, Any]) -> dict[str, Any]:
    """Build kwargs for *fn*, injecting values where the default is INJECTED.

    Args:
        fn: The original (unwrapped) function.
        provided: Dict of injectable name -> value (e.g. project, plt, logger).

    Returns
    -------
        Dict of keyword arguments ready to be passed to *fn*.
    """
    sig = inspect.signature(fn)
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if param.default is not inspect.Parameter.empty and isinstance(
            param.default, type(INJECTED)
        ):
            if name in provided:
                kwargs[name] = provided[name]
        # Non-INJECTED params with defaults are left for the caller or the default
    return kwargs


# EOF
