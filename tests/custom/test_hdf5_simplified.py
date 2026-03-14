#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:18:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/tests/custom/test_hdf5_simplified.py
# ----------------------------------------
import os

__FILE__ = "./tests/custom/test_hdf5_simplified.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test simplified HDF5 save/load functionality
"""

import tempfile
import time

import h5py
import numpy as np
from scitex_io._load_modules._hdf5 import _load_hdf5
from scitex_io._save_modules._hdf5 import _save_hdf5


def test_basic_save_load():
    """Test basic save and load functionality"""
    print("Testing basic save/load...")

    # Create test data
    data = {
        "array": np.random.rand(10, 20),
        "scalar": 42,
        "string": "Hello HDF5",
        "list": [1, 2, 3, 4, 5],
    }

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Save data
        _save_hdf5(data, temp_path)

        # Load data
        loaded_data = _load_hdf5(temp_path)

        # Verify
        assert "array" in loaded_data
        assert "scalar" in loaded_data
        assert "string" in loaded_data
        assert "list" in loaded_data

        np.testing.assert_array_almost_equal(loaded_data["array"], data["array"])
        assert loaded_data["scalar"] == 42
        assert loaded_data["string"] == "Hello HDF5"
        np.testing.assert_array_equal(loaded_data["list"], [1, 2, 3, 4, 5])

        print("✓ Basic save/load test passed")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_group_save_load():
    """Test saving/loading with groups"""
    print("Testing group save/load...")

    data1 = {"data": np.array([1, 2, 3])}
    data2 = {"data": np.array([4, 5, 6])}

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Save to different groups
        _save_hdf5(data1, temp_path, key="group1")
        _save_hdf5(data2, temp_path, key="group2")

        # Load entire file
        loaded_all = _load_hdf5(temp_path)

        # Verify structure
        assert "group1" in loaded_all
        assert "group2" in loaded_all
        assert "data" in loaded_all["group1"]
        assert "data" in loaded_all["group2"]

        np.testing.assert_array_equal(loaded_all["group1"]["data"], [1, 2, 3])
        np.testing.assert_array_equal(loaded_all["group2"]["data"], [4, 5, 6])

        print("✓ Group save/load test passed")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_override_behavior():
    """Test override behavior"""
    print("Testing override behavior...")

    data1 = {"value": 1}
    data2 = {"value": 2}

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Save initial data
        _save_hdf5(data1, temp_path, key="test")

        # Try to save without override (should not change)
        _save_hdf5(data2, temp_path, key="test", override=False)
        loaded = _load_hdf5(temp_path)
        assert loaded["test"]["value"] == 1

        # Save with override
        _save_hdf5(data2, temp_path, key="test", override=True)
        loaded = _load_hdf5(temp_path)
        assert loaded["test"]["value"] == 2

        print("✓ Override behavior test passed")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_performance():
    """Test performance without locking overhead"""
    print("Testing performance...")

    # Create large dataset
    large_data = {
        "array": np.random.rand(1000, 1000),
        "metadata": {"size": 1000000, "type": "random"},
    }

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Time the save operation
        start_time = time.time()
        _save_hdf5(large_data, temp_path)
        save_time = time.time() - start_time

        # Time the load operation
        start_time = time.time()
        loaded_data = _load_hdf5(temp_path)
        load_time = time.time() - start_time

        # Verify data integrity
        np.testing.assert_array_almost_equal(
            loaded_data["array"][:10, :10], large_data["array"][:10, :10]
        )

        print("✓ Performance test passed")
        print(f"  Save time: {save_time:.3f}s")
        print(f"  Load time: {load_time:.3f}s")
        print(f"  File size: {os.path.getsize(temp_path) / 1024 / 1024:.1f} MB")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_complex_data_types():
    """Test various data types"""
    print("Testing complex data types...")

    data = {
        "int8": np.int8(127),
        "float64": np.float64(3.14159),
        "bool": True,
        "complex": np.complex128(1 + 2j),
        "nested_dict": {"a": 1, "b": [2, 3, 4]},
        "unicode": "测试中文",
        "empty_array": np.array([]),
        "nan_value": np.nan,
        "inf_value": np.inf,
    }

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Save data
        _save_hdf5(data, temp_path)

        # Load data
        loaded_data = _load_hdf5(temp_path)

        # Verify different types
        assert loaded_data["int8"] == 127
        assert abs(loaded_data["float64"] - 3.14159) < 1e-10
        assert loaded_data["bool"] == True
        assert loaded_data["unicode"] == "测试中文"
        assert loaded_data["nested_dict"] == {"a": 1, "b": [2, 3, 4]}
        assert loaded_data["empty_array"].size == 0
        assert np.isnan(loaded_data["nan_value"])
        assert np.isinf(loaded_data["inf_value"])

        print("✓ Complex data types test passed")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_nested_groups():
    """Test deeply nested group structures"""
    print("Testing nested groups...")

    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
        temp_path = f.name

    try:
        # Save data in nested groups
        _save_hdf5({"data": [1, 2, 3]}, temp_path, key="level1/level2/level3")
        _save_hdf5({"info": "deep"}, temp_path, key="level1/level2/metadata")

        # Load and verify
        loaded = _load_hdf5(temp_path)

        assert "level1" in loaded
        assert "level2" in loaded["level1"]
        assert "level3" in loaded["level1"]["level2"]
        assert "metadata" in loaded["level1"]["level2"]

        np.testing.assert_array_equal(
            loaded["level1"]["level2"]["level3"]["data"], [1, 2, 3]
        )
        assert loaded["level1"]["level2"]["metadata"]["info"] == "deep"

        print("✓ Nested groups test passed")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Simplified HDF5 Implementation")
    print("=" * 50)

    try:
        test_basic_save_load()
        test_group_save_load()
        test_override_behavior()
        test_performance()
        test_complex_data_types()
        test_nested_groups()

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

# EOF
