#!/usr/bin/env python
"""
Fix specific indentation error in 02_scitex_gen.ipynb
"""

import json
from pathlib import Path


def fix_cell_11_indentation(notebook_path):
    """Fix the specific indentation error in cell 11."""

    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    # Find and fix the problematic cell
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', [])
            source_text = ''.join(source) if isinstance(source, list) else source

            # Look for the problematic pattern
            if 'for name, arr in arrays.items():' in source_text and 'dim_handler = scitex.gen.DimHandler()' in source_text:
                print(f"Found problematic cell at index {i}")

                # Fix the indentation
                fixed_source = """# Create test arrays with different dimensions
array_1d = np.random.randn(100)
array_2d = np.random.randn(50, 20)
array_3d = np.random.randn(10, 8, 5)
array_4d = np.random.randn(5, 4, 3, 2)

arrays = {
    '1D': array_1d,
    '2D': array_2d,
    '3D': array_3d,
    '4D': array_4d
}

# Print array information
for name, arr in arrays.items():
    print(f"{name} array shape: {arr.shape}, size: {arr.size}")

# Use DimHandler for dimension management
dim_handler = scitex.gen.DimHandler()

# Analyze each array
for name, arr in arrays.items():
    print(f"\\nAnalyzing {name} array:")
    print(f"  Shape: {arr.shape}")
    print(f"  Dimensions: {arr.ndim}")
    print(f"  Total elements: {arr.size}")"""

                cell['source'] = fixed_source.split('\n')
                break

    # Save the fixed notebook
    with open(notebook_path, 'w') as f:
        json.dump(notebook, f, indent=2)

    print("Fixed indentation issue in 02_scitex_gen.ipynb")


if __name__ == "__main__":
    notebook_path = Path("02_scitex_gen.ipynb")
    if notebook_path.exists():
        fix_cell_11_indentation(notebook_path)
    else:
        print(f"Notebook not found: {notebook_path}")
