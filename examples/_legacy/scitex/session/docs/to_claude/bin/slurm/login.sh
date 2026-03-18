#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 04:59:48 (ywatanabe)"
# File: ./.claude-worktree/gPAC/docs/slurm/login.sh

PERSISTENT_FILE="./slurm-persistent.txt"

if [[ ! -f "$PERSISTENT_FILE" ]]; then
    echo "Error: Info file not found at $PERSISTENT_FILE" >&2
    exit 1
fi

NODE_NAME=$(cat "$PERSISTENT_FILE" | grep SLURM_HEAD_NODE | cut -d= -f2)

if [[ -z "$NODE_NAME" ]]; then
    echo "Error: Could not find node name" >&2
    exit 1
fi

echo "Connecting to node: $NODE_NAME"
ssh $NODE_NAME

# EOF
