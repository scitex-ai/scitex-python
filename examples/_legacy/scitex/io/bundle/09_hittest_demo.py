#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/09_hittest_demo.py

"""
Example 09: FTS Validation

Demonstrates:
- Three-level validation (schema, semantic, strict)
- Validating node, encoding, theme
- Handling validation errors
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, names):
    """Remove existing bundles."""
    for name in names:
        path = out_dir / name
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_valid_bundle(plt, out_dir):
    """Create a valid FTS bundle."""
    x = np.linspace(0, 10, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.legend()
    ax.set_title("Validation Demo")

    bundle_path = out_dir / "validation_demo.zip"
    sio.save(fig, bundle_path)
    plt.close(fig)

    bundle = FTS(bundle_path)
    bundle.node.name = "Validation Demo"
    bundle.theme = {"mode": "light"}
    bundle.encoding = {
        "traces": [
            {
                "trace_id": "sin",
                "x": {"column": "x", "type": "quantitative"},
                "y": {"column": "y", "type": "quantitative"},
            }
        ]
    }
    bundle.save()

    return bundle


def validate_schema(bundle, logger):
    """Run schema-level validation."""
    logger.info("\n" + "=" * 60)
    logger.info("LEVEL 1: Schema Validation")
    logger.info("=" * 60)
    logger.info("Checks JSON structure matches expected schema")

    result = bundle.validate(level="schema")
    logger.info(f"\nValidation passed: {result.is_valid}")
    if result.errors:
        for err in result.errors:
            logger.warning(f"  Error: {err}")
    else:
        logger.info("  No schema errors")


def validate_semantic(bundle, logger):
    """Run semantic-level validation."""
    logger.info("\n" + "=" * 60)
    logger.info("LEVEL 2: Semantic Validation")
    logger.info("=" * 60)
    logger.info("Checks logical consistency (e.g., encoding refs valid columns)")

    result = bundle.validate(level="semantic")
    logger.info(f"\nValidation passed: {result.is_valid}")
    if result.errors:
        for err in result.errors:
            logger.warning(f"  Error: {err}")
    else:
        logger.info("  No semantic errors")


def validate_strict(bundle, logger):
    """Run strict-level validation."""
    logger.info("\n" + "=" * 60)
    logger.info("LEVEL 3: Strict Validation")
    logger.info("=" * 60)
    logger.info("Full validation including data presence and integrity")

    result = bundle.validate(level="strict")
    logger.info(f"\nValidation passed: {result.is_valid}")
    if result.errors:
        for err in result.errors:
            logger.warning(f"  Error: {err}")
    else:
        logger.info("  No strict validation errors")


def demonstrate_invalid_bundle(out_dir, logger):
    """Create and validate an invalid bundle."""
    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATION: Invalid Bundle")
    logger.info("=" * 60)

    invalid_bundle = FTS(
        out_dir / "invalid_demo.zip",
        create=True,
        node_type="plot",
        name="Invalid Demo",
    )

    # Set invalid encoding (referencing non-existent columns)
    invalid_bundle.encoding = {
        "traces": [
            {
                "trace_id": "test",
                "x": {"column": "nonexistent_column", "type": "quantitative"},
                "y": {"column": "also_nonexistent", "type": "quantitative"},
            }
        ]
    }

    try:
        invalid_result = invalid_bundle.validate(level="strict")
        logger.info(f"\nInvalid bundle validation: {invalid_result.is_valid}")
        if invalid_result.errors:
            logger.info("Detected errors:")
            for err in invalid_result.errors[:5]:
                logger.warning(f"  - {err}")
    except Exception as e:
        logger.info(f"Validation raised: {type(e).__name__}: {e}")

    invalid_bundle.save(validate=True, validation_level="schema")
    logger.info("\nBundle saved with schema-level validation")


def print_summary(logger):
    """Print validation levels summary."""
    logger.info("\n" + "=" * 60)
    logger.info("Validation Levels Summary:")
    logger.info("  schema: JSON structure only (fastest)")
    logger.info("  semantic: Logical consistency (medium)")
    logger.info("  strict: Full integrity check (slowest)")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate FTS bundle validation."""
    logger.info("Example 09: FTS Validation Demo")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, ["validation_demo.zip", "invalid_demo.zip"])

    bundle = create_valid_bundle(plt, out_dir)

    validate_schema(bundle, logger)
    validate_semantic(bundle, logger)
    validate_strict(bundle, logger)

    demonstrate_invalid_bundle(out_dir, logger)

    print_summary(logger)

    logger.success("Example 09 completed!")


if __name__ == "__main__":
    main()

# EOF
