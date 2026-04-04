#!/usr/bin/env python3
# Time-stamp: "2024-11-02 13:29:31 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_symlink.py

import os

from scitex.str import color_text


def symlink(tgt, src, force=False):
    """Create a symbolic link.

    This function creates a symbolic link from the target to the source.
    If the force parameter is True, it will remove any existing file at
    the source path before creating the symlink.

    Parameters
    ----------
    tgt : str
        The target path (the file or directory to be linked to).
    src : str
        The source path (where the symbolic link will be created).
    force : bool, optional
        If True, remove the existing file at the src path before creating
        the symlink (default is False).

    Returns
    -------
    None

    Raises
    ------
    OSError
        If the symlink creation fails.

    Example
    -------
    >>> symlink('/path/to/target', '/path/to/link')
    >>> symlink('/path/to/target', '/path/to/existing_file', force=True)
    """
    if force:
        try:
            os.remove(src)
        except FileNotFoundError:
            pass

    # Calculate the relative path from src to tgt
    src_dir = os.path.dirname(src)
    relative_tgt = os.path.relpath(tgt, src_dir)

    os.symlink(relative_tgt, src)
    print(color_text(f"\nSymlink was created: {src} -> {relative_tgt}\n", c="yellow"))


# EOF
