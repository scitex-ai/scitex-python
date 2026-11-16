# SciTeX MCP tools

The umbrella discovers installed leaf servers through the scitex-dev ecosystem
registry. Available tools depend on installed packages and enabled namespaces;
the running server's MCP `tools/list` response is the callable inventory.

```bash
scitex mcp list-tools --json       # Names and schemas from this installation
scitex mcp list-tools -vv          # Include descriptions
scitex serve                      # stdio
scitex serve -t http --port 8085   # HTTP transport
```

## Names and ownership

The umbrella applies the owning namespace once. A leaf's existing prefix is
removed before mounting: `audio_speak` stays `audio_speak`, rather than becoming
`audio_audio_speak`. Interior domain words are retained: Hub's
`api_scholar_search` becomes `hub_api_scholar_search`.

| Namespace | Provider | Examples |
| --- | --- | --- |
| `sdk_` | scitex-sdk app implementation | `sdk_read_file`, `sdk_validate` |
| `ui_` | scitex-sdk UI implementation | `ui_get_component`, `ui_list_components` |
| `dev_` | scitex-dev, including its linter engine | `dev_config_show`, `dev_linter_list_rules` |
| `hub_` | scitex-hub | `hub_skills_list`, `hub_sdk_data_get` |
| Other peer namespaces | Respective installed leaf | `audio_speak`, `clew_status`, `io_load`, `notebook_check`, `scholar_search_papers` |

SDK supplies app and UI tools; retired scitex-app/scitex-ui copies are not mounted.
The umbrella's old `cloud_` family becomes `hub_`. Clients using doubled prefixes,
`app_app_*`, `cloud_*`, or top-level `linter_*` must rediscover tools and update
saved calls. Standalone leaf servers keep their own local names; the umbrella
renames mounted tools without changing leaf callbacks or Python functions.

`SCITEX_MCP_USE_<NAMESPACE>=0` disables a mount. The legacy `APP` and `CLOUD`
opt-outs also disable their SDK and Hub replacements. Peer import and tool-name
discovery share the existing per-peer timeout; unavailable or ambiguous providers
are skipped with a warning. Renaming requires FastMCP's `mount(tool_names=...)`
API; unsupported versions report a mount error instead of advertising wrong names.

Mounts retain protocol schemas, middleware, resource and prompt namespaces.
MCP availability does not imply Web API admission or anonymous execution; the
host applies its own authentication and route policy.

## Client configuration

Configure a client to launch the umbrella stdio server, for example:

```json
{
  "mcpServers": {
    "scitex": {
      "command": "scitex",
      "args": ["serve"]
    }
  }
}
```

Use each leaf's installed CLI help and bundled skills for standalone server
commands and domain-specific arguments. Use discovery rather than a fixed tool
count or a copied inventory when generating documentation.
