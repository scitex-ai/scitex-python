<!-- ---
!-- Timestamp: 2025-06-14 06:43:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-SCITEX-12-io-module.md
!-- --- -->

## `stx.io`

- `stx.io` is a module for saving/loading data

### Input/Output Operations
**!!! IMPORTANT !!!**
**DO NOT MKDIR IN PYTHON SCRITPS. `stx.io.save` MKDIR AUTOMATICALLY**
**PATH MUST BE ALWAYS RELATIVE FROM THE SCRIPT ITSELF**

### `stx.io.load_configs`
```python
# Load all YAML files from ./config as a combined, dot-accessible dictionary
CONFIG = stx.io.load_configs()

# Access configuration values
print(CONFIG.PATH.DATA)  # Access path defined in PATH.yaml

# Resolve f-strings in config
patient_id = "001"
data_path = eval(CONFIG.PATH.PATIENT_DATA)  # f"./data/patient_{patient_id}/data.csv"
```

#### `stx.io.load`
```python
# Load data with automatic format detection based on extension
data = stx.io.load('./data/results.csv')  # CSV file, using pandas
config = stx.io.load('./config/params.yaml')  # YAML file
array = stx.io.load('./data/features.npy')  # NumPy array
```

Supported File Extensions for `stx.io.load` are:

| Category | Extensions |
|----------|------------|
| **Numeric Data** | `.npy`, `.npz`, `.mat`, `.h5`, `.hdf5` |
| **Tabular Data** | `.csv`, `.xlsx`, `.xls`, `.tsv` |
| **Text & Config** | `.json`, `.yaml`, `.yml`, `.xml`, `.txt` |
| **Python Objects** | `.pkl`, `.pickle`, `.joblib` |
| **Media** | `.jpg`, `.png`, `.gif`, `.tiff`, `.pdf`, `.mp3`, `.wav` |
| **Documents** | `.docx`, `.pdf` |
| **Special** | `.db`, `.sqlite3`, `.edf` (EEG data) |

#### `stx.io.save`

Basic Usage:

``` python
# /path/to/script.py
obj = ...

# Saves to `/path/to/script_out/aab.ext`
stx.io.save(obj, "./aab.ext", symlink_from_cwd=False)

# Saves to `/path/to/script_out/aab.ext` and create symlink to `$(pwd)/aab.ext`
stx.io.save(obj, "./aab.ext", symlink_from_cwd=True)

# Saves to `/path/to/script_out/aab/bbb.ext`
stx.io.save(obj, "./aab/bbb.ext", symlink_from_cwd=False)

# Saves to `/path/to/script_out/aab/bbb.ext` and create symlink to `$(pwd)/aab/bbb.ext`
stx.io.save(obj, "./aab/bbb.ext", symlink_from_cwd=True)
```

Supported File Extensions for `stx.io.save` are:

| Category | Extensions |
|----------|------------|
| **Numeric Data** | `.npy`, `.npz`, `.mat`, `.h5`, `.hdf5` |
| **Tabular Data** | `.csv`, `.xlsx`, `.tsv` |
| **Text & Config** | `.json`, `.yaml`, `.yml`, `.txt` |
| **Python Objects** | `.pkl`, `.pickle`, `.joblib` |
| **Media** | `.jpg`, `.png`, `.gif`, `.tiff`, `.mp4`, `.html` |
| **Visualizations** | `.png`, `.jpg`, `.svg`, `.pdf`, `.html` |


Rules:
- `stx.io.save` saves data in a unified manner with respecting extension
- `stx.io.save` ensures the target directory exits
  - It calls `os.makedir("/path/to/target/directory", exists_ok=True)` internally
  - ENSURE NOT TO CREATE ANY DIRECTORY BY YOURSELF
- `stx.io.save` creates symlink
  - ALWAYS explicitly specify `symlink_from_cwd=True` or `symlink_from_cwd=False`
- Relative path MUST start from dot (e.g., `./path/to/target` or `../../path/to/target`
- By combining `stx.plt.subplots`, **PLOTTED DATA IS TRACKED AND SAVED AS CSV AS WELL AS THE IMAGE THEMSELVES**
  - Use `.jpg` for images to reduce size

#### Reversibility of `stx.io.save` and `stx.io.load`

Objects saved with `stx.io.save()` can be loaded with `stx.io.load()` while maintaining their original structure:

```python
# Save any Python object in a extension-aware manner
data = {"name": "example", "values": np.array([1, 2, 3])}
stx.io.save(data, './data/example.pkl', symlink_from_cwd=True)

# Load it back with identical structure
loaded_data = stx.io.load('./data/example.pkl')

# data and loaded_data are identical
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->
