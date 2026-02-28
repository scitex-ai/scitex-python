# Environment Configuration Examples

Modular environment configuration files for SciTeX and its family of packages.

## SciTeX Family

SciTeX integrates standalone packages that can be used independently:

```
scitex (umbrella)
├── scitex.plt      ← figrecipe + matplotlib + local features
├── scitex.scholar  ← crossref-local + local features
├── scitex.social   ← socialia (thin wrapper)
└── scitex.writer   ← scitex-writer (thin wrapper)
```

| Package | scitex Module | Integration |
|---------|---------------|-------------|
| [figrecipe](https://github.com/ywatanabe1989/figrecipe) | `scitex.plt` | Enhanced |
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `scitex.scholar` | Enhanced |
| [socialia](https://github.com/ywatanabe1989/socialia) | `scitex.social` | Thin |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer) | `scitex.writer` | Thin |

## Structure

```
.env.d.examples/
├── entry.src              # Single entry point (source this)
│
├── # Standalone packages (00_*)
├── 00_scitex.env          # SciTeX base (SCITEX_DIR)
├── 00_crossref-local.env  # CrossRef Local database
├── 00_figrecipe.env       # FigRecipe plotting
├── 00_socialia.env        # Socialia social media package
├── 00_scitex-writer.env   # SciTeX Writer manuscript tools
│
├── # MCP server (02_*)
├── 02_mcp.env             # MCP tool toggles (SCITEX_MCP_USE_*)
│
└── # Modules (01_*) - maps to scitex.{module}
├── 01_audio.env           # scitex.audio - TTS relay
├── 01_cloud.env           # scitex.cloud - Django backend
├── 01_config.env          # scitex.config - Cache settings
├── 01_logging.env         # scitex.logging - Log level, format
├── 01_plt.env             # scitex.plt - Matplotlib plotting
├── 01_scholar.env         # scitex.scholar - Literature management
├── 01_social.env          # scitex.social - Social media APIs
├── 01_ui.env              # scitex.ui - Notifications
└── 01_web.env             # scitex.web - Downloads
```

## Naming Convention

- `00_*` - Standalone packages (loaded first)
- `01_*` - SciTeX modules matching `scitex.{module}` (loaded after)
- `02_*` - MCP server configuration (tool toggles)

## Quick Start

```bash
# 1. Copy examples to .env.d/
cp -r .env.d.examples .env.d

# 2. Edit files with your values
$EDITOR .env.d/

# 3. Source in your shell
source .env.d/entry.src
```

## Usage Options

### Option 1: Source entry.src (Recommended)

The entry point sources all .env files in order:

```bash
# In your shell config (~/.bashrc, ~/.zshrc)
source /path/to/project/.env.d/entry.src

# Or set for MCP server config
export SCITEX_ENV_SRC=/path/to/.env.d/entry.src
```

### Option 2: Merge into single .env

```bash
cat .env.d.examples/*.env > .env
# Edit .env with your values
```

### Option 3: Copy specific modules only

```bash
# Copy only what you need
cat .env.d.examples/00_scitex.env > .env
cat .env.d.examples/01_audio.env >> .env
```

## Module Reference

### Standalone Packages (00_*)

| File | Package | Key Variables |
|------|---------|---------------|
| `00_scitex.env` | scitex | `SCITEX_DIR` |
| `00_crossref-local.env` | crossref-local | `CROSSREF_LOCAL_MODE`, `CROSSREF_LOCAL_API_URL` |
| `00_figrecipe.env` | figrecipe | `FIGRECIPE_OUTPUT_FORMAT`, `FIGRECIPE_DPI` |
| `00_socialia.env` | socialia | `SOCIALIA_BRAND`, `SOCIALIA_ENV_PREFIX` |
| `00_scitex-writer.env` | scitex-writer | `SCITEX_WRITER_BRAND`, `SCITEX_WRITER_LATEX_ENGINE` |

### SciTeX Modules (01_*)

| File | Module | Key Variables |
|------|--------|---------------|
| `01_audio.env` | scitex.audio | `SCITEX_AUDIO_MODE`, `SCITEX_AUDIO_ELEVENLABS_API_KEY` |
| `01_cloud.env` | scitex.cloud | `SCITEX_CLOUD_*` (workspace, auth, database) |
| `01_config.env` | scitex.config | `SCITEX_CACHE_*` (norm, dirs) |
| `01_logging.env` | scitex.logging | `SCITEX_LOGGING_LEVEL`, `SCITEX_LOGGING_FORMAT` |
| `01_plt.env` | scitex.plt | `SCITEX_PLT_STYLE`, `SCITEX_PLT_COLORS` |
| `01_scholar.env` | scitex.scholar | OpenAthens, ZenRows, 2Captcha, Zotero, alerts |
| `01_social.env` | scitex.social | X/Twitter, LinkedIn, Google Analytics, YouTube |
| `01_ui.env` | scitex.ui | Backends, email accounts, SMTP, webhooks |
| `01_web.env` | scitex.web | `SCITEX_WEB_DOWNLOADS_DIR` |

### MCP Server (02_*)

| File | Purpose | Key Variables |
|------|---------|---------------|
| `02_mcp.env` | Tool group toggles | `SCITEX_MCP_USE_PLT`, `SCITEX_MCP_USE_SCHOLAR`, ... |

Set `SCITEX_MCP_USE_<GROUP>=0` to disable a tool group from the MCP server.
All groups are enabled by default. This does not affect Python imports or CLI.

## Port Scheme

SciTeX uses `3129X` (sa-i-te-ku-su = 3-1-2-9):

| Port | Service | Direction |
|------|---------|-----------|
| 31290 | scitex-cloud | Django backend |
| 31291 | crossref-local | NAS → Local (SSH tunnel) |
| 31292 | openalex | Reserved |
| 31293 | scitex-audio | Local → NAS (relay) |

## Network Architecture

### Audio Relay (Local has speakers → NAS uses relay)

```bash
# On NAS (sender): set relay URL to local machine
SCITEX_AUDIO_MODE=remote
SCITEX_AUDIO_RELAY_URL=http://localhost:31293

# On local machine: start relay server
scitex audio relay start
```

### CrossRef Local (NAS has DB → Local connects via SSH)

```bash
# On local machine: connect to NAS database
CROSSREF_LOCAL_MODE=http
CROSSREF_LOCAL_API_URL=http://localhost:31291

# SSH tunnel: ssh -L 31291:localhost:31291 nas
```

## Credential Patterns

### Scholar Authentication

```bash
# OpenAthens (institutional)
SCITEX_SCHOLAR_OPENATHENS_ENABLED=true
SCITEX_SCHOLAR_OPENATHENS_EMAIL=your@university.edu

# SSO alternative
SCITEX_SCHOLAR_SSO_EMAIL=your@university.edu
```

### Social Media (via Socialia)

Socialia reads credentials from `${SOCIALIA_ENV_PREFIX}_*`:

```bash
# Set prefix
SOCIALIA_ENV_PREFIX=SCITEX_SOCIAL

# Socialia will look for:
# - SCITEX_SOCIAL_X_CONSUMER_KEY
# - SCITEX_SOCIAL_LINKEDIN_CLIENT_ID
# etc.
```

## Shell Helpers

When sourcing `.src` files (not `.env`), you get shell functions:

```bash
# Set log level dynamically
stx_set_loglevel debug    # debug, info, warning, error
stx_set_loglevel          # Show current level
```

## Deprecated Variables

The following environment variables are deprecated. They still work but will be removed in a future version:

| Deprecated | Use Instead |
|------------|-------------|
| `SCITEX_SCHOLAR_FROM_EMAIL_ADDRESS` | `SCITEX_SCHOLAR_EMAIL_NOREPLY` |
| `SCITEX_SCHOLAR_FROM_EMAIL_PASSWORD` | `SCITEX_SCHOLAR_EMAIL_PASSWORD` |
| `SCITEX_SCHOLAR_FROM_EMAIL_SMTP_SERVER` | `SCITEX_SCHOLAR_EMAIL_SMTP_SERVER` |
| `SCITEX_SCHOLAR_FROM_EMAIL_SMTP_PORT` | `SCITEX_SCHOLAR_EMAIL_SMTP_PORT` |
| `SCITEX_NOTIFY_EMAIL_TO` | `SCITEX_UI_EMAIL_NOTIFICATION_TO` |
| `SCITEX_NOTIFY_EMAIL_FROM` | `SCITEX_UI_EMAIL_NOTIFICATION_FROM` |
| `SCITEX_NOTIFY_WEBHOOK_URL` | `SCITEX_UI_WEBHOOK_URL` |
| `SCITEX_CROSSREF_EMAIL` | `SCITEX_SCHOLAR_CROSSREF_EMAIL` |
| `SCITEX_PUBMED_EMAIL` | `SCITEX_SCHOLAR_PUBMED_EMAIL` |

## Security

- Never commit `.env` or `.env.d/` to version control
- Add to `.gitignore`:
  ```
  .env
  .env.d/
  !.env.d.examples/
  ```
- Use restricted permissions: `chmod 600 .env.d/*.env`

## MCP Server Integration

For Claude Code MCP config, set the entry point:

```json
{
  "mcpServers": {
    "scitex": {
      "env": {
        "SCITEX_ENV_SRC": "/path/to/.env.d/entry.src"
      }
    }
  }
}
```

The MCP server will source this file on startup.
