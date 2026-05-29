"""Sphinx configuration for SciTeX documentation."""

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
import types

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

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "SciTeX"
copyright = "2024-2026, Yusuke Watanabe"
author = "Yusuke Watanabe"

try:
    from scitex.__version__ import __version__

    release = __version__
except ImportError:
    release = "2.24.0"

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
]

# Suppress non-actionable warnings. The umbrella `__init__.py`s wildcard-
# re-export from standalone peers (e.g. `from scitex_clew import *`); when
# the standalones grow their public API (e.g. the scitex-clew==0.2.12 pin
# bump on this PR), autodoc surfaces each name once via the umbrella RST
# and again via the standalone's own RST. The duplicate descriptions are
# cosmetic (different qualnames; both render); suppress so
# `sphinx-build -W` stays usable on PRs.
suppress_warnings = [
    "autosummary",
    "autosectionlabel.*",
    "ref.python",
    "docutils",
    "image.not_readable",
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
napoleon_include_special_with_doc = True
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


def setup(app):
    """Register Sphinx event hooks for filtering private members."""
    app.connect("autodoc-skip-member", autodoc_skip_member)
    app.connect("autodoc-process-bases", autodoc_process_bases)
