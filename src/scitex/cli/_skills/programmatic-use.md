# Programmatic CLI access

The public Click group is `scitex.cli.cli`. Use a controlled runner to inspect
its output without invoking a provider's business operation:

```python
import json
from click.testing import CliRunner
from scitex.cli import cli

result = CliRunner().invoke(cli, ["--json"])
assert result.exit_code == 0
commands = json.loads(result.output)["data"]["commands"]
```

`group_to_json(ctx, group)` prints a Result JSON summary and calls `ctx.exit(0)`;
it does not return a dictionary. For the umbrella's normal summary it uses
visible metadata without loading provider command trees. Hidden aliases are
omitted.

`help_recursive_to_json(ctx, group)` prints a nested command tree and exits.
`print_help_recursive(ctx, group)` prints formatted help for the group and
nested commands. Recursive inspection can import optional provider parsers;
it is distinct from the normal metadata-only summary.

```python
import json
from scitex.cli import format_python_signature

name, signature = format_python_signature(json.dumps, multiline=True)
```

`LazyGroup` and its command specifications are dispatcher internals. Do not
manufacture command candidates from Python module names or invoke console
functions to discover their schema. Installed declarations, effective policy,
parser resolution and authorized execution are separate stages.

CLI and MCP use SciTeX Dev's same public operator-policy resolver with independent
surface preferences. Each constructed Root CLI retains one snapshot, including
its Dev view and aliases. The MCP server separately retains its construction
snapshot across tools and resources. Neither is a process-global preference cache
or a promise of hot revocation. Use a new CLI/server process after changing policy.
