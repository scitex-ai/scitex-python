#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:15:00 (ywatanabe)"
# File: ./scripts/prepare_notebook_env.py

"""Prepare environment for notebook execution."""

import os
from pathlib import Path

def main():
    # Create necessary directories
    dirs_to_create = [
        "./examples/io_examples",
        "./examples/io_examples_2",
        "./examples/comprehensive_io_test",
        "./examples/01_scitex_io_out",  # SciTeX might save here
    ]

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")

    # Create dummy test data file
    test_data_path = Path("./examples/comprehensive_io_test/test_data.json")
    if not test_data_path.exists():
        test_data_path.write_text('{"test": "data"}')
        print(f"✓ Created test data: {test_data_path}")

    print("\nEnvironment prepared for notebook execution!")

if __name__ == "__main__":
    main()

# EOF
