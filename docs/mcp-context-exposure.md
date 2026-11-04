# MCP context exposure

The umbrella reads SciTeX Dev's resolved package MCP switches before importing
or mounting registry providers. A package disabled centrally stays disabled even
when its namespace environment switch is enabled. The existing namespace switch
`SCITEX_MCP_USE_<NAMESPACE>=0` can further reduce exposure. Brand-adjusted peer
extras honor the same owner switch; umbrella-owned tools use the `scitex` switch.
These choices apply to the next server process, not an already running session.

## On-demand tool discovery (source capability)

With a SciTeX Dev build supplying `scitex_dev.context.configure_mcp_discovery`,
and a FastMCP version supplying `RegexSearchTransform`, enable upstream discovery:

```bash
SCITEX_MCP_DISCOVERY=search SCITEX_MCP_SEARCH_LIMIT=5 scitex mcp start
```

This uses FastMCP's existing search/call transform rather than a new search
engine, ontology or model service. The default is the compatible full listing.
An explicitly requested unsupported or invalid search configuration fails;
it does not silently fall back to advertising every tool.

Search limits advertised definitions, not authorization. A known tool may remain
callable even when omitted from a search result. Apply authorization separately
and preserve it through search and invocation. Discoverability is not runtime
health, and a tool definition is not evidence that its business operation works.

The shared Dev context report consumes explicitly supplied advertised metadata
and registry ownership. It measures normalized UTF-8 bytes and Unicode character
counts, identifies unattributed items, and reports unknown client total context
and token counts honestly. Installed tools, selected tools, later skill-body
loads and the agent's conversation are different quantities.

This document describes a source follow-up. It does not imply the running fleet
has this adapter, that an older Dev wheel supplies it, or that search mode has
been enabled on deployed agents.
