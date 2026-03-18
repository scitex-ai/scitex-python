#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:31:00 (ywatanabe)"
# File: ./scripts/test_notebook_detection.py

"""Test the new notebook detection functionality."""

import sys
import os

# Add src to path to test the new modules
sys.path.insert(0, './src')

def main():
    print("Testing Notebook Detection")
    print("=" * 60)

    # Test environment detection
    from scitex.gen._detect_environment import detect_environment, get_output_directory

    env = detect_environment()
    print(f"Detected environment: {env}")

    # Test different paths
    test_paths = [
        "data.csv",
        "./results/output.pkl",
        "../outputs/figure.png"
    ]

    print("\nPath handling for different files:")
    for path in test_paths:
        output_dir, use_temp = get_output_directory(path, env)
        print(f"  {path} -> {output_dir} (temp: {use_temp})")

    # Test notebook detection
    try:
        from scitex.gen._detect_notebook_path import get_notebook_path, get_notebook_output_dir

        notebook_path = get_notebook_path()
        print(f"\nNotebook path detection: {notebook_path}")

        if notebook_path:
            output_dir = get_notebook_output_dir(notebook_path)
            print(f"Notebook output directory: {output_dir}")
    except Exception as e:
        print(f"\nNotebook detection error: {e}")

    # Test with simulated notebook
    print("\nSimulated notebook test:")
    test_nb = "./examples/analysis.ipynb"
    from scitex.gen._detect_notebook_path import get_notebook_output_dir
    output_dir = get_notebook_output_dir(test_nb)
    print(f"  {test_nb} -> {output_dir}")

if __name__ == "__main__":
    main()

# EOF
