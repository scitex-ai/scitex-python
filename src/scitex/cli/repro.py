#!/usr/bin/env python3
"""
SciTeX CLI - Repro Commands (Reproducibility)

Provides reproducibility utilities: ID generation, timestamps, hashing.
"""

import copy
import sys

import click
from scitex_dev.ecosystem import CliHelp, Example, SpecCommand


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
      generate-id         Generate unique identifier
      generate-timestamp  Generate timestamp
      hash           Hash array/file for reproducibility
      seed           Set random seed across all libraries

    \b
    Examples:
      scitex repro generate-id              # Generate unique ID
      scitex repro generate-timestamp       # Generate timestamp
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
        if cmd is None or cmd.hidden:
            continue
        click.echo()
        click.secho(f"━━━ scitex repro {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@repro.command(
    "generate-id",
    cls=SpecCommand,
    help_spec=CliHelp(
        summary="Generate timestamped identifiers with random suffixes.",
        description=(
            "--length controls the random suffix; the timestamp is always retained.",
        ),
        examples=(
            Example(
                "{prog} --length 12 --count 5 --json",
                "Generate five identifiers as JSON.",
            ),
            Example(
                "{prog} --prefix exp_ --dry-run",
                "Preview the operation without generating identifiers.",
            ),
        ),
    ),
)
@click.option(
    "--length",
    "-l",
    type=click.IntRange(min=1),
    default=8,
    help="Random suffix length; the timestamp is retained (default: 8).",
)
@click.option("--prefix", "-p", default="", help="Prefix to add to ID")
@click.option(
    "--count",
    "-n",
    type=click.IntRange(min=1),
    default=1,
    help="Number of IDs to generate",
)
@click.option("--json", "as_json", is_flag=True, help="Return generated IDs as JSON.")
@click.option(
    "--dry-run", is_flag=True, help="Describe generation without producing IDs."
)
@click.option(
    "--yes", "-y", is_flag=True, help="Accept this non-interactive operation."
)
def gen_id(length, prefix, count, as_json, dry_run, yes):
    """
    Generate unique identifier(s)

    \b
    Examples:
      scitex repro generate-id
      scitex repro generate-id --length 12
      scitex repro generate-id --prefix exp_
      scitex repro generate-id --count 5 --json
    """
    if dry_run:
        if as_json:
            from scitex_dev import Result

            click.echo(
                Result(
                    success=True,
                    data={
                        "dry_run": True,
                        "count": count,
                        "length": length,
                        "prefix": prefix,
                    },
                ).to_json()
            )
        else:
            click.echo(
                f"Would generate {count} timestamped ID(s) with a {length}-character random suffix and prefix {prefix!r}."
            )
        return
    try:
        from scitex.repro import gen_ID

        ids = [f"{prefix}{gen_ID(N=length)}" for _ in range(count)]
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data={"ids": ids}).to_json())
        else:
            for id_str in ids:
                click.echo(id_str)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@repro.command(
    "generate-timestamp",
    cls=SpecCommand,
    help_spec=CliHelp(
        summary="Generate a timestamp in a specified format and timezone.",
        examples=(
            Example(
                "{prog} --utc --json", "Return an ISO timestamp with its UTC offset."
            ),
            Example("{prog} --format file", "Return a file-safe timestamp."),
        ),
    ),
)
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["iso", "file", "compact", "human"]),
    default="iso",
    help="Timestamp format (default: iso)",
)
@click.option("--utc", is_flag=True, help="Use UTC timezone")
@click.option("--json", "as_json", is_flag=True, help="Return the timestamp as JSON.")
@click.option(
    "--dry-run", is_flag=True, help="Describe generation without producing a timestamp."
)
@click.option(
    "--yes", "-y", is_flag=True, help="Accept this non-interactive operation."
)
def gen_timestamp(fmt, utc, as_json, dry_run, yes):
    """
    Generate timestamp

    \b
    Formats:
      iso     - ISO 8601 format (2025-01-08T12:30:45)
      file    - File-safe format (20250108_123045)
      compact - Compact format (20250108123045)
      human   - Human readable (Jan 08, 2025 12:30:45)

    \b
    Examples:
      scitex repro generate-timestamp
      scitex repro generate-timestamp --format file
      scitex repro generate-timestamp --format human --utc
    """
    if dry_run:
        if as_json:
            from scitex_dev import Result

            click.echo(
                Result(
                    success=True, data={"dry_run": True, "format": fmt, "utc": utc}
                ).to_json()
            )
        else:
            click.echo(
                f"Would generate a {fmt} timestamp using {'UTC' if utc else 'local time'}."
            )
        return
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
            from scitex_dev import Result

            click.echo(
                Result(
                    success=True, data={"timestamp": ts, "format": fmt, "utc": utc}
                ).to_json()
            )
        else:
            click.echo(ts)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@repro.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--algorithm",
    "-a",
    default="sha256",
    help="File-byte hash algorithm (default: sha256); use --raw for array files.",
)
@click.option("--short", "-s", is_flag=True, help="Output short hash (first 8 chars)")
@click.option(
    "--raw",
    is_flag=True,
    help="Stream file bytes without deserializing array/checkpoint contents.",
)
def hash(file_path, algorithm, short, raw):
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
      scitex repro hash weights.npz --raw --algorithm md5

    Array mode disables NumPy pickle and uses weights-only checkpoint loading.
    Use --raw for untrusted or serialized-object files: it streams bytes without
    interpreting their contents and honors --algorithm.
    """
    try:
        import hashlib
        from pathlib import Path

        path = Path(file_path)

        # Try to load as array first
        hash_val = None
        try:
            if not raw and path.suffix in (".npy", ".npz"):
                import numpy as np

                from scitex.repro import hash_array

                arr = np.load(path, allow_pickle=False)
                if isinstance(arr, np.lib.npyio.NpzFile):
                    # For npz, hash all arrays
                    with arr:
                        hashes = [hash_array(arr[key]) for key in arr.files]
                    hash_val = hashlib.sha256("".join(hashes).encode()).hexdigest()
                else:
                    hash_val = hash_array(arr)
            elif not raw and path.suffix in (".pt", ".pth"):
                import torch

                data = torch.load(path, map_location="cpu", weights_only=True)
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


# Keep established scripts working without advertising abbreviated names.
for _old_name, _command in (("gen-id", gen_id), ("gen-timestamp", gen_timestamp)):
    _alias = copy.copy(_command)
    _alias.hidden = True
    repro.add_command(_alias, _old_name)


if __name__ == "__main__":
    repro()
