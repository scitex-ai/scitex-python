#!/usr/bin/env python3
# Timestamp: "2025-07-14 15:28:49 (ywatanabe)"
# File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/__init__.py
# ----------------------------------------
import os

__FILE__ = "./src/scitex/__init__.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Minimal scitex initialization.
Modules are imported on-demand to avoid circular dependencies.
"""

# Suppress SQLAlchemy verbose logging (SQL queries, BEGIN/COMMIT)
# Must happen early, before any module imports sqlalchemy
import logging as _stdlib_logging
import warnings

_stdlib_logging.getLogger("sqlalchemy").setLevel(_stdlib_logging.WARNING)
_stdlib_logging.getLogger("sqlalchemy.engine").setLevel(_stdlib_logging.WARNING)
_stdlib_logging.getLogger("sqlalchemy.engine.Engine").setLevel(_stdlib_logging.WARNING)
_stdlib_logging.getLogger("sqlalchemy.pool").setLevel(_stdlib_logging.WARNING)

# Show deprecation warnings from scitex modules (educational for migration)
warnings.filterwarnings("default", category=DeprecationWarning, module="scitex.*")

# Version
from .__version__ import __version__

# BACKWARD COMPATIBILITY: Deprecated items accessible via __getattr__
# These are handled at the end of this file after lazy modules are defined
_DEPRECATED_ATTRS = {"INJECTED", "show_install_guide", "Diagram"}


# Lazy loading for all modules
class _LazyModule:
    def __init__(self, name):
        self._name = name
        self._module = None

    def _load_module(self):
        if self._module is None:
            import importlib

            self._module = importlib.import_module(f".{self._name}", package="scitex")
        return self._module

    def _warn_missing(self):
        warnings.warn(
            f"scitex.{self._name} requires additional dependencies. "
            f"Install with: pip install scitex[{self._name}]",
            UserWarning,
            stacklevel=3,
        )

    def __getattr__(self, attr):
        # Return sensible defaults for dunder attrs without triggering import
        # (prevents Sphinx autodoc crashes when optional deps are missing)
        if attr == "__name__":
            return f"scitex.{self._name}"
        if attr == "__module__":
            return "scitex"
        if attr == "__qualname__":
            return self._name
        if attr == "__path__":
            return []
        if attr == "__file__":
            return None
        if attr == "__loader__":
            return None
        if attr == "__spec__":
            return None
        try:
            return getattr(self._load_module(), attr)
        except (ImportError, ModuleNotFoundError):
            self._module = None  # Reset so next attempt retries
            raise ImportError(
                f"scitex.{self._name} requires additional dependencies. "
                f"Install with: pip install scitex[{self._name}]"
            ) from None

    def __dir__(self):
        """Return dir of the actual module for tab completion."""
        try:
            members = dir(self._load_module())
        except (ImportError, ModuleNotFoundError):
            self._module = None  # Reset so next attempt retries
            self._warn_missing()
            return []
        # Detect broken modules stuck in sys.modules (only have dunder attrs)
        public = [m for m in members if not m.startswith("_")]
        if not public:
            self._module = None
            self._warn_missing()
            return []
        return members

    def __repr__(self):
        if self._module is None:
            return f"<LazyModule(scitex.{self._name}) - not loaded>"
        return repr(self._module)


class _CallableModuleWrapper:
    """Callable module wrapper that acts as both a decorator and a module.

    This allows:
    - @scitex.session (new clean API)
    - @scitex.session.session (old API for backwards compatibility)
    - scitex.session.start() and other module functions

    Example:
        import scitex

        @scitex.session  # Clean! Calls __call__()
        def main(): pass

        @scitex.session.session  # Backwards compatible
        def main(): pass

        scitex.session.start(...)  # Access other functions
    """

    def __init__(self, module_name, main_decorator_name="session"):
        self._module_name = module_name
        self._main_decorator_name = main_decorator_name
        self._module = None
        self._parent_name = None
        self._attr_name = None

    def _setup_persistence(self, parent_name, attr_name):
        """Set up persistence information to prevent replacement."""
        self._parent_name = parent_name
        self._attr_name = attr_name

    def _load_module(self):
        """Lazy load the actual module."""
        if self._module is None:
            import importlib
            import sys

            # Import the module
            self._module = importlib.import_module(
                f".{self._module_name}", package="scitex"
            )

            # Restore ourselves in the parent module's __dict__ to prevent replacement
            if self._parent_name and self._attr_name:
                parent_module = sys.modules.get(self._parent_name)
                if parent_module is not None:
                    setattr(parent_module, self._attr_name, self)

        return self._module

    def __call__(self, *args, **kwargs):
        """When used as @scitex.session"""
        module = self._load_module()
        main_decorator = getattr(module, self._main_decorator_name)
        return main_decorator(*args, **kwargs)

    def __getattr__(self, name):
        """When accessed as scitex.session.session or scitex.session.start"""
        if name == self._main_decorator_name:
            # Return self so @scitex.session.session works
            return self

        # Otherwise, delegate to the actual module
        module = self._load_module()
        return getattr(module, name)

    def __dir__(self):
        """Return dir of the actual module for tab completion."""
        module = self._load_module()
        return dir(module)

    def __repr__(self):
        """Show module representation."""
        if self._module is None:
            return f"<LazyModule(scitex.{self._module_name}) - not loaded>"
        return repr(self._module)


# Create lazy modules
io = _LazyModule("io")
gen = _LazyModule("gen")
plt = _LazyModule("plt")
ai = _LazyModule("ai")
pd = _LazyModule("pd")
str = _LazyModule("str")
stats = _LazyModule("stats")
path = _LazyModule("path")
dict = _LazyModule("dict")
decorators = _LazyModule("decorators")
dsp = _LazyModule("dsp")
nn = _LazyModule("nn")
torch = _LazyModule("torch")
web = _LazyModule("web")
db = _LazyModule("db")
repro = _LazyModule("repro")
scholar = _LazyModule("scholar")
writer = _LazyModule("writer")
fig = _LazyModule("fig")
resource = _LazyModule("resource")
tex = _LazyModule("tex")
linalg = _LazyModule("linalg")
parallel = _LazyModule("parallel")
datetime = _LazyModule("datetime")
dt = _LazyModule("dt")  # Alias for datetime (shorter name)
types = _LazyModule("types")
utils = _LazyModule("utils")
etc = _LazyModule("etc")
context = _LazyModule("context")
dev = _LazyModule("dev")
gists = _LazyModule("gists")
errors = _LazyModule("errors")
units = _LazyModule("units")
logging = _LazyModule("logging")
session = _CallableModuleWrapper("session", main_decorator_name="session")
session._setup_persistence("scitex", "session")
module = _CallableModuleWrapper("module", main_decorator_name="module")
module._setup_persistence("scitex", "module")
capture = _LazyModule("capture")
template = _LazyModule("template")
cloud = _LazyModule("cloud")
tunnel = _LazyModule("tunnel")
config = _LazyModule("config")
audio = _LazyModule("audio")
msword = _LazyModule("msword")
fts = _LazyModule("fts")  # Bundle schemas module
social = _LazyModule("social")  # Social media integration (socialia wrapper)
diagram = _LazyModule("diagram")  # Diagram creation (delegates to figrecipe)
introspect = _LazyModule("introspect")  # Python introspection utilities
sh = _LazyModule("sh")  # Shell command execution
os = _LazyModule("os")  # OS utilities (file operations)
cv = _LazyModule("cv")  # Computer vision utilities
ui = _LazyModule("ui")  # User interface utilities
notification = _LazyModule(
    "notification"
)  # Multi-backend notifications (scitex-notification)
notify = notification  # Backward compat alias
git = _LazyModule("git")  # Git operations
schema = _LazyModule("schema")  # Data schema utilities
canvas = _LazyModule("canvas")  # Canvas utilities for figure composition
security = _LazyModule("security")  # Security utilities
benchmark = _LazyModule("benchmark")  # Benchmarking utilities
bridge = _LazyModule("bridge")  # Bridge utilities
browser = _LazyModule("browser")  # Browser automation
compat = _LazyModule("compat")  # Compatibility utilities
audit = _LazyModule("audit")  # Security auditing
events = _LazyModule("events")  # Event system
media = _LazyModule("media")  # Media utilities
cli = _LazyModule("cli")  # Command-line interface
linter = _LazyModule("linter")  # AST-based linter (delegates to scitex-linter)
clew = _LazyModule("clew")  # Hash-based verification (Ariadne's thread)
notebook = _LazyModule("notebook")  # Jupyter notebook verification & compilation
app = _LazyModule("app")  # App SDK — unified file storage for local + cloud
usage = _CallableModuleWrapper("usage", main_decorator_name="show")
usage._setup_persistence("scitex", "usage")


# Deprecated module aliases — kept accessible via __getattr__ so the directory
# can be deleted. Each access emits a DeprecationWarning and returns the
# canonical lazy module.
_DEPRECATED_MODULE_ALIASES = {
    "ml": "ai",
    "reproduce": "repro",
    "rng": "repro",
    "verify": "clew",
}


# BACKWARD COMPATIBILITY: Module-level __getattr__ for deprecated attributes
def __getattr__(name):
    """Handle deprecated attributes with warnings."""
    if name in _DEPRECATED_MODULE_ALIASES:
        canonical = _DEPRECATED_MODULE_ALIASES[name]
        warnings.warn(
            f"scitex.{name} is deprecated, use scitex.{canonical} instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[canonical]
    if name == "INJECTED":
        warnings.warn(
            "scitex.INJECTED is deprecated, use scitex.session.INJECTED instead",
            DeprecationWarning,
            stacklevel=2,
        )
        from .session import INJECTED

        return INJECTED
    if name == "show_install_guide":
        warnings.warn(
            "scitex.show_install_guide() is deprecated, use scitex.dev.show_install_guide() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        from .dev import show_install_guide

        return show_install_guide
    if name == "Diagram":
        warnings.warn(
            "scitex.Diagram is deprecated, use scitex.diagram.Diagram instead",
            DeprecationWarning,
            stacklevel=2,
        )
        from .diagram import Diagram

        return Diagram
    raise AttributeError(f"module 'scitex' has no attribute '{name}'")


# Centralized path configuration - eager loaded for convenience
# Usage: scitex.PATHS.logs, scitex.PATHS.cache, etc.
from .config import ScitexPaths as _ScitexPaths

PATHS = _ScitexPaths()

# Auto-load cloud hooks if in cloud environment
import os as _os

if _os.environ.get("SCITEX_CLOUD_CODE_WORKSPACE") == "true":
    try:
        from .cloud import _matplotlib_hook
    except Exception:
        pass  # Silently fail if matplotlib not available

__all__ = [
    # Core modules
    "io",
    "gen",
    "plt",
    "ai",
    "pd",
    "str",
    "stats",
    "path",
    "dict",
    "decorators",
    "sh",
    "errors",
    "units",
    "logging",
    "session",
    "module",
    "capture",
    "template",
    "torch",
    "dsp",
    "nn",
    "web",
    "db",
    "repro",
    "scholar",
    "writer",
    "fig",
    "resource",
    "tex",
    "linalg",
    "parallel",
    "datetime",
    "dt",
    "types",
    "utils",
    "etc",
    "context",
    "dev",
    "gists",
    "cloud",
    "tunnel",
    "config",
    "audio",
    "msword",
    "fts",
    "social",
    "diagram",
    "introspect",
    "os",
    "cv",
    "ui",
    "git",
    "schema",
    "canvas",
    "security",
    "benchmark",
    "bridge",
    "browser",
    "compat",
    "cli",
    "usage",
    "audit",
    "events",
    "media",
    "notification",
    "clew",
    "notebook",
    "linter",
    "PATHS",
    "__version__",
]

# EOF
