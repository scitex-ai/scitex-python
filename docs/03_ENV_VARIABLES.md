# SciTeX Environment Variables

This document describes the naming conventions and available environment variables for SciTeX.

## Naming Convention

All SciTeX environment variables follow the pattern:

```
SCITEX_{MODULE}_{SETTING}
```

Where:
- `SCITEX_` is the required prefix
- `{MODULE}` identifies the SciTeX module (e.g., `AUDIO`, `SCHOLAR`, `UI`, `LOGGING`, `PLT`)
- `{SETTING}` describes the specific configuration option

## Migration Guide (v2.15.x)

The following environment variables were renamed for consistency. Old names are still supported for backwards compatibility but are deprecated.

| Old Name | New Name | Module |
|----------|----------|--------|
| `SCITEX_LOG_FORMAT` | `SCITEX_LOGGING_FORMAT` | logging |
| `SCITEX_FORCE_COLOR` | `SCITEX_LOGGING_FORCE_COLOR` | logging |
| `SCITEX_NOTIFY_EMAIL_TO` | `SCITEX_UI_EMAIL_NOTIFICATION_TO` | ui |
| `SCITEX_NOTIFY_EMAIL_FROM` | `SCITEX_UI_EMAIL_NOTIFICATION_FROM` | ui |
| `SCITEX_NOTIFY_WEBHOOK_URL` | `SCITEX_UI_WEBHOOK_URL` | ui |
| `SCITEX_CROSSREF_EMAIL` | `SCITEX_SCHOLAR_CROSSREF_EMAIL` | scholar |
| `SCITEX_PUBMED_EMAIL` | `SCITEX_SCHOLAR_PUBMED_EMAIL` | scholar |
| `ELEVENLABS_API_KEY` | `SCITEX_AUDIO_ELEVENLABS_API_KEY` | audio |
| `SCITEX_STYLE` | `SCITEX_PLT_STYLE` | plt |
| `SCITEX_COLORS` | `SCITEX_PLT_COLORS` | plt |
| `SCITEX_X_CONSUMER_KEY` | `SCITEX_SOCIAL_X_CONSUMER_KEY` | social |
| `SCITEX_X_CONSUMER_SECRET` | `SCITEX_SOCIAL_X_CONSUMER_KEY_SECRET` | social |
| `SCITEX_X_ACCESS_TOKEN` | `SCITEX_SOCIAL_X_ACCESS_TOKEN` | social |
| `SCITEX_X_ACCESS_TOKEN_SECRET` | `SCITEX_SOCIAL_X_ACCESS_TOKEN_SECRET` | social |
| `SCITEX_LINKEDIN_ACCESS_TOKEN` | `SCITEX_SOCIAL_LINKEDIN_ACCESS_TOKEN` | social |
| `SCITEX_REDDIT_CLIENT_ID` | `SCITEX_SOCIAL_REDDIT_CLIENT_ID` | social |
| `SCITEX_REDDIT_CLIENT_SECRET` | `SCITEX_SOCIAL_REDDIT_CLIENT_SECRET` | social |
| `SCITEX_YOUTUBE_API_KEY` | `SCITEX_SOCIAL_YOUTUBE_API_KEY` | social |
| `SCITEX_GA_PROPERTY_ID` | `SCITEX_SOCIAL_GOOGLE_ANALYTICS_PROPERTY_ID` | social |
| `SCITEX_GOOGLE_CLIENT_ID` | `SCITEX_SOCIAL_GOOGLE_CLIENT_ID` | social |
| `SCITEX_GOOGLE_CLIENT_SECRET` | `SCITEX_SOCIAL_GOOGLE_CLIENT_SECRET` | social |

## Environment Variables by Module

### Core

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_DIR` | Base directory for SciTeX data | `~/.scitex` |
| `SCITEX_ENV_SRC` | Path to env source file/directory | - |

### Logging (`scitex.logging`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_LOGGING_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `SCITEX_LOGGING_FORMAT` | Log format style (minimal, default, detailed, debug, full) | `default` |
| `SCITEX_LOGGING_FORCE_COLOR` | Force colored output even when not a TTY | `false` |

### Audio (`scitex.audio`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_AUDIO_MODE` | Audio mode: local, remote, or auto | `auto` |
| `SCITEX_AUDIO_ELEVENLABS_API_KEY` | ElevenLabs API key for TTS | - |
| `SCITEX_AUDIO_RELAY_URL` | Full relay URL for remote audio | - |
| `SCITEX_AUDIO_RELAY_HOST` | Relay server host | - |
| `SCITEX_AUDIO_RELAY_PORT` | Relay server port | `31293` |
| `SCITEX_AUDIO_PORT` | Audio server port | `31293` |

### Scholar (`scitex.scholar`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_SCHOLAR_DIR` | Scholar library directory | - |
| `SCITEX_SCHOLAR_CROSSREF_EMAIL` | Email for Crossref API (polite pool) | - |
| `SCITEX_SCHOLAR_PUBMED_EMAIL` | Email for PubMed API | - |
| `SCITEX_SCHOLAR_CROSSREF_DB` | Local Crossref database path | - |
| `SCITEX_SCHOLAR_CROSSREF_API_URL` | Crossref API URL | - |
| `SCITEX_SCHOLAR_CROSSREF_MODE` | Crossref mode: local, api, or hybrid | - |
| `SCITEX_SCHOLAR_OPENATHENS_EMAIL` | OpenAthens login email | - |
| `SCITEX_SCHOLAR_OPENATHENS_ENABLED` | Enable OpenAthens authentication | `false` |
| `SCITEX_SCHOLAR_EZPROXY_URL` | EZProxy URL for institutional access | - |
| `SCITEX_SCHOLAR_OPENURL_RESOLVER_URL` | OpenURL resolver URL | - |
| `SCITEX_SCHOLAR_ZENROWS_API_KEY` | ZenRows API key for scraping | - |

