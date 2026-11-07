"""Collecting basic I/O tests must not initialize the optional tensor backend."""

import json
import subprocess
import sys
from pathlib import Path


def test_io_module_collects_all_cases_without_importing_torch(tmp_path):
    source = (
        Path(__file__).resolve().parents[1] / "custom/test_scitex_io_consistency.py"
    )
    script = r"""
import json, runpy, sys
def guard(event, args):
    if event == "import" and args[0].split(".")[0] == "torch":
        raise AssertionError("I/O collection attempted to import Torch")
sys.addaudithook(guard)
module = runpy.run_path(sys.argv[1], run_name="owned_io_collection")
names = sorted(name for name, value in module.items()
               if name.startswith("test_") and callable(value))
print(json.dumps({"tests": names, "torch_imported": "torch" in sys.modules}))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script, str(source)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data == {
        "tests": [
            "test_nested_structures_consistency",
            "test_numpy_arrays_consistency",
            "test_pandas_dataframe_consistency",
            "test_pytorch_tensor_consistency",
            "test_scalar_handling",
        ],
        "torch_imported": False,
    }
