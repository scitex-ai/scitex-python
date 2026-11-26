---
description: |
  [TOPIC] CLI and MCP — scitex umbrella
  [DETAILS] Inspect installed command help, distinguish metadata discovery from execution, and start the MCP server explicitly with stdio. Preserve release-specific compatibility limits.
tags: [scitex-cli-reference]
---

# CLI and MCP — scitex

```bash
scitex --version
scitex --help
scitex mcp --help
scitex mcp start --help
```

The available groups depend on the installed release and providers. Inspect the
selected group's help instead of inferring a command from a Python module name.
Help success verifies parsing/discovery, not the operation itself.

## MCP

```bash
scitex mcp list-tools --module stats
scitex mcp start --transport stdio
```

The first command lists registered statistics tool metadata. The second starts
the server; bare `scitex mcp` displays help and does not start it. An MCP client
must use the `scitex` executable from the intended environment. Protocol metadata
discovery does not invoke the tools or prove their external services are ready.
No fixed tool count or universal result envelope is assumed.

## Skills and Web APIs

Use package-owned skill files and inspect the installed scitex-dev skill manager
before choosing an export/install command. In the checked public 2.30.8 and source
2.30.9 dependency sets, the legacy `scitex skills get` callback imports a missing
`scitex_dev.skills` module. Do not present that callback as verified by its help.
Do not assume a vendor-specific discovery directory.

Hub/app plugins provide Web API endpoints. Use their declared routes and owning
package documentation; a registered Python/CLI name is not a Web route.
