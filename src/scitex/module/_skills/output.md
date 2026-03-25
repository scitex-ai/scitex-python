---
name: module-output
description: Return typed module outputs with output(), embed HTML content with html(), and render outputs for display with render_output() and render_outputs().
---

# Output System

## output

Wrap a return value with a named label for the module output system.

```python
output(data, name: str, mime_type: str | None = None) -> ModuleOutput
```

```python
from scitex_cloud.module import output
import pandas as pd

result_df = pd.DataFrame({"score": [0.92, 0.88]})
return output(result_df, "classification_results")
```

---

## html

Wrap an HTML string as a module output.

```python
html(content: str, name: str = "html") -> ModuleOutput
```

```python
from scitex_cloud.module import html

return html("<h2>Analysis complete</h2><p>See attached CSV.</p>", name="summary")
```

---

## render_output / render_outputs

Render a single `ModuleOutput` or list of them to HTML/markdown for display.

```python
render_output(out: ModuleOutput) -> str
render_outputs(outputs: list[ModuleOutput]) -> str
```

```python
from scitex_cloud.module import render_outputs

html_str = render_outputs([result_output, plot_output])
print(html_str)
```

---

## ModuleOutput / ModuleOutputCollector

`ModuleOutput`: dataclass wrapping a named result with optional MIME type.
`ModuleOutputCollector`: accumulates multiple outputs from a single module call.
