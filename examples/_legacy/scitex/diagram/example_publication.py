#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication mode example: Compact layout for journal figures.
"""

from scitex.diagram import Diagram, PaperMode


def main():
    # Create diagram with publication settings
    d = Diagram(type="workflow", title="SciTeX Figure Lifecycle")

    # Add nodes
    d.add_node("python", "Python", shape="rounded")
    d.add_node("savefig", "savefig()", shape="box")
    d.add_node("figz", ".figz Bundle", shape="stadium", emphasis="primary")
    d.add_node("spec", "spec.json", shape="box")
    d.add_node("data", "data.csv", shape="box")
    d.add_node("preview", "preview", shape="box", emphasis="muted")
    d.add_node("editor", "Editor", shape="rounded", emphasis="primary")
    d.add_node("ai", "AI Review", shape="diamond", emphasis="primary")
    d.add_node("export", "Export", shape="stadium", emphasis="success")

    # Add edges
    d.add_edge("python", "savefig")
    d.add_edge("savefig", "figz")
    d.add_edge("figz", "spec", style="dashed")
    d.add_edge("figz", "data", style="dashed")
    d.add_edge("figz", "preview", style="dashed")
    d.add_edge("figz", "editor")
    d.add_edge("editor", "figz", label="changes")
    d.add_edge("figz", "ai")
    d.add_edge("ai", "figz", label="diffs")
    d.add_edge("figz", "export")

    # Set publication mode
    d.spec.paper.mode = PaperMode.PUBLICATION
    d.spec.paper.return_edges = [("editor", "figz"), ("ai", "figz")]

    # Define layers for rank=same constraints
    d.spec.layout.layers = [
        ["python", "savefig"],
        ["figz"],
        ["spec", "data", "preview"],
        ["editor", "ai"],
        ["export"],
    ]

    # Compile
    print("=== Graphviz DOT (Publication Mode) ===")
    print(d.to_graphviz())

    print("\n=== Note ===")
    print("Render with: dot -Tpng output.dot -o output.png")
    print("Graphviz produces tighter layout than Mermaid.")


if __name__ == "__main__":
    main()
