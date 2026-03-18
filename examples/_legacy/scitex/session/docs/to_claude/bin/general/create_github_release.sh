#!/bin/bash
# Script to create GitHub release for gpu-pac v0.1.0

echo "==================================="
echo "Creating GitHub Release for v0.1.0"
echo "==================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run from the gPAC root directory"
    exit 1
fi

# Push the tag
echo "Pushing tag v0.1.0 to GitHub..."
git push origin v0.1.0

# Create the release
echo "Creating GitHub release..."
gh release create v0.1.0 \
    --title "gpu-pac v0.1.0 - First Release" \
    --notes-file RELEASE_NOTES_v0.1.0.md \
    --verify-tag \
    dist/gpu_pac-0.1.0-py3-none-any.whl \
    dist/gpu_pac-0.1.0.tar.gz

echo ""
echo "✅ Release created successfully!"
echo "View at: https://github.com/ywatanabe1989/gPAC/releases/tag/v0.1.0"
