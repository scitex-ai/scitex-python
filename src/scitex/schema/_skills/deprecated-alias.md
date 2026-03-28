---
description: scitex.schema is deprecated. Core schemas (FTS, Node, Encoding, Theme, Stats, BBox, SizeMM, DataInfo) are migrating to scitex.io.bundle.
---

# stx.schema — Deprecated Module

`scitex.schema` emits `DeprecationWarning` on import. Core bundle schemas have moved to `scitex.io.bundle`; plot/encoding/theme/stat/validation schemas are temporarily still defined here.

## Migration for bundle schemas

```python
# Old (triggers DeprecationWarning)
from scitex.schema import FTS, Node, Encoding, Theme, Stats, BBox, SizeMM, DataInfo

# New (preferred)
from scitex.io.bundle import FTS, Node, Encoding, Theme, Stats, BBox, SizeMM, DataInfo
```

## Schemas still defined in scitex.schema (temporary)

These have not yet been migrated and must be imported from `scitex.schema` until they move:

### Plot specs
```python
from scitex.schema import (
    PlotSpec, PlotStyle, PlotGeometry, TraceSpec, TraceStyleSpec,
    AxesLabels, AxesLimits, AxesSpecItem, DataSourceSpec,
    LegendSpec, SizeSpec, FontSpec, ThemeSpec,
    TraceType, CoordinateSpace, LegendLocation,
    BboxRatio, BboxPx,
    RenderedArtist, RenderedAxes, HitRegionEntry,
    SelectableRegion, RenderManifest,
)
```

### Encoding
```python
from scitex.schema import PlotEncoding, TraceEncoding, ChannelBinding
```

### Theme
```python
from scitex.schema import PlotTheme, ColorScheme, Typography, LineDefaults, MarkerDefaults
```

### Figure elements
```python
from scitex.schema import (
    FigureTitle, Caption, PanelLabels, PanelInfo,
    generate_caption, generate_caption_latex, generate_caption_markdown,
)
```

### Stats
```python
from scitex.schema import (
    StatResult, StatPositioning, StatStyling, Position,
    PositionMode, UnitType, SymbolStyle,
    create_stat_result,
)
```

### Validation
```python
from scitex.schema import (
    validate_figure, validate_axes, validate_plot,
    validate_stat_result, validate_color,
    ValidationError,
)
```

## Version constant

```python
from scitex.schema import SCHEMA_VERSION
# "0.2.0"
```
