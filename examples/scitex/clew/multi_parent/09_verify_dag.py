#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: examples/scitex/clew/multi_parent/09_verify_dag.py

"""Demo multi-parent DAG verification, claims, and visualization."""

from pathlib import Path

import scitex as stx

SCRIPT_DIR = Path(__file__).parent


def _demo_dag_verification():
    """Verify the full multi-parent DAG from two target files."""
    fig1 = str(SCRIPT_DIR / "08_make_figures_out" / "figure1.png")
    fig2 = str(SCRIPT_DIR / "08_make_figures_out" / "figure2.png")

    print("\n--- Multi-Target DAG Verification ---")
    result = stx.clew.dag([fig1, fig2])

    print(f"  Targets:           {len(result.target_files)} files")
    print(f"  Runs in DAG:       {len(result.runs)}")
    print(f"  Edges:             {len(result.edges)}")
    print(f"  Status:            {result.status.value}")
    print(f"  Verified:          {result.is_verified}")
    print(f"  Topological order: {len(result.topological_order)} sessions")
    print()
    for run in result.runs:
        badge = "\u2713" if run.is_verified else "\u2717"
        script = Path(run.script_path).name if run.script_path else "?"
        print(f"  {badge} {script} ({run.session_id[:20]}...)")


def _demo_claims():
    """Register claims and verify their DAG."""
    fig1 = str(SCRIPT_DIR / "08_make_figures_out" / "figure1.png")
    combined = str(SCRIPT_DIR / "07_merge_results_out" / "combined.csv")

    print("\n--- Claims Registration ---")
    stx.clew.add_claim(
        file_path="manuscript.tex",
        claim_type="figure",
        source_file=fig1,
        claim_value="Treatment group shows higher accuracy (p < 0.05)",
        line_number=42,
    )
    stx.clew.add_claim(
        file_path="manuscript.tex",
        claim_type="statistic",
        source_file=combined,
        claim_value="r = 0.72",
        line_number=87,
    )
    claims = stx.clew.list_claims()
    print(f"  Registered {len(claims)} claims")

    print("\n--- Claims-to-Sources DAG ---")
    dag = stx.clew.verify_claims_dag()
    print(f"  Runs in claims DAG: {len(dag.runs)}")
    print(f"  Edges:              {len(dag.edges)}")
    print(f"  Verified:           {dag.is_verified}")


def _demo_render():
    """Render the DAG to HTML."""
    from scitex.clew import render_dag

    fig1 = str(SCRIPT_DIR / "08_make_figures_out" / "figure1.png")
    fig2 = str(SCRIPT_DIR / "08_make_figures_out" / "figure2.png")

    output_dir = SCRIPT_DIR / "09_verify_dag_out"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n--- DAG Rendering ---")
    for fmt in ["html", "mmd"]:
        output = output_dir / f"dag.{fmt}"
        try:
            render_dag(
                str(output),
                target_files=[fig1, fig2],
                title="Multi-Parent DAG Demo",
                show_hashes=True,
            )
            print(f"  Generated: {output}")
        except Exception as e:
            print(f"  Skipped {fmt}: {e}")


@stx.session
def main(
    action: str = "all",
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demo multi-parent DAG features.

    Actions:
        dag       - Verify multi-target DAG
        claims    - Register claims and verify claims DAG
        render    - Render DAG to HTML
        all       - Run all demos
    """
    if action in ("dag", "all"):
        logger.info("Running DAG verification demo...")
        _demo_dag_verification()

    if action in ("claims", "all"):
        logger.info("Running claims demo...")
        _demo_claims()

    if action in ("render", "all"):
        logger.info("Rendering DAG...")
        _demo_render()

    return 0


if __name__ == "__main__":
    main()

# EOF
