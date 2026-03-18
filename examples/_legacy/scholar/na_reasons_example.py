#!/usr/bin/env python3
"""
Example demonstrating N/A reasons in Scholar module output.

This example shows how the Scholar module now provides explanations
for missing data (N/A values) in the DataFrame output.
"""

from scitex.scholar import Scholar

# Create scholar instance
scholar = Scholar()

# Search for papers - mix of journal articles and arXiv preprints
papers = scholar.search(
    "machine learning transformers",
    source=["arxiv", "pubmed"],  # Mix of sources
    limit=10
)

# Enrich with metadata (some will fail)
papers.enrich()

# Convert to DataFrame to see N/A reasons
df = papers.to_dataframe()

# Display relevant columns showing N/A reasons
print("\n=== Impact Factor Column with N/A Reasons ===")
print(df[['title', 'impact_factor', 'journal']].head(10))

print("\n=== Citation Count Column with N/A Reasons ===")
print(df[['title', 'citation_count']].head(10))

print("\n=== Quartile Column with N/A Reasons ===")
print(df[['title', 'quartile', 'journal']].head(10))

# Show unique N/A reasons
print("\n=== Unique N/A Reasons Found ===")
for col in ['impact_factor', 'citation_count', 'quartile']:
    na_values = df[col][df[col].astype(str).str.startswith('N/A')]
    if len(na_values) > 0:
        print(f"\n{col}:")
        for reason in na_values.unique():
            print(f"  - {reason}")
