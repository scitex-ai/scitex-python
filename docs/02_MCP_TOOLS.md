# SciTeX MCP discovery

The installed, admitted provider catalog is authoritative; there is no fixed
umbrella tool count. Inspect it without invoking a business operation:

```bash
scitex mcp --help
scitex mcp list-tools --json
scitex mcp list-tools --summary
```

The JSON listing includes each tool's input parameters and actual
`output_schema`. A missing output schema is explicitly unspecified. Tools can
return a Result envelope or another shape; the listing does not normalize them.
The compatibility `result_envelope` field is a reference schema, not a promise
about every tool. Its additive `result_envelope_scope` field states that limit.

## Ownership and construction

CLI, MCP and skills preferences are independent axes of the same SciTeX Dev
package configuration and knob-state resolver. Python imports remain separate.
Enabling a package does not install it or manufacture a missing capability.

The Root CLI freezes its effective view at construction. The MCP server freezes
its own owner and namespace preferences at server/module construction and shares
that snapshot across generic mounts, compatibility adapters and resources. These
are separate construction boundaries, not a process-global cache. Changes are read at the
next construction, normally in a new CLI/server process. Existing objects do not
promise hot revocation.
This freezes registration admission, not provider data or authorization: native
operations retain their own current checks.

MCP owner declines also apply to the owner's compatibility namespaces and
resources. Root-owned adapters additionally require Root's MCP preference.
An existing `SCITEX_MCP_USE_<NAMESPACE>=0` switch can independently decline a
namespace; it cannot re-enable a declined owner.

The optional search discovery mode reduces the exposed definitions after
registration. It does not defer provider imports or authorize their operations.
Set `SCITEX_MCP_DISCOVERY=search` on the umbrella server to advertise discovery
tools instead of the full catalog. `SCITEX_MCP_SEARCH_LIMIT` sets the maximum
matches per search (a positive integer; default `5`). The default mode is `full`,
which preserves clients that expect the complete tool listing.

## Local client configuration

The package declares the stdio console entry point `scitex-mcp-server`. This
example enables search mode; omit `env` to retain the default full catalog.
These settings describe this source tree; older releases may not support them.

```json
{
  "mcpServers": {
    "scitex": {
      "command": "scitex-mcp-server",
      "env": {
        "SCITEX_MCP_DISCOVERY": "search",
        "SCITEX_MCP_SEARCH_LIMIT": "5"
      }
    }
  }
}
```

The CLI also exposes `scitex mcp start` (stdio by default). Inspect
`scitex mcp start --help` and `scitex mcp installation --help` for the installed
transport and setup options. A leaf's ordinary CLI executable is not necessarily
an MCP launcher; use that leaf's declared MCP setup rather than guessing arguments.
