---
description: Retrieve YouTube channel statistics and Google Analytics traffic reports.
---

# Social Analytics

## YouTube

```python
import scitex as stx

yt = stx.social.YouTube()
stats = yt.get_channel_stats()
# Returns: {'subscribers': ..., 'views': ..., 'videos': ...}
```

Required env var: `SCITEX_SOCIAL_YOUTUBE_API_KEY`

---

## GoogleAnalytics

```python
import scitex as stx

ga = stx.social.GoogleAnalytics()
report = ga.get_report(start_date="7daysAgo", end_date="today")
# Returns: dict with sessions, pageviews, users
```

Required env var: `SCITEX_SOCIAL_GOOGLE_ANALYTICS_PROPERTY_ID`
