#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-18 09:38:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python.py


"""Minimal Demonstration - Pure Python Version"""

import argparse
import json
import logging
import os
import random
import shutil
import string
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def generate_session_id():
    """Generate a unique session ID with timestamp and random suffix."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{timestamp}_{random_suffix}"


def setup_logging(log_dir):
    """Set up logging to both file and console."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # File handlers
    stdout_handler = logging.FileHandler(log_dir / "stdout.log")
    stderr_handler = logging.FileHandler(log_dir / "stderr.log")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Format
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    logger.addHandler(console_handler)

    return logger


def save_plot_data_to_csv(fig, output_path):
    """Extract plot data and save to CSV."""
    csv_path = output_path.with_suffix(".csv")

    data_lines = ["ax_00_plot_line_0_line_x,ax_00_plot_line_0_line_y"]

    for ax in fig.get_axes():
        for line in ax.get_lines():
            x_data = line.get_xdata()
            y_data = line.get_ydata()

            for x, y in zip(x_data, y_data):
                data_lines.append(f"{x},{y}")

    csv_path.write_text("\n".join(data_lines))

    size_kb = csv_path.stat().st_size / 1024
    return csv_path, size_kb


def embed_metadata_in_image(image_path, metadata):
    """Embed metadata into image file."""
    img = Image.open(image_path)

    if image_path.suffix.lower() in [".png"]:
        # PNG metadata
        pnginfo = PngInfo()
        for key, value in metadata.items():
            pnginfo.add_text(key, str(value))
        img.save(image_path, pnginfo=pnginfo)
    elif image_path.suffix.lower() in [".jpg", ".jpeg"]:
        # JPEG EXIF metadata (simplified - full implementation needs piexif)
        # For demonstration, we'll save to a sidecar JSON file
        json_path = image_path.with_suffix(image_path.suffix + ".meta.json")
        json_path.write_text(json.dumps(metadata, indent=2))
        img.save(image_path, quality=95)
    else:
        img.save(image_path)


