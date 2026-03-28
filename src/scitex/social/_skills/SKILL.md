---
name: stx.social
description: Unified social media management for Twitter/X, LinkedIn, Reddit, YouTube, and Google Analytics.
---

# stx.social

The `stx.social` module provides a unified interface for social media operations. It wraps the `socialia` package with SciTeX branding and `SCITEX_SOCIAL_*` environment variable prefixes.

## Python API

```python
import scitex as stx

# Twitter/X
x = stx.social.Twitter()
x.post("Excited to share our new paper on EEG classification!")
analytics = x.get_analytics()

# LinkedIn
linkedin = stx.social.LinkedIn()
linkedin.post("Research update: our model achieves SOTA on BCI benchmarks", visibility="public")

# Reddit
reddit = stx.social.Reddit()
reddit.post(subreddit="MachineLearning", title="Our Paper", body="...")

# YouTube analytics
yt = stx.social.YouTube()
stats = yt.get_channel_stats()
video_stats = yt.get_video_stats("video_id")

# Google Analytics
ga = stx.social.GoogleAnalytics()
report = ga.get_report(start_date="7daysAgo", end_date="today")
```

## Key Features

- `Twitter()` / `LinkedIn()` / `Reddit()` — social media posting clients
- `YouTube()` — YouTube channel and video analytics
- `GoogleAnalytics()` — web analytics reporting
- Credentials use `SCITEX_SOCIAL_*` env var prefix (falls back to `SOCIALIA_*`)
- Thin wrapper over `socialia` package with scitex branding
