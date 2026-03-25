---
name: social-config
description: Check socialia availability, inspect PLATFORM_STRATEGIES, and configure SCITEX_SOCIAL_ environment variables.
---

# Social Configuration

## Environment Variables

All credentials use the `SCITEX_SOCIAL_` prefix (falls back to `SOCIALIA_` prefix if the scitex prefix is absent).

| Variable | Platform |
|----------|---------|
| `SCITEX_SOCIAL_X_CONSUMER_KEY` | Twitter/X |
| `SCITEX_SOCIAL_X_CONSUMER_KEY_SECRET` | Twitter/X |
| `SCITEX_SOCIAL_X_ACCESS_TOKEN` | Twitter/X |
| `SCITEX_SOCIAL_X_ACCESS_TOKEN_SECRET` | Twitter/X |
| `SCITEX_SOCIAL_X_BEARER_TOKEN` | Twitter/X (read-only) |
| `SCITEX_SOCIAL_LINKEDIN_CLIENT_ID` | LinkedIn |
| `SCITEX_SOCIAL_LINKEDIN_CLIENT_SECRET` | LinkedIn |
| `SCITEX_SOCIAL_LINKEDIN_ACCESS_TOKEN` | LinkedIn |
| `SCITEX_SOCIAL_REDDIT_CLIENT_ID` | Reddit |
| `SCITEX_SOCIAL_REDDIT_CLIENT_SECRET` | Reddit |
| `SCITEX_SOCIAL_YOUTUBE_API_KEY` | YouTube |
| `SCITEX_SOCIAL_GOOGLE_ANALYTICS_PROPERTY_ID` | Google Analytics |

---

## has_socialia

Check if the `socialia` package is installed before attempting to use any platform client.

```python
import scitex as stx

if stx.social.has_socialia():
    x = stx.social.Twitter()
    x.post("Hello!")
else:
    print("Install socialia: pip install socialia")
```

---

## PLATFORM_STRATEGIES

String describing recommended content strategies for each platform (used by MCP tools).

```python
import scitex as stx

print(stx.social.PLATFORM_STRATEGIES)
```
