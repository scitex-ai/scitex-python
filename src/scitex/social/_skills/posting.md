---
name: social-posting
description: Post content to Twitter/X, LinkedIn, and Reddit using platform client classes.
---

# Social Posting

## Twitter / X

```python
import scitex as stx

x = stx.social.Twitter()
x.post("New preprint out! Check results at https://arxiv.org/...")
```

Required env vars: `SCITEX_SOCIAL_X_CONSUMER_KEY`, `SCITEX_SOCIAL_X_CONSUMER_KEY_SECRET`, `SCITEX_SOCIAL_X_ACCESS_TOKEN`, `SCITEX_SOCIAL_X_ACCESS_TOKEN_SECRET`

---

## LinkedIn

```python
import scitex as stx

linkedin = stx.social.LinkedIn()
linkedin.post("Research update: our new method achieves SOTA.", visibility="public")
```

Required env vars: `SCITEX_SOCIAL_LINKEDIN_CLIENT_ID`, `SCITEX_SOCIAL_LINKEDIN_CLIENT_SECRET`, `SCITEX_SOCIAL_LINKEDIN_ACCESS_TOKEN`

---

## Reddit

```python
import scitex as stx

reddit = stx.social.Reddit()
reddit.post(
    subreddit="MachineLearning",
    title="New reproducibility tool for scientific Python",
    text="We built SciTeX to automate experiment tracking...",
)
```

Required env vars: `SCITEX_SOCIAL_REDDIT_CLIENT_ID`, `SCITEX_SOCIAL_REDDIT_CLIENT_SECRET`
