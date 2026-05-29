<!-- ---
!-- Timestamp: 2025-10-09 04:18:23
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/io/README.md
!-- --- -->

# SciTeX I/O Module

Files in Windows/MacOS can be opened by licking without specifying software to open. This io module enables such experiences with automatic format detection from file extension, making standardized coding available: `stx.io.load("path/to/file.ext")` and `stx.io.save(obj, "path/to/file.ext")`

## Loading Data

The `load` function allows you to read data from various file formats. It automatically detects the file type based on the extension and uses the appropriate method to load the data.

### Supported Formats

- **Tabular Data**: `.csv`, `.tsv`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.parquet`
- **Configuration**: `.json`, `.yaml`, `.yml`
- **Serialization**: `.pkl`, `.joblib`
- **Scientific Arrays**: `.npy`, `.npz`, `.hdf5`, `.h5`, `.zarr`, `.nc` (NetCDF), `.mat` (MATLAB), `.con`
- **ML/DL Models**: `.pth`, `.pt` (PyTorch), `.cbm` (CatBoost)
- **Documents**: `.txt`, `.log`, `.md`, `.pdf`, `.docx`, `.xml`, `.bib` (BibTeX)
- **Images**: `.jpg`, `.png`, `.tiff`, `.tif`, `.gif`
- **Video**: `.mp4`
- **EEG**: `.vhdr`, `.vmrk`, `.edf`, `.bdf`, `.gdf`, `.cnt`, `.egi`, `.eeg`, `.set`
- **Database**: `.db` (SQLite3)

### Example Usage

```python
import scitex

# Load a CSV file into a pandas DataFrame
dataframe = scitex.io.load('data.csv')

# Load a JSON configuration file
config = scitex.io.load('config.json')

# Load a NumPy array from a .npy file
array = scitex.io.load('array.npy')

# Load an image file using PIL
image = scitex.io.load('image.png')

# Load a PyTorch model
model_state = scitex.io.load('model.pth')

# Load an EEG data file
eeg_data = scitex.io.load('subject1.edf')

# Load a YAML file
settings = scitex.io.load('settings.yaml')
```

## Saving Data

The `save` function lets you save various types of data to files. It determines the appropriate saving method based on the file extension you provide.

### Example Usage

```python
import scitex
import pandas as pd
import numpy as np
import torch
from PIL import Image

# Save a pandas DataFrame as a CSV file
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
scitex.io.save(df, 'output.csv')

# Save a NumPy array to a .npy file
array = np.array([1, 2, 3])
scitex.io.save(array, 'array.npy')

# Save a PyTorch model's state dictionary
model = torch.nn.Linear(10, 1)
scitex.io.save(model.state_dict(), 'model.pth')

# Save an image using PIL
image = Image.new('RGB', (100, 100), color='red')
scitex.io.save(image, 'image.png')  # Use PNG for lossless quality

# Save a dictionary as a JSON file
data = {'name': 'Alice', 'age': 30}
scitex.io.save(data, 'data.json')

# Save a text string to a .txt file
text = "Hello, World!"
scitex.io.save(text, 'hello.txt')
```

## ⚠️ File Format Best Practices for Scientific Figures

### **NEVER use JPEG for scientific figures!**

JPEG uses lossy compression that creates artifacts around text, lines, and sharp edges, making it unsuitable for scientific figures.

#### Recommended Formats:

1. **PNG (Portable Network Graphics)** ✅ BEST for raster figures
   - **Lossless compression** - no quality loss
   - Perfect for figures with text, lines, and solid colors
   - Supports transparency
   - Metadata preserved (scitex stores full metadata in PNG tEXt chunks)
   - Auto-cropping preserves quality and DPI
   ```python
   scitex.io.save(fig, 'figure.png', dpi=300, auto_crop=True)
   ```

2. **PDF (Portable Document Format)** ✅ BEST for vector graphics
   - **Vector format** - infinite zoom without quality loss
   - Required by most scientific journals
   - Smaller file size for line art
   - Metadata preserved (scitex stores metadata in PDF Subject field)
   ```python
   scitex.io.save(fig, 'figure.pdf')
   ```

3. **JPEG (Joint Photographic Experts Group)** ❌ NEVER for scientific figures
   - **Lossy compression** - creates visible artifacts
   - Degrades quality around text and lines
   - Not suitable for graphs, plots, or diagrams
   - Only use for photographs

#### Example - Publication-Ready Figure Saving:

```python
import scitex as stx

# Create publication figure
fig, ax = stx.plt.subplots(**stx.plt.presets.SCITEX_STYLE)
ax.plot(x, y, label='Data')
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude [a.u.]')
ax.legend()

# Save in publication formats (PNG + PDF)
stx.io.save(fig, 'figure1.png', dpi=300, auto_crop=True)  # Lossless raster
stx.io.save(fig, 'figure1.pdf')                           # Vector format

# DO NOT save as JPEG - it creates artifacts!
# stx.io.save(fig, 'figure1.jpg')  # ❌ WRONG - lossy compression!
```

#### Auto-Cropping Feature:

By default (`auto_crop=True`), figures are automatically cropped to content with 1mm margin:
- Removes excess whitespace
- Preserves image quality (PNG: lossless, PDF: vector)
- Preserves DPI metadata (300 DPI for publication)
- Preserves scitex metadata (version, style, dimensions, etc.)

```python
# Auto-crop is enabled by default
stx.io.save(fig, 'figure.png')  # Automatically cropped, metadata preserved
```

<summary>Advanced Usage</summary>

## Caching Data

The `cache` function provides a simple mechanism to store and retrieve Python objects using pickle files. It helps avoid recomputation by caching results.

### Example Usage

```python
from scitex

