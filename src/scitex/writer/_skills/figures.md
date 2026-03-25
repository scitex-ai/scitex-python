---
description: Figure management — add, list, remove, convert formats, extract PDF pages as images.
---

# Figure Management

The `figures` submodule manages image files stored under `00_shared/figures/` in the project directory.

## Module-level access

```python
import scitex as stx

stx.writer.figures.add(project_dir, key, path, caption="")
stx.writer.figures.list(project_dir)
stx.writer.figures.remove(project_dir, key)
stx.writer.figures.convert(src, dst, dpi=300)
stx.writer.figures.pdf_to_images(pdf_path, output_dir, dpi=150, fmt="png")
```

## Via Writer convenience methods

```python
from scitex.writer import Writer
writer = Writer("my_paper")

writer.add_figure("fig1", "plots/results.png", caption="Results overview.")
writer.list_figures()
writer.convert_figure("figure.pdf", "figure.png", dpi=300)
```

## figures.add

```python
figures.add(
    project_dir,    # str or Path
    key,            # str — identifier used in LaTeX \ref{fig:key}
    path,           # str or Path — source image file
    caption="",     # str — figure caption text
) -> Path
```

Copies the image to `00_shared/figures/{key}{ext}` and creates an accompanying `{key}_caption.tex` file with the caption. Returns the path to the copied image.

```python
stx.writer.figures.add(
    "my_paper",
    "fig_results",
    "out/results.png",
    caption="Group comparison. Error bars: ±SEM. *p<0.05.",
)
```

## figures.list

```python
figures.list(
    project_dir,   # str or Path
) -> list[dict]
```

Returns a list of dicts, each with `key`, `path`, and `caption` fields.

```python
figs = stx.writer.figures.list("my_paper")
for f in figs:
    print(f["key"], f["path"])
```

## figures.remove

```python
figures.remove(
    project_dir,   # str or Path
    key,           # str
) -> bool
```

Removes the image file and its caption `.tex` file from the project.

## figures.convert

```python
figures.convert(
    src,           # str or Path — source image
    dst,           # str or Path — output image (format inferred from extension)
    dpi=300,       # int — output resolution for raster formats
) -> Path
```

Converts between image formats (PDF, PNG, EPS, SVG, TIFF). Uses ImageMagick or Pillow under the hood.

```python
stx.writer.figures.convert("fig.pdf", "fig.png", dpi=600)
stx.writer.figures.convert("fig.png", "fig.eps")
```

## figures.pdf_to_images

```python
figures.pdf_to_images(
    pdf_path,      # str or Path
    output_dir,    # str or Path — where to write extracted images
    dpi=150,       # int
    fmt="png",     # str — 'png' | 'jpg' | 'tiff'
) -> list[Path]
```

Extracts each page of a PDF as a separate image file. Returns list of output paths.

```python
pages = stx.writer.figures.pdf_to_images(
    "manuscript.pdf",
    "figures/pages",
    dpi=300,
    fmt="png",
)
```

## MCP

```
writer_add_figure     project_dir=./my-paper  key=fig1  path=plots/results.png  caption="Results."
writer_list_figures   project_dir=./my-paper
writer_remove_figure  project_dir=./my-paper  key=fig1
writer_convert_figure src=figure.pdf  dst=figure.png  dpi=300
writer_pdf_to_images  pdf_path=manuscript.pdf  output_dir=./pages  dpi=150
```

## CLI

```bash
scitex writer figures list ./my-paper
scitex writer figures add ./my-paper plots/results.png --key fig1 --caption "Results."
scitex writer figures remove ./my-paper fig1
scitex writer figures convert figure.pdf figure.png --dpi 300
```
