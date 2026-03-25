# Programmatic Use of stx.cli

The `stx.cli` module exposes utilities for programmatic interaction with the Click-based CLI, including recursive help display and JSON output.

## Accessing the CLI group

```python
from scitex.cli import cli

# cli is a Click group — can be invoked programmatically
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(cli, ["scholar", "--help"])
print(result.output)
```

## print_help_recursive

Print formatted help for a Click group and all its subcommands (terminal output):

```python
import click
from scitex.cli import print_help_recursive

ctx = click.Context(cli)
print_help_recursive(ctx, cli)
# Outputs colored "━━━ scitex <subcommand> ━━━" banners with help text
```

## group_to_json

Output available subcommands as a JSON `Result` envelope:

```python
import click
from scitex.cli import group_to_json

ctx = click.Context(cli)
group_to_json(ctx, cli)
# Prints JSON: {"success": true, "data": {"commands": {"scholar": "Scholar CLI commands.", ...}}}
```

## help_recursive_to_json

Get the full CLI command tree as structured JSON:

```python
import click
from scitex.cli import help_recursive_to_json

ctx = click.Context(cli)
help_recursive_to_json(ctx, cli)
# Prints JSON with nested command structure including help text, params, and subcommands
```

## format_python_signature

Format a Python function signature with Click-style terminal colors:

```python
from scitex.cli import format_python_signature
import scitex as stx

name_colored, sig_colored = format_python_signature(stx.io.save, multiline=True)
print(f"{name_colored}{sig_colored}")
# Output: green bold function name + colored parameter types and defaults
```

## LazyGroup (internal)

The CLI uses a custom `LazyGroup` that only imports subcommand modules when they are actually invoked. This keeps `scitex --help` instant and avoids loading all 30+ subcommand modules at startup.

```python
from scitex.cli.main import LazyGroup

# LazyGroup subcommands are defined as:
# (module_path, attr_name, short_help)
# They are importlib.import_module'd only when first called
```
