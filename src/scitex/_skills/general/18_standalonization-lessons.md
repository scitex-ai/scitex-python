---
description: Lessons learned from splitting scitex-scholar / scitex-browser out of the scitex monolith. Applies to any future standalonization.
---

# SciTeX Standalonization Lessons

Lessons from the April 2026 scitex-scholar + scitex-browser decoupling.

## 1. Audit reverse-direction imports

When splitting a child package out of the monolith, the obvious direction
(monolith → child) is usually clean. The danger is the **reverse**: the
child's standalone repo still has `from scitex.parent.x import Y` or even
`from scitex_child` inside the *parent* repo. Both make the decoupling
a lie — the child doesn't stand alone.

```bash
# From the child repo:
grep -rn "from scitex[._ ]" src --include="*.py" | grep -v "scitex_child"

# From the parent / sibling repos:
grep -rn "scitex_child" src --include="*.py"
```

Both directions must be clean before claiming loose coupling. Add a
regression test in the child's test suite that reads its own source and
asserts the parent's namespace does not appear.

## 2. `try: from .x import Y\nexcept ImportError: Y = None` is almost always wrong

Either `x` is a required dep — make it a direct import and let the
failure propagate; or `x` is a genuine optional extra — declare it in
`[project.optional-dependencies]` and use a clear gate:

```python
try:
    import scitex_clew as _clew
except ImportError:
    _clew = None
if _clew is not None:
    _clew.hash_file(path)   # real use, real failure surface
```

Silent `X = None` downgrades produce confusing `AttributeError` at
call-time and hide dep problems.

## 3. `scitex[session]` is the minimal monolith dep

`@stx.session` lives in `scitex-python` itself (not `scitex-core`). If a
standalone package only needs the session decorator, depend on
`"scitex[session]>=2.0.0"` — not `"scitex>=2.0.0"`. Same pattern for
`scitex[sh]`, `scitex[social]`, etc. See
`~/proj/scitex-python/pyproject.toml` for the canonical extras list.

## 4. `scitex-logging` is its own package — prefer direct

```python
# NO  — pulls the monolith transitively:
from scitex.logging import getLogger
from scitex import logging

# YES — standalone:
from scitex_logging import getLogger
import scitex_logging as logging
```

Exports: `getLogger`, `ScholarError`, `AuthenticationError`, and all
other SciTeX error types. Zero heavy deps.

## 5. Path injection beats path coupling

Child packages should not import the parent's config to find their own
cache/data dirs. Inject the path as a constructor arg:

```python
# scitex-browser BEFORE (reaches into scitex-scholar):
class ChromeProfileManager:
    def __init__(self, profile_name, config=None):
        self.config = config or ScholarConfig()           # bad
        self.profile_dir = self.config.get_cache_chrome_dir(profile_name)

# AFTER (pure path injection):
class ChromeProfileManager:
    def __init__(self, profile_name, chrome_cache_dir=None):
        self.profile_dir = Path(chrome_cache_dir or _DEFAULT) / profile_name
```

Callers in the upstream package pass the resolved path explicitly. A
back-compat duck-typed `config` kwarg can bridge the transition without
reintroducing the import.

## 6. Never hardcode `~/.scitex/<pkg>/...` — always `PathManager`

```python
# NO
screenshot_dir = Path.home() / ".scitex/scholar/workspace/screenshots"

# YES
screenshot_dir = (
    ScholarConfig().path_manager.get_cache_engine_dir() / "workspace" / "screenshots"
)
```

Hardcoded paths break when users set `SCITEX_DIR`.

## 7. Record failure outcomes in metadata, not just logs

Long-running pipelines (download, enrichment) should populate metadata
fields like `access.pdf_download_{attempted_at,status,error}` on *every*
terminal branch — success, no-URLs, auth-failed, download-failed. A
project symlink to a paper without a PDF must be self-describing;
otherwise consumers can't tell "paywalled" from "not yet attempted".

## 8. "Pipeline Successful: N" ≠ "N papers got PDFs"

Report the actual artifact count, not the workflow-completed count.
`Successful: 10 / Failed: 0` with zero PDFs downloaded is a false
positive that masks the real problem.

## 9. One worker against a single publisher

Publisher bot detection (Cloudflare, OpenAthens SSO) triggers on
concurrent requests to the same host. Four parallel workers hitting
`academic.oup.com` at once reliably trips Cloudflare; one worker at a
time succeeds. A per-host rate limiter is the right abstraction; until
that exists, default `--num-workers 1` for paywalled publishers.

## 10. Xvfb auto-start must handle timeout, not only nonzero exit

`xdpyinfo` can hang against a missing display rather than returning
non-zero. Verifier code like

```python
if subprocess.run([...], timeout=5).returncode == 0: ok
else: start_xvfb()
```

misses the timeout path entirely (the `except TimeoutExpired` branch
returns False without starting anything). Always take the start-Xvfb
branch on any failure mode, with a recursion guard.

## 11. wait_redirects success needs a semantic check, not just "settled"

OpenAthens SSO redirect chains can take 25–35s — longer than most
"wait for navigation to settle" timeouts. If the timeout fires but the
page URL has left the origin resolver (`sfxlcl`, `exlibrisgroup`),
that IS success. Strict `success = not timed_out AND ...` discards
valid resolutions and forces the caller to fall back to the original
OpenURL, producing "Found 0 PDF URLs" on pages that have no PDFs.

## 12. Dead tests at collection break CI

After splitting a package, `pytest` collects ALL test files — including
ones that import modules that were removed. They fail at collection,
not at assertion, so they pollute failure counts. Delete or move them;
don't leave them hoping someone re-adds the module.
