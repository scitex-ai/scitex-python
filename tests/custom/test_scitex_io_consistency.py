#!/usr/bin/env python3
# Timestamp: "2025-05-18 03:11:10 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/custom/test_scitex_io_consistency.py
# ----------------------------------------
import os
import shutil
import tempfile

import pytest

pytest.importorskip("zarr")
import numpy as np
import pandas as pd
import torch

"""
Tests for IO consistency across different formats in the scitex package.
This ensures that data can be saved and loaded back with the same values.
"""


def test_numpy_arrays_consistency():
    """Test saving and loading various numpy arrays consistently."""
    try:
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Import actual modules
            from scitex.io import load, save

            # Test data
            test_arrays = {
                "array_1d": np.array([1, 2, 3, 4, 5]),
                "array_2d": np.array([[1, 2, 3], [4, 5, 6]]),
                "array_3d": np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
            }

            for name, array in test_arrays.items():
                # Test .npy format
                npy_path = os.path.join(temp_dir, f"{name}.npy")
                save(array, npy_path, verbose=False)
                loaded_npy = load(npy_path)
                assert np.array_equal(array, loaded_npy)

                # Test .npz format
                npz_path = os.path.join(temp_dir, f"{name}.npz")
                save({"data": array}, npz_path, verbose=False)
                loaded_npz = load(npz_path)
                # Handling different formats that might be returned by load
                if isinstance(loaded_npz, dict):
                    assert np.array_equal(array, loaded_npz["data"])
                elif isinstance(loaded_npz, list):
                    # When loaded as list, it might be the first element
                    assert np.array_equal(array, loaded_npz[0])
    except ImportError:
        pytest.skip("Required scitex modules not available")


def test_pandas_dataframe_consistency():
    """Test saving and loading pandas DataFrames consistently."""
    try:
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Import actual modules
            from scitex.io import load, save

            # Test data
            df = pd.DataFrame(
                {"A": [1, 2, 3], "B": [4.1, 5.2, 6.3], "C": ["a", "b", "c"]}
            )

            # Test CSV format
            csv_path = os.path.join(temp_dir, "dataframe.csv")
            save(df, csv_path, verbose=False)
            loaded_csv = load(csv_path)
            # Check structure
            assert loaded_csv.shape == df.shape
            assert all(loaded_csv.columns == df.columns)

            # Test pickle format
            pkl_path = os.path.join(temp_dir, "dataframe.pkl")
            save(df, pkl_path, verbose=False)
            loaded_pkl = load(pkl_path)
            assert loaded_pkl.equals(df)
    except ImportError:
        pytest.skip("Required scitex modules not available")


@pytest.mark.xfail(
    reason="torch._has_torch_function docstring conflict in current torch version"
)
def test_pytorch_tensor_consistency():
    """Test saving and loading PyTorch tensors consistently."""
    try:
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Import actual modules
            from scitex.io import load, save

            # Test data
            tensors = {
                "tensor_1d": torch.tensor([1, 2, 3, 4, 5]),
                "tensor_2d": torch.tensor([[1, 2, 3], [4, 5, 6]]),
                "tensor_3d": torch.tensor([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
            }

            for name, tensor in tensors.items():
                # Test .pt format (PyTorch native)
                pt_path = os.path.join(temp_dir, f"{name}.pt")
                save(tensor, pt_path, verbose=False)
                loaded_pt = load(pt_path)
                assert torch.all(tensor == loaded_pt)

                # Test .pth format (PyTorch alternative extension)
                pth_path = os.path.join(temp_dir, f"{name}.pth")
                save(tensor, pth_path, verbose=False)
                loaded_pth = load(pth_path)
                assert torch.all(tensor == loaded_pth)
    except ImportError:
        pytest.skip("Required scitex modules not available")


def test_nested_structures_consistency():
    """Test saving and loading nested data structures consistently."""
    try:
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Import actual modules
            from scitex.io import load, save

            # Test data - nested dictionary with various types
            nested_data = {
                "scalars": {"int": 42, "float": 3.14, "str": "test"},
                "arrays": {"numpy": np.array([1, 2, 3]), "list": [4, 5, 6]},
                "dataframe": pd.DataFrame({"A": [1, 2], "B": [3, 4]}),
            }

            # Test pickle format for complex nested structures
            pkl_path = os.path.join(temp_dir, "nested.pkl")
            save(nested_data, pkl_path, verbose=False)
            loaded_pkl = load(pkl_path)

            # Check structure is preserved
            assert loaded_pkl["scalars"]["int"] == nested_data["scalars"]["int"]
            assert loaded_pkl["scalars"]["float"] == nested_data["scalars"]["float"]
            assert loaded_pkl["scalars"]["str"] == nested_data["scalars"]["str"]
            assert np.array_equal(
                loaded_pkl["arrays"]["numpy"], nested_data["arrays"]["numpy"]
            )
            assert loaded_pkl["arrays"]["list"] == nested_data["arrays"]["list"]
            assert loaded_pkl["dataframe"].equals(nested_data["dataframe"])

            # Test joblib format (better for large numpy arrays)
            joblib_path = os.path.join(temp_dir, "nested.joblib")
            save(nested_data, joblib_path, verbose=False)
            loaded_joblib = load(joblib_path)

            # Check structure is preserved
            assert loaded_joblib["scalars"]["int"] == nested_data["scalars"]["int"]
            assert np.array_equal(
                loaded_joblib["arrays"]["numpy"], nested_data["arrays"]["numpy"]
            )
            assert loaded_joblib["dataframe"].equals(nested_data["dataframe"])
    except ImportError:
        pytest.skip("Required scitex modules not available")


def test_scalar_handling():
    """Test saving and loading scalar values."""
    try:
        # Create test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Import actual modules
            from scitex.io import load, save
            from scitex.pd import force_df

            # Test data - scalar values
            scalar_int = 42
            scalar_float = 3.14
            scalar_str = "hello world"

            # Test scalar conversion to DataFrame
            df_int = force_df(scalar_int)
            assert isinstance(df_int, pd.DataFrame)
            assert df_int.shape == (1, 1)
            assert df_int.iloc[0, 0] == scalar_int

            df_float = force_df(scalar_float)
            assert isinstance(df_float, pd.DataFrame)
            assert df_float.shape == (1, 1)
            assert df_float.iloc[0, 0] == scalar_float

            df_str = force_df(scalar_str)
            assert isinstance(df_str, pd.DataFrame)
            assert df_str.shape == (1, 1)
            assert df_str.iloc[0, 0] == scalar_str

            # Test saving and loading scalars as pickles
            pkl_int_path = os.path.join(temp_dir, "scalar_int.pkl")
            save(scalar_int, pkl_int_path, verbose=False)
            loaded_int = load(pkl_int_path)
            assert loaded_int == scalar_int

            pkl_float_path = os.path.join(temp_dir, "scalar_float.pkl")
            save(scalar_float, pkl_float_path, verbose=False)
            loaded_float = load(pkl_float_path)
            assert loaded_float == scalar_float

            pkl_str_path = os.path.join(temp_dir, "scalar_str.pkl")
            save(scalar_str, pkl_str_path, verbose=False)
            loaded_str = load(pkl_str_path)
            assert loaded_str == scalar_str
    except ImportError:
        pytest.skip("Required scitex modules not available")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])

# EOF
