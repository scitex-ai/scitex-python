#!/usr/bin/env python
"""
Fix kernel death issues in 02_scitex_gen.ipynb

This script fixes:
1. Incomplete code blocks
2. Missing print statements
3. Syntax errors in exception handling
"""

import json
import re
from pathlib import Path


def fix_incomplete_blocks(source):
    """Fix incomplete if/else/try blocks."""
    lines = source.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # Fix incomplete if blocks
        if re.match(r'^\s*if\s+.*:\s*$', line) and (i + 1 >= len(lines) or not lines[i + 1].strip()):
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * (indent + 4) + 'pass  # Fixed incomplete if block')

        # Fix incomplete else blocks
        elif re.match(r'^\s*else:\s*$', line) and (i + 1 >= len(lines) or not lines[i + 1].strip()):
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * (indent + 4) + 'pass  # Fixed incomplete else block')

        # Fix incomplete except blocks
        elif re.match(r'^\s*except.*:\s*$', line) and (i + 1 >= len(lines) or not lines[i + 1].strip()):
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * (indent + 4) + 'pass  # Fixed incomplete except block')

    return '\n'.join(fixed_lines)


def fix_missing_prints(source):
    """Add missing print statements."""
    # Fix lines that have bare expressions without print
    patterns = [
        (r'^(\s*)f"([^"]+)"$', r'\1print(f"\2")'),
        (r'^(\s*)f\'([^\']+)\'$', r'\1print(f\'\2\')'),
        (r'^(\s*)"([^"]+)"$', r'\1print("\2")'),
        (r'^(\s*)\'([^\']+)\'$', r'\1print(\'\2\')'),
    ]

    for pattern, replacement in patterns:
        source = re.sub(pattern, replacement, source, flags=re.MULTILINE)

    return source


def fix_syntax_errors(source):
    """Fix common syntax errors."""
    # Fix incomplete variable references
    source = re.sub(r'Second call result: {result2}"', r'print(f"Second call result: {result2}")', source)

    # Fix incomplete f-strings
    source = re.sub(r'(\s+)([A-Za-z_][A-Za-z0-9_]*): {([^}]+)}', r'\1print(f"\2: {\3}")', source)

    return source


def fix_notebook(notebook_path):
    """Fix the notebook."""
    print(f"Fixing {notebook_path}...")

    # Read notebook
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    cells_fixed = 0

    # Process each cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = cell.get('source', '')
            if isinstance(source, list):
                source = ''.join(source)

            original = source

            # Apply fixes
            source = fix_incomplete_blocks(source)
            source = fix_missing_prints(source)
            source = fix_syntax_errors(source)

            if source != original:
                cells_fixed += 1
                cell['source'] = source.split('\n')

    # Save fixed notebook
    output_path = notebook_path.parent / f"{notebook_path.stem}_fixed.ipynb"
    with open(output_path, 'w') as f:
        json.dump(notebook, f, indent=2)

    print(f"Fixed {cells_fixed} cells")
    print(f"Saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    notebook_path = Path("02_scitex_gen.ipynb")
    if notebook_path.exists():
        fix_notebook(notebook_path)
    else:
        print(f"Notebook not found: {notebook_path}")
