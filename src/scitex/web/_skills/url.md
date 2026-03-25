---
description: Extract and summarize web page content with summarize_url(), crawl pages with crawl_url() and crawl_to_json(), and collect all hyperlinks with get_urls().
---

# URL Utilities

## summarize_url

Fetch a URL and return a concise text summary of the main content.

```python
summarize_url(url: str, max_length: int = 500) -> str
```

```python
import scitex as stx

summary = stx.web.summarize_url("https://arxiv.org/abs/2301.12345")
print(summary)
```

---

## crawl_url

Fetch the full main text content of a page.

```python
crawl_url(url: str) -> str
```

```python
import scitex as stx

content = stx.web.crawl_url("https://example.com/article")
print(content[:500])
```

---

## crawl_to_json

Fetch a page and return structured content as a dict.

```python
crawl_to_json(url: str) -> dict
```

```python
import scitex as stx

data = stx.web.crawl_to_json("https://example.com/article")
# Returns: {'title': ..., 'content': ..., 'links': [...], 'url': ...}
```

---

## get_urls

Extract all hyperlinks from a web page.

```python
get_urls(url: str) -> list[str]
```

```python
import scitex as stx

links = stx.web.get_urls("https://example.com")
print(links[:5])
```
