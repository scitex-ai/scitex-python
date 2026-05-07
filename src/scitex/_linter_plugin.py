"""Linter plugin for the `scitex` umbrella — import + structure rules.

Owns the rules that talk about scitex umbrella API (`stx.io`, `stx.plt`,
`stx.stats`, `@stx.session`, `import scitex as stx`):

- STX-I001-I007 — import hygiene (use stx.* instead of raw matplotlib /
  scipy / numpy / pandas / pickle / random / logging)
- STX-S001-S008 — structure / `@stx.session` (decorator, main guard,
  argparse, exit code, INJECTED params, CONFIG naming, magic numbers)

Registered via the `scitex_dev.linter.plugins` entry point so
`scitex-dev linter` discovers them automatically when scitex is
installed. The legacy `scitex_linter.plugins` group is also accepted
(dual-registered in pyproject.toml during the deprecation window).

These were lifted out of the `scitex-dev` engine in the per-package
rule migration so an `@stx.session` rename or a `stx.io` API change
forces a same-PR rule update — the rule + the API now live together.
"""


def get_plugin():
    """Return scitex umbrella's linter rules."""
    from scitex_dev.linter._rules._base import Rule

    # ------------------------------------------------------------------
    # I — Import hygiene
    # ------------------------------------------------------------------
    I001 = Rule(
        id="STX-I001",
        severity="warning",
        category="import",
        message="Use `stx.plt` instead of importing matplotlib.pyplot directly",
        suggestion="Replace with `stx.plt` (or `plt` injected by @stx.session).",
        requires="scitex",
    )
    I002 = Rule(
        id="STX-I002",
        severity="warning",
        category="import",
        message="Use `stx.stats` instead of importing scipy.stats directly",
        suggestion="Replace with `stx.stats` which adds effect sizes, CI, and power analysis.",
        requires="scitex",
    )
    I003 = Rule(
        id="STX-I003",
        severity="warning",
        category="import",
        message="Use `stx.io` instead of pickle for file I/O",
        suggestion="Replace with `stx.io.save(obj, 'file.pkl')` / `stx.io.load('file.pkl')`.",
        requires="scitex",
    )
    I004 = Rule(
        id="STX-I004",
        severity="warning",
        category="import",
        message="Use `stx.io` for CSV/DataFrame I/O instead of pandas I/O functions",
        suggestion="Replace `pd.read_csv()` with `stx.io.load()`, `df.to_csv()` with `stx.io.save()`.",
        requires="scitex",
    )
    I005 = Rule(
        id="STX-I005",
        severity="warning",
        category="import",
        message="Use `stx.io` for array I/O instead of numpy save/load",
        suggestion="Replace `np.save()`/`np.load()` with `stx.io.save()`/`stx.io.load()`.",
        requires="scitex",
    )
    I006 = Rule(
        id="STX-I006",
        severity="info",
        category="import",
        message="Use `rngg` (injected by @stx.session) for reproducible randomness",
        suggestion="Remove `import random` and use `rngg` from @stx.session injection.",
        requires="scitex",
    )
    I007 = Rule(
        id="STX-I007",
        severity="warning",
        category="import",
        message="Use `logger` (injected by @stx.session) instead of logging module",
        suggestion="Remove `import logging` and use `logger` from @stx.session injection.",
        requires="scitex",
    )

    # ------------------------------------------------------------------
    # S — Structure / @stx.session
    # ------------------------------------------------------------------
    S001 = Rule(
        id="STX-S001",
        severity="error",
        category="structure",
        message="Missing @stx.session or @stx.module decorator on main function",
        suggestion=(
            "Add @stx.session (for scripts) or @stx.module (for cloud modules).\n"
            "  @stx.session\n"
            "  def main(...):\n"
            "      return 0\n"
            "If this is library code (not a script), add its directory to library_dirs:\n"
            "  [tool.scitex-linter]\n"
            '  library_dirs = ["src", "tests", "apps", "config", "docs"]\n'
            "  Or: SCITEX_DEV_LINTER_NON_SCRIPT_DIRS=src,tests,apps,config,docs"
        ),
        requires="scitex",
    )
    S002 = Rule(
        id="STX-S002",
        severity="error",
        category="structure",
        message="Missing `if __name__ == '__main__'` guard",
        suggestion=(
            "Add `if __name__ == '__main__': main()` at the end of the script.\n"
            "If this is library code (not a script), add its directory to library_dirs:\n"
            "  [tool.scitex-linter]\n"
            '  library_dirs = ["src", "tests", "apps", "config", "docs"]\n'
            "  Or: SCITEX_DEV_LINTER_NON_SCRIPT_DIRS=src,tests,apps,config,docs"
        ),
    )
    S003 = Rule(
        id="STX-S003",
        severity="error",
        category="structure",
        message="argparse detected — @stx.session auto-generates CLI from function signature",
        suggestion=(
            "Remove `import argparse` and define parameters as function arguments:\n"
            "  @stx.session\n"
            "  def main(data_path: str, threshold: float = 0.5):\n"
            "      # Auto-generates: --data-path, --threshold"
        ),
        requires="scitex",
    )
    S004 = Rule(
        id="STX-S004",
        severity="warning",
        category="structure",
        message="@stx.session function should return an integer exit code",
        suggestion="Add `return 0` for success at the end of your session function.",
        requires="scitex",
    )
    S005 = Rule(
        id="STX-S005",
        severity="warning",
        category="structure",
        message="Missing `import scitex as stx`",
        suggestion="Add `import scitex as stx` to use SciTeX modules.",
        requires="scitex",
    )
    S006 = Rule(
        id="STX-S006",
        severity="warning",
        category="structure",
        message="@stx.session function missing explicit INJECTED parameters",
        suggestion=(
            "Declare auto-injected values explicitly in the function signature:\n"
            "  @stx.session\n"
            "  def main(\n"
            "      CONFIG=stx.session.INJECTED,\n"
            "      plt=stx.session.INJECTED,\n"
            "      COLORS=stx.session.INJECTED,\n"
            "      rngg=stx.session.INJECTED,\n"
            "      logger=stx.session.INJECTED,\n"
            "  ):\n"
            "      return 0"
        ),
        requires="scitex",
    )
    S007 = Rule(
        id="STX-S007",
        severity="warning",
        category="structure",
        message="load_configs() result should be assigned to an UPPER_CASE variable",
        suggestion=(
            "Use UPPER_CASE for config variables — they hold project constants:\n"
            "  CONFIG = load_configs()          # good\n"
            "  config = load_configs()          # bad — looks like a local variable"
        ),
    )
    S008 = Rule(
        id="STX-S008",
        severity="info",
        category="structure",
        message="Magic number in module scope — consider centralizing in config/",
        suggestion=(
            "Move hard-coded values to config/*.yaml and load with load_configs():\n"
            "  # config/MODEL.yaml\n"
            "  HIDDEN_DIM: 256\n"
            "  DROPOUT: 0.3\n"
            "\n"
            "  # script.py\n"
            "  CONFIG = load_configs()\n"
            "  CONFIG.MODEL.HIDDEN_DIM    # 256"
        ),
    )

    return {
        "rules": [
            I001,
            I002,
            I003,
            I004,
            I005,
            I006,
            I007,
            S001,
            S002,
            S003,
            S004,
            S005,
            S006,
            S007,
            S008,
        ],
        "call_rules": {},
        "axes_hints": {},
        "checkers": [],
    }
