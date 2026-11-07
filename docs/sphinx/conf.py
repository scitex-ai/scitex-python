"""Sphinx configuration for SciTeX documentation."""

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
import types
import re
import json
import importlib.metadata
import inspect
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 source builds
    import tomli as tomllib
from pathlib import Path

# Stub `mcp` / `fastmcp` BEFORE any `import scitex` so autodoc never triggers
# the broken pydantic schema generation in mcp.types.TaskMetadata. Real mcp is
# pulled in transitively via scitex-writer → fastmcp; we don't need the actual
# implementation to render docs. autodoc_mock_imports doesn't help because the
# package is installed (so it's "present").
for _name in ("mcp", "mcp.types", "mcp.server", "mcp.client", "fastmcp"):
    if _name not in sys.modules:
        _mod = types.ModuleType(_name)
        if "." not in _name:
            _mod.__path__ = []  # mark as package
        sys.modules[_name] = _mod

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))

# -- Project information -----------------------------------------------------

project = "SciTeX"
copyright = "2024-2026, Yusuke Watanabe"
author = "Yusuke Watanabe"

release = tomllib.loads((_root / "pyproject.toml").read_text())["project"]["version"]
if not isinstance(release, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", release):
    raise ValueError("Sphinx project release identity is missing or malformed")

# A public umbrella may arrive transitively through legacy peers. Its metadata
# is observed honestly, but its Root code must never substitute for Git source.
try:
    _installed_root = importlib.metadata.distribution("scitex")
except importlib.metadata.PackageNotFoundError:
    _installed_root = None
_installed_root_files = {
    Path(_installed_root.locate_file(path)).resolve()
    for path in (_installed_root.files or [])
    if path.parts and path.parts[0] == "scitex"
} if _installed_root else set()
_documented_root_origins = {}


def _check_root_origin(name, obj):
    source = (_root / "src/scitex").resolve()
    observed = {}
    root_file = inspect.getattr_static(obj, "__file__", None)
    if name == "scitex" and (
        not isinstance(root_file, str) or not Path(root_file).resolve().is_relative_to(source)
    ):
        raise RuntimeError("documented Root code came from installed umbrella instead of trusted source")
    spec = inspect.getattr_static(obj, "__spec__", None)
    code = obj.__code__ if isinstance(obj, types.FunctionType) else None
    for kind, value in (
        ("file", root_file),
        ("spec", getattr(spec, "origin", None)),
        ("code", getattr(code, "co_filename", None)),
    ):
        if not isinstance(value, str):
            continue
        path = Path(value).resolve()
        if path in _installed_root_files and not path.is_relative_to(source):
            raise RuntimeError("documented Root code came from installed umbrella instead of trusted source")
        observed[kind] = str(path)
        observed[kind + "_is_concrete"] = path.is_file()
    return observed


def _record_root_doc_origin(app, what, name, obj, options, lines):
    if name == "scitex" or name.startswith("scitex."):
        observed = _check_root_origin(name, obj)
        if what == "module":
            _documented_root_origins[name] = observed


def _finish_root_doc_origins(app, exception):
    if exception is not None:
        return
    imported = {}
    for name, obj in sys.modules.copy().items():
        if name == "scitex" or name.startswith("scitex."):
            imported[name] = _check_root_origin(name, obj)
    declared = set()
    for path in (_root / "docs/sphinx").rglob("*.rst"):
        declared.update(re.findall(r"^\.\.\s+automodule::\s+(scitex(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*$", path.read_text(), re.MULTILINE))
    print("ROOT-DOC-ORIGINS " + json.dumps({
        "source_release": release,
        "installed_umbrella_metadata_version": _installed_root.version if _installed_root else None,
        "source_module_version": getattr(sys.modules.get("scitex"), "__version__", None),
        "documented_modules": _documented_root_origins,
        "documented_unverified_origins": sorted(
            name for name, origin in _documented_root_origins.items()
            if not origin.get("file_is_concrete")
        ),
        "declared_but_not_documented": sorted(declared - _documented_root_origins.keys()),
        "imported_root_namespaces": imported,
        "mixed_installed_root_code": False,
        "scope": "source overlay static rendering; not installed Root runtime qualification",
    }, sort_keys=True))

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx_rtd_theme",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "nbsphinx",  # For including Jupyter notebooks
    # matplotlib registers the `:mpltype:` / `:rc:` roles that appear in
    # matplotlib (and figrecipe/scitex-plt) docstrings. The companion
    # `plot_directive` extension would normally provide the `.. plot::`
    # directive but it enforces strict file-existence checks on the
    # script-or-example references inside matplotlib's own docstrings —
    # those paths only exist in matplotlib's own docs tree, so loading the
    # extension here turns `Errno 2: No such file or directory` errors
    # into PR-blocking warnings. We register a no-op `plot::` directive
    # in setup() instead.
    "matplotlib.sphinxext.roles",
]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": False,
    "private-members": False,
    "exclude-members": "__weakref__,__init__,__dict__,__module__",
}

