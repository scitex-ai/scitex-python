#!/usr/bin/env python3
"""
SciTeX CLI - Repro Commands (Reproducibility)

Provides reproducibility utilities: ID generation, timestamps, hashing.
"""

import sys

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def repro(ctx, help_recursive, as_json):
    """
    Reproducibility utilities

    \b
    Commands:
      get-id         Get new unique identifier(s)
      get-timestamp  Get the current timestamp
      hash           Hash array/file for reproducibility
      seed           Set random seed across all libraries

    \b
    Examples:
      scitex repro get-id              # Get a new unique ID
      scitex repro get-timestamp       # Get the current timestamp
      scitex repro hash data.npy       # Hash array file
      scitex repro seed 42             # Set random seed
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, repro)
        else:
            click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(repro, info_name="repro", parent=fake_parent)
    click.secho("━━━ scitex repro ━━━", fg="cyan", bold=True)
    click.echo(repro.get_help(parent_ctx))
    for name in sorted(repro.list_commands(ctx) or []):
        cmd = repro.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex repro {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@repro.command("get-id")
@click.option("--length", "-l", type=int, default=8, help="ID length (default: 8)")
@click.option("--prefix", "-p", default="", help="Prefix to add to ID")
@click.option("--count", "-n", type=int, default=1, help="Number of IDs to generate")
@click.option("--json", "as_json", is_flag=True, help="Output as a JSON array")
def gen_id(length, prefix, count, as_json):
    """
    Get new unique identifier(s)

    \b
    Examples:
      scitex repro get-id
      scitex repro get-id --length 12
      scitex repro get-id --prefix exp_
      scitex repro get-id --count 5 --json
    """
    try:
        from scitex.repro import gen_ID

        ids = []
        for _ in range(count):
            id_str = gen_ID()
            if length != 8:
                id_str = id_str[:length]
            if prefix:
                id_str = f"{prefix}{id_str}"
            ids.append(id_str)
        if as_json:
            import json

            click.echo(json.dumps(ids))
        else:
            for id_str in ids:
                click.echo(id_str)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@repro.command("get-timestamp")
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["iso", "file", "compact", "human"]),
    default="iso",
    help="Timestamp format (default: iso)",
)
@click.option("--utc", is_flag=True, help="Use UTC timezone")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def gen_timestamp(fmt, utc, as_json):
    """
    Get the current timestamp

    \b
    Formats:
      iso     - ISO 8601 format (2025-01-08T12:30:45)
      file    - File-safe format (20250108_123045)
      compact - Compact format (20250108123045)
      human   - Human readable (Jan 08, 2025 12:30:45)

    \b
    Examples:
      scitex repro get-timestamp
      scitex repro get-timestamp --format file
      scitex repro get-timestamp --format human --utc --json
    """
    try:
        from datetime import datetime, timezone

        from scitex.repro import gen_timestamp as make_timestamp

        if utc:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now()

        if fmt == "iso":
            ts = now.isoformat()
        elif fmt == "file":
            ts = now.strftime("%Y%m%d_%H%M%S")
        elif fmt == "compact":
            ts = now.strftime("%Y%m%d%H%M%S")
        elif fmt == "human":
            ts = now.strftime("%b %d, %Y %H:%M:%S")
        else:
            ts = make_timestamp()

        if as_json:
            import json

            click.echo(json.dumps({"timestamp": ts, "format": fmt, "utc": utc}))
        else:
            click.echo(ts)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@repro.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--algorithm", "-a", default="sha256", help="Hash algorithm (default: sha256)"
)
@click.option("--short", "-s", is_flag=True, help="Output short hash (first 8 chars)")
def hash(file_path, algorithm, short):
    """
    Hash array or file for reproducibility verification

    \b
    Supported file types:
      .npy, .npz  - NumPy arrays
      .pt, .pth   - PyTorch tensors
      .pkl        - Pickle files
      *           - Any file (raw bytes hash)

    \b
    Examples:
      scitex repro hash data.npy
      scitex repro hash model.pt --short
      scitex repro hash weights.npz --algorithm md5
    """
    try:
        import hashlib
        from pathlib import Path

        path = Path(file_path)

        # Try to load as array first
        hash_val = None
        try:
            if path.suffix in (".npy", ".npz"):
                import numpy as np

                from scitex.repro import hash_array

                arr = np.load(path, allow_pickle=True)
                if isinstance(arr, np.lib.npyio.NpzFile):
                    # For npz, hash all arrays
                    hashes = []
                    for key in arr.files:
                        hashes.append(hash_array(arr[key]))
                    hash_val = hashlib.sha256("".join(hashes).encode()).hexdigest()
                else:
                    hash_val = hash_array(arr)
            elif path.suffix in (".pt", ".pth"):
                import torch

                data = torch.load(path, map_location="cpu")
                if isinstance(data, torch.Tensor):
                    hash_val = hashlib.sha256(data.numpy().tobytes()).hexdigest()
                else:
                    # State dict or other
                    hash_val = hashlib.sha256(str(data).encode()).hexdigest()
        except ImportError:
            pass

        # Fall back to file hash
        if hash_val is None:
            h = hashlib.new(algorithm)
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            hash_val = h.hexdigest()

        if short:
            hash_val = hash_val[:8]

        click.echo(f"{hash_val}  {path.name}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@repro.command()
@click.argument("seed", type=int)
@click.option("--verbose", "-v", is_flag=True, help="Show what was seeded")
def seed(seed, verbose):
    """
    Set random seed across all available libraries

    \b
    Affects: os, random, numpy, torch, tensorflow, jax

    \b
    Examples:
      scitex repro seed 42
      scitex repro seed 12345 --verbose
    """
    try:
        from scitex.repro import RandomStateManager

        rsm = RandomStateManager(seed=seed, verbose=verbose)

        click.secho(f"Random seed set to: {seed}", fg="green")
        if verbose:
            click.echo("Seeded libraries:")
            click.echo("  - os.environ['PYTHONHASHSEED']")
            click.echo("  - random")
            click.echo("  - numpy (if available)")
            click.echo("  - torch (if available)")
            click.echo("  - tensorflow (if available)")
            click.echo("  - jax (if available)")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


# Renamed to the noun/verb convention; old names stay as hidden aliases.
from ._deprecation import alias_renamed  # noqa: E402

alias_renamed(repro, {"gen-id": "get-id", "gen-timestamp": "get-timestamp"})


if __name__ == "__main__":
    repro()