# Define variables to cache
var1 = "Hello"
var2 = 42

# Save variables to cache
var1, var2 = scitex.io.cache("my_cache_id", "var1", "var2")

# Later in your code, you can reload them
del var1, var2  # Simulate a fresh environment

# Load variables from cache
var1, var2 = scitex.io.cache("my_cache_id", "var1", "var2")

print(var1)  # Outputs: Hello
print(var2)  # Outputs: 42
```

## Working with File Patterns

The `glob` function extends the standard `glob.glob` functionality, providing natural sorting and support for curly brace expansion.

### Example Usage

```python
from scitex

# Find all .txt files in the data directory
files = scitex.io.glob('data/*.txt')
print(files)

# Use curly brace expansion to match multiple patterns
files = scitex.io.glob('data/{train,validation,test}/*.csv')
print(files)

# Parse file paths to extract variables
paths, parsed = scitex.io.glob('data/subject_{id}/session_{session}.csv', parse=True)

for path, params in zip(paths, parsed):
    print(f"File: {path}, Subject ID: {params['id']}, Session: {params['session']}")
```

## Flushing Output Streams

The `flush` function ensures that all pending write operations to `stdout` and `stderr` are completed. This can be useful when you need to make sure all outputs are written before the program continues or exits.

### Example Usage

```python
from scitex
import sys

print("This is printed to stdout.")
print("This is an error message.", file=sys.stderr)

# Flush the output streams
scitex.io.flush()
```

## Loading Configuration Files

The `load_configs` function loads YAML configuration files from the `./config` directory and merges them into a single dictionary. It also handles debug configurations if `IS_DEBUG` is set.

### Example Usage

```python
from scitex

# Load configurations (assuming YAML files are in ./config directory)
configs = scitex.io.load_configs()

# Access configuration values
db_host = configs.get('database_host')
api_key = configs.get('api_key')

# Access configuration values as DotDict
db_host = configs.database_host
api_key = configs.api_key
```

## Additional Functions

### Saving Images

You can use the `save` function to save images in various formats such as PNG, JPEG, and TIFF.

```python
from PIL import Image
import scitex

# Create or load an image
image = Image.open('input_image.png')

# Save the image in a different format
scitex.io.save(image, 'output_image.jpg')

# Save a Plotly figure
import plotly.express as px

fig = px.bar(x=['A', 'B', 'C'], y=[1, 3, 2])
scitex.io.save(fig, 'bar_chart.png')
```

## HDF5 and Zarr Exploration

The module includes specialized explorers for hierarchical data formats:

```python
from scitex.io import H5Explorer, ZarrExplorer, has_h5_key, has_zarr_key

# HDF5 exploration
with H5Explorer("data.h5") as h5:
    h5.tree()                          # Display hierarchy
    data = h5["group/dataset"]         # Access data
    attrs = h5.get_attrs("dataset")    # Get attributes

# Check for specific keys
if has_h5_key("data.h5", "experiments/run_001"):
    data = scitex.io.load("data.h5", key="experiments/run_001")

# Zarr exploration
with ZarrExplorer("data.zarr") as zarr:
    zarr.tree()
    data = zarr["array"]
```

## Advanced Caching

The module provides a sophisticated caching system for expensive I/O operations:

```python
from scitex.io import configure_cache, get_cache_info, clear_load_cache

# Configure cache settings
configure_cache(max_size_mb=500, ttl_seconds=3600)

# Load with caching (default: enabled)
data = scitex.io.load("large_file.h5", cache=True)  # First: disk read
data = scitex.io.load("large_file.h5", cache=True)  # Second: cached

# Check cache status
info = get_cache_info()
print(f"Cached items: {info['size']}, Hits: {info['hits']}")

# Clear cache when needed
clear_load_cache()
```

## Decorator-Based Caching

```python
from scitex.io import cache

@cache(cache_dir=".cache")
def expensive_computation(x):
    data = scitex.io.load("large_dataset.h5")
    return process(data, x)

# First call: computes and caches
result = expensive_computation(42)

# Subsequent calls with same args: instant from cache
result = expensive_computation(42)
```

</details>

<details>

<summary>For Developers</summary>

## Module Structure

```
scitex.io/
├── _load.py              # Universal load function
├── _save.py              # Universal save function
├── _cache.py             # Caching decorator
├── _load_cache.py        # Load caching system
├── _load_configs.py      # Config file loading
├── _glob.py              # Pattern matching
├── _reload.py            # Module reloading
├── _flush.py             # Output flushing
│   ├── _H5Explorer.py    # HDF5 exploration
│   ├── _ZarrExplorer.py  # Zarr exploration
│   ├── _bibtex.py        # BibTeX loader
│   └── ...               # Other format loaders
└── _save_modules/        # Format-specific savers
    ├── _save_bibtex.py
    ├── _save_csv.py
    └── ...
```

</details>


## See Also

- [Root README](../../../README.md) - Project overview
- [Examples](../../../examples/01_scitex_io.ipynb) - I/O tutorial notebook
- Documentation: https://scitex.readthedocs.io/io

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->
