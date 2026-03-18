#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/examples/scitex/verify/10_programmatic_verification.py

"""Demonstrates programmatic verification API usage."""

from pathlib import Path

import scitex as stx
from scitex import verify

SCRIPT_DIR = Path(__file__).parent


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate programmatic verification API.

    Shows how to:
    - Get verification status
    - Verify specific runs
    - Trace dependency chains
    - Access database statistics
    """
    # 1. Database statistics
    logger.info("=== Database Statistics ===")
    stats = verify.stats()
    logger.info(f"Total runs: {stats['total_runs']}")
    logger.info(f"Success runs: {stats['success_runs']}")
    logger.info(f"Failed runs: {stats['failed_runs']}")

    # 2. List recent runs
    logger.info("\n=== Recent Runs ===")
    runs = verify.list_runs(limit=5)
    for run in runs[:5]:
        sid = run["session_id"]
        script = Path(run.get("script_path", "unknown")).name
        status = run.get("status", "unknown")
        logger.info(f"  {sid}: {script} [{status}]")

    # 3. Verify chain for the report
    logger.info("\n=== Chain Verification ===")
    target = str(SCRIPT_DIR / "08_analyze_out" / "report.json")
    if Path(target).exists():
        chain_result = verify.chain(target)
        logger.info(f"Target: {Path(target).name}")
        logger.info(f"Chain length: {len(chain_result.runs)}")
        logger.info(f"Overall status: {chain_result.status.value}")
        logger.info(f"Is verified: {chain_result.is_verified}")
        logger.info(f"Failed runs: {len(chain_result.failed_runs)}")

        logger.info("\nRuns in chain:")
        for run in chain_result.runs:
            badge = "✓" if run.is_verified else "✗"
            script = Path(run.script_path).name if run.script_path else "unknown"
            logger.info(f"  {badge} {run.session_id}: {script}")
            for f in run.mismatched_files:
                logger.info(f"    ✗ mismatch: {Path(f.path).name}")
    else:
        logger.warning(f"Target not found: {target}")
        logger.info("Run 00_run_all.sh first to generate the pipeline outputs")

    # 4. Generate verification summary
    logger.info("\n=== Verification Summary ===")
    logger.info("Use these commands for more details:")
    logger.info("  scitex clew status     # Show changed items")
    logger.info("  scitex clew list       # List all tracked runs")
    logger.info("  scitex clew chain FILE # Trace file dependencies")

    return 0


if __name__ == "__main__":
    main()


# EOF
