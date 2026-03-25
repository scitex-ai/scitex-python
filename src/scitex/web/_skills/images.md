---
name: web-images
description: Bulk-download images from a web page with download_images() and collect all image URLs with get_image_urls().
---

# Image Downloading

## download_images

Download all images found on a web page to a local directory.

```python
download_images(url: str, output_dir: str = ".", extensions: list[str] | None = None) -> list[str]
```

Returns a list of local file paths for successfully downloaded images.

```python
import scitex as stx

saved = stx.web.download_images(
    "https://example.com/gallery",
    output_dir="./downloaded_images",
    extensions=[".png", ".jpg"],
)
print(f"Downloaded {len(saved)} images")
```

---

## get_image_urls

Collect all image URLs from a web page without downloading them.

```python
get_image_urls(url: str) -> list[str]
```

```python
import scitex as stx

img_urls = stx.web.get_image_urls("https://example.com/gallery")
print(img_urls[:3])
```