def save_figure(fig, output_path, metadata=None, symlink_to=None, logger=None):
    """Save figure with metadata and optional symlink."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add URL to metadata
    if metadata is None:
        metadata = {}
    metadata["url"] = "https://scitex.ai"

    if logger:
        logger.info(f"📝 Saving figure with metadata to: {output_path}")
        logger.info(f"  • Auto-added URL: {metadata['url']}")
        logger.info(f"  • Embedded metadata: {metadata}")

    # Save CSV data
    csv_path, csv_size = save_plot_data_to_csv(fig, output_path)
    if logger:
        logger.info(f"✅ Saved to: {csv_path} ({csv_size:.1f} KiB)")

    # Save figure
    fig.savefig(output_path, dpi=150, bbox_inches="tight")

    # Embed metadata
    embed_metadata_in_image(output_path, metadata)

    fig_size_kb = output_path.stat().st_size / 1024
    if logger:
        logger.info(f"✅ Saved to: {output_path} ({fig_size_kb:.1f} KiB)")

    # Create symlink
    if symlink_to:
        symlink_dir = Path(symlink_to)
        symlink_dir.mkdir(parents=True, exist_ok=True)
        symlink_path = symlink_dir / output_path.name

        # Remove existing symlink if present
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()

        # Create new symlink
        symlink_path.symlink_to(output_path.resolve())
        if logger:
            logger.info(f"✅ Symlinked: {symlink_path} -> {output_path}")


def load_image_with_metadata(image_path, logger=None):
    """Load image and extract embedded metadata."""
    image_path = Path(image_path)

    if logger:
        logger.info(f"✅ Loading image with metadata from: {image_path}")

    img = Image.open(image_path)
    metadata = {}

    if image_path.suffix.lower() in [".png"]:
        # PNG metadata
        metadata = dict(img.info)
    elif image_path.suffix.lower() in [".jpg", ".jpeg"]:
        # Try loading from sidecar JSON
        json_path = image_path.with_suffix(image_path.suffix + ".meta.json")
        if json_path.exists():
            metadata = json.loads(json_path.read_text())

    if logger and metadata:
        logger.info("  • Embedded metadata found:")
        for key, value in metadata.items():
            logger.info(f"    - {key}: {value}")

    return np.array(img), metadata


def demo(output_dir, filename, verbose=False, logger=None):
    """Show metadata without QR code (just embedded)."""

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Generate signal
    t = np.linspace(0, 2, 1000)
    signal = np.sin(2 * np.pi * 5 * t) * np.exp(-t / 2)

    # Plot
    ax.plot(t, signal)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Clean Figure (metadata embedded, no QR overlay)")
    ax.grid(True, alpha=0.3)

    # Save with metadata
    output_path = output_dir / filename
    save_figure(
        fig,
        output_path,
        metadata={"exp": "s01", "subj": "S001"},
        symlink_to=output_dir.parent / "data",
        logger=logger,
    )
    plt.close(fig)

    # Load back
    img, meta = load_image_with_metadata(output_path, logger=logger)

    return 0


def main():
    """Run demo - Pure Python Version."""

    # Parse arguments
    parser = argparse.ArgumentParser(description="Run demo - Pure Python Version")
    parser.add_argument(
        "-f",
        "--filename",
        default="demo.jpg",
        help="Output filename (default: demo.jpg)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=bool,
        default=True,
        help="Verbose output (default: True)",
    )

    args = parser.parse_args()

    # Generate session ID
    session_id = generate_session_id()

    # Setup directories
    script_path = Path(__file__).resolve()
    output_base = script_path.parent / (script_path.stem + "_out")
    running_dir = output_base / "RUNNING" / session_id
    logs_dir = running_dir / "logs"
    config_dir = running_dir / "CONFIGS"

    # Setup logging
    logger = setup_logging(logs_dir)

    # Print header
    print("=" * 40)
    print(f"Pure Python Demo")
    print(f"{session_id} (PID: {os.getpid()})")
    print(f"\n{script_path}")
    print(f"\nArguments:")
    print(f"    filename: {args.filename}")
    print(f"    verbose: {args.verbose}")
    print("=" * 40)
    print()

    logger.info("=" * 60)
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Output directory: {running_dir}")
    logger.info(f"PID: {os.getpid()}")
    logger.info("=" * 60)

    # Save config
    config_dir.mkdir(parents=True, exist_ok=True)
    config_data = {
        "ID": session_id,
        "FILE": str(script_path),
        "SDIR_OUT": str(output_base),
        "SDIR_RUN": str(running_dir),
        "PID": os.getpid(),
        "ARGS": vars(args),
    }
    (config_dir / "CONFIG.json").write_text(json.dumps(config_data, indent=2))

    try:
        # Run demo
        result = demo(output_base, args.filename, args.verbose, logger)

        # Move to success directory
        success_dir = output_base / "FINISHED_SUCCESS" / session_id
        success_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(running_dir), str(success_dir))

        logger.info(f"\n✅ Congratulations! The script completed: {success_dir}")
        print(f"\n✅ Congratulations! The script completed: {success_dir}")

        return result

    except Exception as e:
        # Move to error directory
        error_dir = output_base / "FINISHED_ERROR" / session_id
        error_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(running_dir), str(error_dir))

        logger.error(f"\n❌ Error: {e}", exc_info=True)
        print(f"\n❌ Error occurred. Logs saved to: {error_dir}")

        raise


if __name__ == "__main__":
    sys.exit(main())

# (.env-3.11) (wsl) scitex-code $ /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python.py
# ========================================
# Pure Python Demo
# 2025-11-18_09-31-00_NNLL (PID: 494069)

# /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python.py

# Arguments:
#     filename: demo.jpg
#     verbose: True
# ========================================

# INFO: ============================================================
# INFO: Session ID: 2025-11-18_09-31-00_NNLL
# INFO: Output directory: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/RUNNING/2025-11-18_09-31-00_NNLL
# INFO: PID: 494069
# INFO: ============================================================
# INFO: 📝 Saving figure with metadata to: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/demo.jpg
# INFO:   • Auto-added URL: https://scitex.ai
# INFO:   • Embedded metadata: {'exp': 's01', 'subj': 'S001', 'url': 'https://scitex.ai'}
# INFO: ✅ Saved to: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/demo.csv (38.0 KiB)
# INFO: ✅ Saved to: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/demo.jpg (138.6 KiB)
# INFO: ✅ Symlinked: /home/ywatanabe/proj/scitex-code/examples/data/demo.jpg -> /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/demo.jpg
# INFO: ✅ Loading image with metadata from: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/demo.jpg
# INFO:   • Embedded metadata found:
# INFO:     - exp: s01
# INFO:     - subj: S001
# INFO:     - url: https://scitex.ai
# INFO:
# ✅ Congratulations! The script completed: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/FINISHED_SUCCESS/2025-11-18_09-31-00_NNLL

# ✅ Congratulations! The script completed: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_pure_python_out/FINISHED_SUCCESS/2025-11-18_09-31-00_NNLL

# EOF
