---

# stx.scholar — Citation Graph

The citation graph module builds and analyzes citation networks using CrossRef
data. It supports both a local SQLite database (via `crossref-local`) and an
HTTP API.

## Quick Start

```python
from scitex.scholar import CitationGraphBuilder, plot_citation_graph

# Using local SQLite database
builder = CitationGraphBuilder(db_path="/path/to/crossref.db")

# Using crossref-local HTTP API
builder = CitationGraphBuilder(api_url="http://localhost:31291")

# Build a citation graph around a seed DOI
graph = builder.build("10.1038/s41586-020-2008-3", top_n=20)
```

---

## Data Models

```python
from scitex.scholar.citation_graph import PaperNode, CitationEdge, CitationGraph

# PaperNode — a paper in the graph
node: PaperNode = graph.nodes["10.1038/s41586-020-2008-3"]
node.doi
node.title
node.year
node.citation_count
node.authors

# CitationEdge — directed citation relationship
edge: CitationEdge   # source.doi cites target.doi
edge.source_doi
edge.target_doi
edge.weight          # co-citation or bibliographic coupling score

# CitationGraph — the complete network
graph.nodes          # dict[doi, PaperNode]
graph.edges          # list[CitationEdge]
len(graph.nodes)
len(graph.edges)
```

---

## Building Graphs

```python
# Expand from seed paper (top_n most-connected papers)
graph = builder.build("10.1038/s41586-020-2008-3", top_n=20)

# Grow existing graph
graph = builder.expand(graph, hops=2)

# Graph similarity measures are computed automatically:
# - co-citation strength (papers that are cited together)
# - bibliographic coupling (papers that cite the same papers)
```

---

## Visualization

```python
from scitex.scholar.citation_graph import plot_citation_graph, list_backends

# Check available backends
backends = list_backends()
# ["networkx", "d3", "visjs", "cytoscape"]

# Plot the graph (selects best available backend)
plot_citation_graph(graph)

# Export for specific visualization tool
plot_citation_graph(graph, backend="d3", output="./graph.html")
plot_citation_graph(graph, backend="cytoscape", output="./graph.json")
```

---

## MCP Interface

```bash
# Via MCP tools (for AI agents)
mcp__scitex__crossref_cache_create
mcp__scitex__crossref_cache_query
mcp__scitex__crossref_cache_plot_network
mcp__scitex__crossref_cache_plot_scatter
mcp__scitex__crossref_cache_top_cited
mcp__scitex__crossref_cache_stats
mcp__scitex__crossref_cache_citation_summary
mcp__scitex__crossref_cache_export
mcp__scitex__crossref_cache_list
```

---

## Integration with Papers

```python
# Convert graph nodes to Papers collection
from scitex.scholar.citation_graph import CitationGraphBuilder
from scitex.scholar import Papers, Paper

builder = CitationGraphBuilder(db_path="/path/to/crossref.db")
graph = builder.build("10.1038/s41586-020-2008-3", top_n=20)

# Get DOIs from graph
dois = list(graph.nodes.keys())

# Create Papers from DOIs for enrichment
papers_list = []
for doi in dois:
    p = Paper()
    p.metadata.id.doi = doi
    node = graph.nodes[doi]
    p.metadata.basic.title = node.title
    p.metadata.basic.year = node.year
    papers_list.append(p)

papers = Papers(papers_list, project="citation_network")
```
