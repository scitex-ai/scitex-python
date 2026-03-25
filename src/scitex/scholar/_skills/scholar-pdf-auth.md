---
name: stx.scholar — PDF Download and Authentication
---

# stx.scholar — PDF Download and Authentication

## Authentication Overview

The auth system supports institutional access via EZProxy, OpenAthens, and
Shibboleth. Credentials are cached as browser cookies at:
`~/.scitex/scholar/cache/chrome/`

```
~/.scitex/scholar/cache/chrome/
├── auth/          # Saved auth cookies
├── Profile 1/     # Manually created browser profile (recommended for auth)
└── extension/     # Programmatically created profile with extensions
```

### ScholarAuthManager

```python
from scitex.scholar.auth import ScholarAuthManager

auth = ScholarAuthManager()

# Check if currently authenticated
status = auth.check_status()

# Authenticate via OpenAthens (opens browser if interactive)
await auth.authenticate("openathens")

# Logout / clear cookies
auth.logout()
```

### Authentication providers

| Provider | Class |
|---|---|
| EZProxy | `EZProxyAuthenticator` |
| OpenAthens | `OpenAthensAuthenticator` |
| Shibboleth | `ShibbolethAuthenticator` |

### From CLI

```bash
python -m scitex.scholar.auth openathens
```

---

## PDF Download via Scholar

```python
scholar = Scholar(project="eeg_seizure")

# Download PDFs for a list of DOIs (async)
results = await scholar.download_pdfs_from_dois_async(
    dois=["10.1038/s41598-017-02626-y", "10.1002/ana.410350102"],
    max_concurrent=1,   # Sequential is safer to avoid bot detection
)
# results: {"downloaded": 2, "failed": 0, "errors": 0}

# PDFs are stored in ~/.scitex/scholar/library/MASTER/{8DIGITID}/paper.pdf
```

### Download via the full pipeline

```python
# Single paper — full pipeline: DOI resolve → URL find → download → store
paper = await scholar.process_paper_async(
    doi="10.1038/s41598-017-02626-y",
    project="eeg_seizure",
)

# From title (DOI resolved automatically)
paper = await scholar.process_paper_async(
    title="Attention Is All You Need",
    project="transformers",
)
```

Pipeline stages:
1. **Stage 0** — Resolve DOI from title (if title provided, no DOI)
2. **Stage 1** — Load existing paper from storage or create new
3. **Stage 2** — Find PDF URLs via `ScholarURLFinder`
4. **Stage 3** — Download PDF via `ScholarPDFDownloader`
5. **Stage 4** — Update project symlinks

---

## URL Finding

`ScholarURLFinder` finds the actual PDF download URL from a DOI or publisher page.
It uses Zotero translators and direct URL strategies.

```python
from scitex.scholar.url_finder import ScholarURLFinder

finder = ScholarURLFinder(config=scholar.config)

# Find PDF URLs for a DOI
urls = await finder.find_pdf_urls(doi="10.1038/s41598-017-02626-y")
# [{"url": "https://...", "type": "pdf", "source": "zotero"}, ...]
```

### Zotero translators

Translators are bundled at:
`src/scitex/scholar/url_finder/translators/`

They extract PDF download links from publisher pages (Nature, Elsevier, Springer,
PubMed Central, bioRxiv, arXiv, etc.).

---

## ScholarBrowserManager

Manages Playwright browser instances used for authentication and PDF download.

```python
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.auth import ScholarAuthManager

auth = ScholarAuthManager()
browser_mgr = ScholarBrowserManager(
    auth_manager=auth,
    chrome_profile_name="system",   # use system Chrome profile
    browser_mode="stealth",         # "stealth" | "interactive" | "manual"
)

# Get authenticated browser context
browser, context = await browser_mgr.get_authenticated_browser_and_context_async()
```

Browser modes:
- `stealth` — headless with stealth patches (default)
- `interactive` — visible browser window
- `manual` — no automation; user drives browser

### Chrome extensions used

- **Lean Library** — links to institutional access
- **Zotero Connector** — browser PDF sniffer
- **Accept all cookies** — auto-dismisses cookie banners
- **Captcha Solver** — auto-solves CAPTCHAs via 2captcha API

---

## OpenURL Resolution

OpenURL is used to generate institution-specific access URLs from DOIs.

```python
from scitex.scholar.auth.gateway import OpenURLResolver

resolver = OpenURLResolver(config=scholar.config)
resolved_urls = await resolver.resolve(doi="10.1038/s41598-017-02626-y")
# ["https://resolver.unimelb.edu.au/openurl?..."]
```

---

## ScholarPDFDownloader

Low-level PDF downloader. Used internally by `Scholar` via `PDFDownloadMixin`.

```python
from scitex.scholar.pdf_download import ScholarPDFDownloader

downloader = ScholarPDFDownloader(context=browser_context, config=scholar.config)

results = await downloader.download_from_dois(
    dois=["10.1038/xxx"],
    output_dir="/tmp/pdfs/",
    max_concurrent=1,
)
```
