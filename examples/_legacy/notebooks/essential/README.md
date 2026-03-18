# Essential SciTeX Notebooks

This directory contains minimal, working example notebooks that demonstrate core SciTeX functionality. These notebooks are guaranteed to work and provide a quick introduction to SciTeX's main features.

## Notebooks Overview

### 1. [01_quickstart.ipynb](01_quickstart.ipynb)
**Getting Started with SciTeX**
- Basic imports and setup
- Unified I/O operations (save/load)
- Simple plotting with automatic styling
- Configuration basics

### 2. [02_io_operations.ipynb](02_io_operations.ipynb)
**Advanced I/O Features**
- Working with different file formats
- Compression and HDF5 support
- Caching decorators for performance
- Batch operations

### 3. [03_visualization.ipynb](03_visualization.ipynb)
**Publication-Ready Plotting**
- SciTeX plotting wrapper features
- Statistical visualizations
- Multi-panel figures
- Automatic CSV export from plots

### 4. [04_scholar_papers.ipynb](04_scholar_papers.ipynb)
**Managing Academic Papers**
- Searching for papers
- Managing paper collections
- Exporting to BibTeX
- PDF downloads (when available)

### 5. [05_mcp_servers.ipynb](05_mcp_servers.ipynb)
**Code Translation with MCP**
- Understanding MCP servers
- SciTeX to pure Python translation
- Translation patterns and examples
- Integration with Claude

## Running the Notebooks

Each notebook is self-contained and can be run independently:

```bash
jupyter notebook 01_quickstart.ipynb
```

Or run all notebooks in sequence:

```bash
jupyter nbconvert --execute --to notebook --inplace *.ipynb
```

## Requirements

These notebooks require:
- SciTeX installation: `pip install scitex`
- Jupyter: `pip install jupyter`
- Basic scientific Python stack (numpy, pandas, matplotlib)

## Note on Other Examples

The main `examples/notebooks/` directory contains more comprehensive examples, but many have syntax issues that are being addressed. These essential notebooks provide a reliable starting point while those issues are resolved.

## Contributing

If you'd like to add more essential examples, please ensure they:
1. Are self-contained and minimal
2. Pass syntax validation
3. Demonstrate a specific SciTeX feature clearly
4. Include explanatory markdown cells
