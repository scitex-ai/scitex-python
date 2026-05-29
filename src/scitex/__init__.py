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

# All re-export machinery lives in one place: `scitex.re_export`. It owns the
# lazy proxies, the curated external map, the eager lazy pre-registration, and
# the registry-driven alias finder so `import scitex.<short>` resolves to the
# peer standalone (`scitex_<short>` or a branded peer like `figrecipe`) when no
# in-tree `scitex/<short>/` directory exists. The umbrella ships NO duplicate
# impl — peers are the single source of truth (see re_export.py for the full
# contract).
from .re_export import (
    _CallableModuleWrapper,
    _LazyModule,
)
from .re_export import (
    install_alias_finder as _install_alias_finder,
)
from .re_export import (
    register_external_lazy_modules as _register_external_lazy_modules,
)

_install_alias_finder(__path__)

# Version
from .__version__ import __version__

# BACKWARD COMPATIBILITY: Deprecated items accessible via __getattr__
# These are handled at the end of this file after lazy modules are defined
_DEPRECATED_ATTRS = {"INJECTED", "show_install_guide", "Diagram"}


# Eagerly (but lazily) pre-register every external standalone in sys.modules.
# All machinery — the `_LazyModule` / `_CallableModuleWrapper` proxies and the
# `EXTERNAL_REEXPORTS` map — lives in `scitex.re_export` (imported above).
_register_external_lazy_modules()

# Deprecated module aliases. All four (`ml`, `verify`, `reproduce`, `rng`)
# are handled by tiny shim directories at `src/scitex/{ml,verify,reproduce,
# rng}/__init__.py` so:
#   1. `import scitex.<alias>` keeps working (Python finds the dir).
#   2. The DeprecationWarning fires only when the deprecated path is
#      actually used (not on every `import scitex`).
#   3. We avoid eager in-tree imports here — those can trigger circular
#      imports when the canonical leaf transitively reaches back into the
#      umbrella (`scitex.plt`, `scitex.config`, etc.).
# See also `__getattr__` below — that catches `getattr(scitex, "ml")` too.


# Create lazy modules
io = _LazyModule("io", external="scitex_io")
gen = _LazyModule("gen", external="scitex_gen")
plt = _LazyModule("plt")
ml = _LazyModule("ml", external="scitex_ml")
genai = _LazyModule("genai", external="scitex_genai")
pd = _LazyModule("pd", external="scitex_pd")
str = _LazyModule("str", external="scitex_str")
stats = _LazyModule("stats")
path = _LazyModule("path", external="scitex_path")
dict = _LazyModule("dict", external="scitex_dict")
decorators = _LazyModule("decorators", external="scitex_decorators")
dsp = _LazyModule("dsp", external="scitex_dsp")
nn = _LazyModule("nn", external="scitex_nn")
torch = _LazyModule("torch")
web = _LazyModule("web", external="scitex_web")
db = _LazyModule("db", external="scitex_db")
repro = _LazyModule("repro", external="scitex_repro")
scholar = _LazyModule("scholar", external="scitex_scholar")
writer = _LazyModule("writer", external="scitex_writer")
fig = _LazyModule("fig")
resource = _LazyModule("resource", external="scitex_resource")
tex = _LazyModule("tex", external="scitex_tex")
linalg = _LazyModule("linalg", external="scitex_linalg")
parallel = _LazyModule("parallel", external="scitex_parallel")
datetime = _LazyModule("datetime", external="scitex_datetime")
dt = datetime  # Shorter alias — same lazy-loaded module instance.
types = _LazyModule("types", external="scitex_types")
utils = _LazyModule("utils")
etc = _LazyModule("etc", external="scitex_etc")
context = _LazyModule("context", external="scitex_context")
dev = _LazyModule("dev", external="scitex_dev")
gists = _LazyModule("gists", external="scitex_gists")
errors = _LazyModule("errors")
logging = _LazyModule("logging", external="scitex_logging")
session = _CallableModuleWrapper("session", main_decorator_name="session")
session._setup_persistence("scitex", "session")
module = _CallableModuleWrapper("module", main_decorator_name="module")
module._setup_persistence("scitex", "module")
capture = _LazyModule("capture", external="scitex_capture")
template = _LazyModule("template", external="scitex_template")
cloud = _LazyModule("cloud")
tunnel = _LazyModule("tunnel")
config = _LazyModule("config", external="scitex_config")
audio = _LazyModule("audio", external="scitex_audio")
msword = _LazyModule("msword", external="scitex_msword")
fts = _LazyModule("fts")  # Bundle schemas module
social = _LazyModule("social")  # Social media integration (socialia wrapper)
diagram = _LazyModule("diagram")  # Diagram creation (delegates to figrecipe)
introspect = _LazyModule(
    "introspect", external="scitex_introspect"
)  # Python introspection utilities
sh = _LazyModule("sh", external="scitex_sh")  # Shell command execution
os = _LazyModule("os", external="scitex_os")  # OS utilities (file operations)
cv = _LazyModule("cv", external="scitex_cv")  # Computer vision utilities
ui = _LazyModule("ui", external="scitex_ui")  # User interface utilities
notification = _LazyModule("notification", external="scitex_notification")  # Multi-backend notifications (scitex-notification)
notify = notification  # Backward compat alias
git = _LazyModule("git", external="scitex_git")  # Git operations
schema = _LazyModule("schema")  # Data schema utilities
canvas = _LazyModule("canvas")  # Canvas utilities for figure composition
security = _LazyModule("security", external="scitex_security")  # Security utilities
benchmark = _LazyModule(
    "benchmark", external="scitex_benchmark"
)  # Benchmarking utilities
bridge = _LazyModule("bridge", external="scitex_bridge")  # Bridge utilities
browser = _LazyModule("browser", external="scitex_browser")  # Browser automation
compat = _LazyModule("compat", external="scitex_compat")  # Compatibility utilities
audit = _LazyModule("audit", external="scitex_audit")  # Security auditing
events = _LazyModule("events", external="scitex_events")  # Event system
media = _LazyModule("media")  # Media utilities
cli = _LazyModule("cli")  # Command-line interface
linter = _LazyModule("linter", external="scitex_linter")  # AST-based linter (delegates to scitex-linter)
clew = _LazyModule("clew")  # Hash-based verification (Ariadne's thread)
notebook = _LazyModule(
    "notebook", external="scitex_notebook"
)  # Jupyter notebook verification & compilation
app = _LazyModule(
    "app", external="scitex_app"
)  # App SDK — unified file storage for local + cloud
usage = _CallableModuleWrapper("usage", main_decorator_name="show")
usage._setup_persistence("scitex", "usage")


# Deprecated module aliases — kept accessible via __getattr__ so the directory
# can be deleted. Each access emits a DeprecationWarning and returns the
# canonical lazy module.
_DEPRECATED_MODULE_ALIASES = {
    "ai": "ml",  # scitex.ai split into scitex.ml + scitex.genai
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

__all__ = [
    # Core modules
    "io",
    "gen",
    "plt",
    "ml",
    "genai",
    "pd",
    "str",
    "stats",
    "path",
    "dict",
    "decorators",
    "sh",
    "errors",
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
