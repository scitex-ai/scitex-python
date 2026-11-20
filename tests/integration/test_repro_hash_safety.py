"""Hashing a data file must not execute its serialized objects."""

import hashlib

import numpy as np
from click.testing import CliRunner

from scitex.cli.repro import repro


class _OwnedPickleProbe:
    def __init__(self, marker):
        self.marker = marker

    def __reduce__(self):
        expression = f"__import__('pathlib').Path({str(self.marker)!r}).write_text('owned-probe')"
        return eval, (expression,)


def test_array_hash_refuses_pickle_objects_without_executing_them(tmp_path):
    # Arrange
    marker = tmp_path / "must-not-exist"
    data = tmp_path / "objects.npy"
    np.save(
        data, np.array([_OwnedPickleProbe(marker)], dtype=object), allow_pickle=True
    )
    # Act
    result = CliRunner().invoke(repro, ["hash", str(data)])
    # Assert
    assert (result.exit_code != 0, marker.exists()) == (True, False)


def test_raw_hash_can_fingerprint_pickle_file_without_loading_it(tmp_path):
    # Arrange
    marker = tmp_path / "must-not-exist"
    data = tmp_path / "objects.npy"
    np.save(
        data, np.array([_OwnedPickleProbe(marker)], dtype=object), allow_pickle=True
    )
    expected = hashlib.sha256(data.read_bytes()).hexdigest()
    # Act
    result = CliRunner().invoke(repro, ["hash", str(data), "--raw"])
    # Assert
    assert (result.exit_code, result.stdout.strip(), marker.exists()) == (
        0,
        f"{expected}  objects.npy",
        False,
    )


def test_numeric_array_hash_preserves_the_public_provider_contract(tmp_path):
    # Arrange
    from scitex_repro import hash_array

    array = np.arange(12, dtype=np.int64).reshape(3, 4)
    data = tmp_path / "numeric.npy"
    np.save(data, array, allow_pickle=False)
    expected = hash_array(array)
    # Act
    result = CliRunner().invoke(repro, ["hash", str(data)])
    # Assert
    assert (result.exit_code, result.stdout.strip()) == (0, f"{expected}  numeric.npy")


def test_numeric_checkpoint_hash_preserves_tensor_bytes(tmp_path):
    # Arrange
    import torch

    tensor = torch.tensor([1.0, 2.0, 3.0])
    data = tmp_path / "tensor.pt"
    torch.save(tensor, data)
    expected = hashlib.sha256(tensor.numpy().tobytes()).hexdigest()
    # Act
    result = CliRunner().invoke(repro, ["hash", str(data)])
    # Assert
    assert (result.exit_code, result.stdout.strip()) == (0, f"{expected}  tensor.pt")