# Mock imports for packages that can't install on RTD (system deps, heavy ML, etc.)
autodoc_mock_imports = [
    # GUI frameworks (require display)
    "PyQt6",
    "PyQt5",
    "dearpygui",
    # Audio backends (require system audio)
    "pyaudio",
    "sounddevice",
    # System-level dependencies
    "cv2",  # OpenCV requires system libs
    # Heavy ML/AI packages
    "torch",
    "torchvision",
    "pytorch_pretrained_vit",
    # LLM API clients (not needed for docs)
    "openai",
    "anthropic",
    "google",
    "google.genai",
    "groq",
    # Optional heavy packages
    "umap",
    "sktime",
    "imbalanced_learn",
    "imblearn",
    "xarray",
    # Audio/browser packages
    "pyttsx3",
    "gTTS",
    "gtts",
    "pydub",
    "elevenlabs",
    "playwright",
    "mss",
    "aiohttp",
    # Cloud package
    "scitex_cloud",
    # OpenAlex (pulls awscli causing pip deadlock)
    "openalex_local",
    # MCP SDK — pydantic 2.13 incompat with currently-released mcp triggers
    # PydanticSchemaGenerationError on import; mock for autodoc.
    "mcp",
]

# Autosummary settings
autosummary_generate = True

# Napoleon settings for numpy/google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "to_claude/**"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# RTD-specific configurations
html_title = f"{project} v{release}"
html_short_title = project
html_logo = None  # Add path to logo if available
html_favicon = None  # Add path to favicon if available

# Show "Edit on GitHub" links
html_context = {
    "display_github": True,
    "github_user": "ywatanabe1989",
    "github_repo": "scitex-python",
    "github_version": "develop",
    "conf_py_path": "/docs/sphinx/",
}

# nbsphinx configuration for Jupyter notebooks
nbsphinx_execute = "never"  # Don't execute notebooks during build
nbsphinx_allow_errors = True
nbsphinx_timeout = 60

# MyST parser configuration
myst_enable_extensions = [
    "dollarmath",
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    # "linkify",  # Disabled - requires linkify-it-py package
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
}

if os.environ.get("SCITEX_DOCS_STATIC") == "1":
    intersphinx_mapping = {}  # Offline static bundle; no remote inventory fetch.


# -- Hide private/internal members from autodoc --------------------------------


def autodoc_skip_member(app, what, name, obj, skip, options):
    """Skip private members (starting with _) in all autodoc output."""
    # Skip any name starting with underscore (private/internal)
    if name.startswith("_"):
        return True
    # Also check the fully qualified name for private components
    full_name = getattr(obj, "__qualname__", "") or ""
    if any(part.startswith("_") for part in full_name.split(".")):
        return True
    return skip


def autodoc_process_bases(app, name, obj, options, bases):
    """Filter out private base classes from inheritance display."""
    return [b for b in bases if not getattr(b, "__name__", "").startswith("_")]


class _NoopPlotDirective(__import__("docutils").parsers.rst.Directive):
    """No-op replacement for matplotlib's `plot::` directive.

    Matplotlib's docstrings frequently use `.. plot:: <script_path>`. We
    don't want to evaluate those plots during docs build (they reference
    files inside matplotlib's own repo), but we DO need the directive
    registered or sphinx-build -W errors on the unknown directive.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 99
    final_argument_whitespace = True
    option_spec = {}

    def run(self):  # noqa: D401
        return []


def setup(app):
    """Register Sphinx event hooks for filtering private members."""
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("autodoc-process-bases", autodoc_process_bases)
    app.connect("autodoc-process-docstring", _record_root_doc_origin)
    app.connect("build-finished", _finish_root_doc_origins)
    app.add_directive("plot", _NoopPlotDirective)
