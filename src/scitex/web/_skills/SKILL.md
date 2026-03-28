---
name: stx.web
description: Web utilities for PubMed search, URL scraping, content summarization, and image downloading.
---

# stx.web

The `stx.web` module provides web utilities for scientific use cases: searching PubMed for papers, scraping URLs for content and images, summarizing web pages, and downloading images in bulk.

## Python API

```python
import scitex as stx

# Search PubMed
papers = stx.web.search_pubmed("EEG deep learning classification", max_results=20)
metrics = stx.web.get_crossref_metrics(doi="10.1000/xyz123")

# Summarize a URL
summary = stx.web.summarize_url("https://arxiv.org/abs/2401.00000")

# Crawl URL for structured content
content = stx.web.crawl_url("https://example.com")
json_data = stx.web.crawl_to_json("https://example.com")

# Scrape URLs and images from a page
urls = stx.web.get_urls("https://example.com")
image_urls = stx.web.get_image_urls("https://example.com")

# Download images
stx.web.download_images(
    urls=image_urls,
    output_dir="./downloaded_images",
    max_workers=5
)
```

## Key Features

- `search_pubmed(query, max_results)` — search PubMed and return structured paper data
- `get_crossref_metrics(doi)` — fetch citation counts and impact metrics from CrossRef
- `summarize_url(url)` — extract and summarize main content from a URL
- `crawl_url` / `crawl_to_json` — structured web crawling
- `get_urls` / `get_image_urls` — scrape links and images from pages
- `download_images(urls, output_dir)` — bulk image download with concurrency
