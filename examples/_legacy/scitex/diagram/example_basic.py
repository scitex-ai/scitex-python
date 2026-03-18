#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic example: Create a simple workflow diagram programmatically.
"""

from scitex.diagram import Diagram


def main():
    # Create a workflow diagram
    d = Diagram(type="workflow", title="Data Processing Pipeline")

    # Add nodes
    d.add_node("input", "Raw Data", shape="stadium")
    d.add_node("clean", "Preprocessing", shape="rounded")
    d.add_node("transform", "Feature Extraction", shape="rounded", emphasis="primary")
    d.add_node("model", "ML Model", shape="rounded", emphasis="primary")
    d.add_node("output", "Results", shape="stadium", emphasis="success")

    # Add edges
    d.add_edge("input", "clean")
    d.add_edge("clean", "transform")
    d.add_edge("transform", "model")
    d.add_edge("model", "output")

    # Group related nodes
    d.set_group("Processing", ["clean", "transform"])
    d.set_group("Analysis", ["model"])

    # Export to Mermaid
    mmd = d.to_mermaid()
    print("=== Mermaid Output ===")
    print(mmd)

    # Export to Graphviz
    dot = d.to_graphviz()
    print("\n=== Graphviz Output ===")
    print(dot)

    # Export to YAML (can be edited and reloaded)
    yaml_content = d.to_yaml()
    print("\n=== YAML Specification ===")
    print(yaml_content)


if __name__ == "__main__":
    main()
