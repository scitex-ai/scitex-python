#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-11 13:32:44 (ywatanabe)"
# File: ./.claude/scripts/render_mermaid.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
# ---------------------------------------

LOG_FILE="$0.log"

mmd2images() {
    local path_mmd=$1
    local base_name=${path_mmd%.mmd}
    local path_svg="${base_name}.svg"
    local path_png="${base_name}.png"
    local path_gif="${base_name}.gif"

    # Step 1: Ensure mermaid file is in TD (top-down) format
    echo "Checking if Mermaid file is in TD format..."
    if ! grep -q "^graph TD" "$path_mmd"; then
        echo "Warning: Mermaid file is not using TD (top-down) format."
        echo "Converting to TD format..."
        sed -i 's/^graph \(LR\|RL\|BT\)/graph TD/' "$path_mmd"
    fi

    # Step 2: Convert MMD to SVG (high resolution)
    echo "Converting ${path_mmd} to SVG..."
    mmdc -i "$path_mmd" -o "$path_svg" --backgroundColor white

    # Step 3: Convert SVG to high-res PNG with reasonable size
    echo "Converting ${path_svg} to high-res PNG..."
    convert "$path_svg" -quality 100 -background white -flatten "$path_png"

    # Step 4: Convert PNG to GIF
    echo "Converting ${path_png} to GIF..."
    convert "$path_png" "$path_gif"

    # Output success message
    echo "Created: $path_svg"
    echo "Created: $path_png"
    echo "Created: $path_gif"

    # Return the paths to the created files
    echo "$path_svg $path_png $path_gif"
}

usage() {
    echo "Usage: $0 [-h|--help]"
    echo
    echo "Options:"
    echo " -h, --help   Display this help message"
    echo
    echo "Example:"
    echo " $0"
    echo
    echo "Purpose:"
    echo " Converts progress.mmd file to SVG, PNG and GIF formats"
    echo " and ensures all diagrams are in TD (top-down) format"
    exit 1
}

main() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        -h|--help) usage ;;
          -) echo "Unknown option: $1"; usage ;;
        esac
    done

    # Get the directory where this script is located
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Set the path to the Mermaid file
    local mermaid_file="${script_dir}/progress.mmd"

    # Check if the Mermaid file exists
    if [[ ! -f "$mermaid_file" ]]; then
        echo "Error: Mermaid file not found: $mermaid_file"
        exit 1
    fi

    # Check if mmdc command is available
    if ! command -v mmdc &> /dev/null; then
        echo "Error: mmdc command not found. Please install @mermaid-js/mermaid-cli:"
        echo "npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi

    # Check if convert command is available
    if ! command -v convert &> /dev/null; then
        echo "Error: convert command not found. Please install ImageMagick:"
        echo "sudo apt-get install imagemagick # Ubuntu/Debian"
        echo "brew install imagemagick # macOS with Homebrew"
        exit 1
    fi

    # Generate the images
    echo "Generating images from Mermaid diagram..."
    mmd2images "$mermaid_file"

    echo "Successfully generated SVG, PNG and GIF from Mermaid diagram."
    echo "SVG: ${mermaid_file%.mmd}.svg"
    echo "PNG: ${mermaid_file%.mmd}.png"
    echo "GIF: ${mermaid_file%.mmd}.gif"
}

{ main "$@"; } 2>&1 | tee "$LOG_FILE"

# EOF
