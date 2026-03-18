#!/usr/bin/env python3
"""Quick test to check specific notebook cell"""

import json
from pathlib import Path

notebook_path = Path("./examples/01_scitex_io.ipynb")

with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Find cell 9 (index 8)
if len(nb['cells']) > 8:
    cell = nb['cells'][8]
    print(f"Cell type: {cell.get('cell_type')}")
    print(f"Cell content:")
    print("-" * 60)
    source = cell.get('source', [])
    if isinstance(source, list):
        print(''.join(source))
    else:
        print(source)
    print("-" * 60)