### UI & Notifications (`scitex.ui`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_UI_DEFAULT_BACKEND` | Default notification backend | - |
| `SCITEX_UI_BACKEND_PRIORITY` | Notification backend priority (comma-sep) | - |
| `SCITEX_UI_INFO_BACKENDS` | Backends for info notifications | - |
| `SCITEX_UI_WARNING_BACKENDS` | Backends for warning notifications | - |
| `SCITEX_UI_ERROR_BACKENDS` | Backends for error notifications | - |
| `SCITEX_UI_CRITICAL_BACKENDS` | Backends for critical notifications | - |
| `SCITEX_UI_EMAIL_NOTIFICATION_FROM` | Email notification sender | - |
| `SCITEX_UI_EMAIL_NOTIFICATION_TO` | Email notification recipient | - |
| `SCITEX_UI_WEBHOOK_URL` | Webhook URL for notifications | - |

### Plotting (`scitex.plt`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_PLT_AXES_WIDTH_MM` | Default axes width in mm | - |
| `SCITEX_PLT_LINES_TRACE_MM` | Default line trace width in mm | - |
| `SCITEX_PLT_STYLE` | Default plot style | - |
| `SCITEX_PLT_COLORS` | Color palette to use | - |

### Social (`scitex.social`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_SOCIAL_X_CONSUMER_KEY` | Twitter/X consumer key | - |
| `SCITEX_SOCIAL_X_CONSUMER_KEY_SECRET` | Twitter/X consumer secret | - |
| `SCITEX_SOCIAL_X_ACCESS_TOKEN` | Twitter/X access token | - |
| `SCITEX_SOCIAL_X_ACCESS_TOKEN_SECRET` | Twitter/X access token secret | - |
| `SCITEX_SOCIAL_X_BEARER_TOKEN` | Twitter/X bearer token | - |
| `SCITEX_SOCIAL_LINKEDIN_CLIENT_ID` | LinkedIn client ID | - |
| `SCITEX_SOCIAL_LINKEDIN_CLIENT_SECRET` | LinkedIn client secret | - |
| `SCITEX_SOCIAL_LINKEDIN_ACCESS_TOKEN` | LinkedIn access token | - |
| `SCITEX_SOCIAL_REDDIT_CLIENT_ID` | Reddit client ID | - |
| `SCITEX_SOCIAL_REDDIT_CLIENT_SECRET` | Reddit client secret | - |
| `SCITEX_SOCIAL_YOUTUBE_API_KEY` | YouTube API key | - |
| `SCITEX_SOCIAL_YOUTUBE_CLIENT_SECRETS_FILE` | YouTube client secrets file | - |
| `SCITEX_SOCIAL_GOOGLE_ANALYTICS_PROPERTY_ID` | Google Analytics property ID | - |
| `SCITEX_SOCIAL_GOOGLE_ANALYTICS_MEASUREMENT_ID` | Google Analytics measurement ID | - |
| `SCITEX_SOCIAL_GOOGLE_ANALYTICS_API_SECRET` | Google Analytics API secret | - |
| `SCITEX_SOCIAL_GOOGLE_APPLICATION_CREDENTIALS` | Google service account credentials | - |
| `SCITEX_SOCIAL_GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `SCITEX_SOCIAL_GOOGLE_CLIENT_SECRET` | Google OAuth client secret | - |

### Cloud (`scitex.cloud`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_CLOUD_USERNAME` | Cloud username | - |
| `SCITEX_CLOUD_PASSWORD` | Cloud password | - |
| `SCITEX_CLOUD_CODE_WORKSPACE` | Running in cloud workspace | `false` |
| `SCITEX_CLOUD_CODE_PROJECT_ROOT` | Cloud project root | - |
| `SCITEX_CLOUD_CODE_BACKEND` | Cloud backend type | - |

### Capture (`scitex.capture`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_CAPTURE_DIR` | Screenshot capture directory | - |

### Web (`scitex.web`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_WEB_DOWNLOADS_DIR` | Web downloads directory | - |

### Dev (`scitex._dev`)

| Variable | Description | Default |
|----------|-------------|---------|
| `SCITEX_DEV_CONFIG` | Path to dev config YAML file | `~/.scitex/dev_config.yaml` |
| `SCITEX_DEV_HOSTS` | Comma-separated list of enabled host names (overrides YAML `enabled` field) | - |
| `SCITEX_DEV_GITHUB_REMOTES` | Comma-separated list of enabled GitHub remote names (overrides YAML `enabled` field) | - |
| `GITHUB_TOKEN` / `GH_TOKEN` | GitHub personal access token for API calls | - |

Notes:
- `SCITEX_DEV_CONFIG` is read by `load_config()` and `get_config_path()`.
- `SCITEX_DEV_HOSTS` and `SCITEX_DEV_GITHUB_REMOTES` selectively enable entries defined in the config file; entries not in the list are disabled.
- `GITHUB_TOKEN` / `GH_TOKEN` are standard GitHub env vars; `GH_TOKEN` is checked first.

## Generating a Template

You can generate a template `.src` file programmatically:

```python
from scitex.config import generate_template

# Generate template with all variables
template = generate_template()
print(template)

# Save to file
with open("scitex_env.src", "w") as f:
    f.write(template)
```

## See Also

- `.env.example` - Example environment file
- `src/scitex/config/_env_registry.py` - Canonical registry of all env vars
