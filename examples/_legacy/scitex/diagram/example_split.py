#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split example: Auto-split large diagrams into multiple figures.
"""

from scitex.diagram import Diagram


def main():
    # Create a large diagram
    d = Diagram(type="workflow", title="Complex Pipeline")

    # Add many nodes
    d.add_node("input", "Input Data", shape="stadium")
    d.add_node("validate", "Validation", shape="rounded")
    d.add_node("clean", "Cleaning", shape="rounded")
    d.add_node("normalize", "Normalization", shape="rounded")
    d.add_node("features", "Feature Engineering", shape="rounded", emphasis="primary")
    d.add_node("select", "Feature Selection", shape="rounded")
    d.add_node("train", "Model Training", shape="rounded", emphasis="primary")
    d.add_node("tune", "Hyperparameter Tuning", shape="diamond")
    d.add_node("evaluate", "Evaluation", shape="rounded")
    d.add_node("deploy", "Deployment", shape="stadium", emphasis="success")

    # Add edges
    d.add_edge("input", "validate")
    d.add_edge("validate", "clean")
    d.add_edge("clean", "normalize")
    d.add_edge("normalize", "features")
    d.add_edge("features", "select")
    d.add_edge("select", "train")
    d.add_edge("train", "tune")
    d.add_edge("tune", "train", label="retry")
    d.add_edge("train", "evaluate")
    d.add_edge("evaluate", "deploy")

    # Define groups
    d.set_group("Preprocessing", ["input", "validate", "clean", "normalize"])
    d.set_group("Feature Engineering", ["features", "select"])
    d.set_group("Model Development", ["train", "tune", "evaluate"])
    d.set_group("Production", ["deploy"])

    print(f"Original diagram: {len(d.spec.nodes)} nodes")

    # Split into smaller figures
    parts = d.split(max_nodes=5, strategy="by_groups")

    print(f"Split into {len(parts)} figures")
    print()

    for i, part in enumerate(parts):
        label = chr(ord('A') + i)
        print(f"=== Figure {label}: {part.spec.title} ({len(part.spec.nodes)} nodes) ===")

        # List nodes
        for node in part.spec.nodes:
            ghost = "→" in node.label
            print(f"  {'[ghost] ' if ghost else ''}{node.id}: {node.label}")

        print()
        print("Mermaid:")
        print(part.to_mermaid())
        print()


if __name__ == "__main__":
    main()
