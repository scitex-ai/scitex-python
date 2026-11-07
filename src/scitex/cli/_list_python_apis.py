"""Compatibility-preserving umbrella Python API inspection command."""

import click


@click.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List SciTeX Python APIs (same operation as dev introspect list-apis scitex).

    $ scitex dev list-python-apis --json
    """
    from .introspect import api

    ctx.invoke(
        api, dotted_path="scitex", verbose=verbose, max_depth=max_depth, as_json=as_json
    )
