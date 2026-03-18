#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-04 04:46:34 (ywatanabe)"
# File: ./.claude-worktree/gPAC/docs/slurm/run.sh

PERSISTENT_FILE="./slurm-persistent.txt"

_parse_persistent_info() {
    if [[ ! -f "$PERSISTENT_FILE" ]]; then
        echo "Error: Info file not found at $PERSISTENT_FILE" >&2
        exit 1
    fi
    cat "$PERSISTENT_FILE"
    eval $(cat "$PERSISTENT_FILE" | xargs -I {} echo "export {}")
}

_setup_master_address() {
    export MASTER_ADDR=$SLURM_HEAD_IP
    export MASTER_PORT=29500
}

usage() {
    cat << 'EOH'
Usage: $0 <command>

Examples:
  ./run.sh python script.py     # -> python -u script.py
  ./run.sh script.py            # -> python -u script.py
  ./run.sh python -u script.py  # -> unchanged
  ./run.sh nvidia-smi           # -> nvidia-smi
  CUDA_VISIBLE_DEVICES=0,1 ./run.sh python script.py  # -> use GPU 0,1
EOH
}


add_u_option_if_python() {
    if [[ "$1" == "python" ]] && [[ "$2" != "-u" ]]; then
        echo "python" "-u" "${@:2}"
    elif [[ "$1" == *.py ]]; then
        echo "python" "-u" "$@"
    else
        echo "$@"
    fi
}

_parse_persistent_info
_setup_master_address

main() {
    if [[ -z "$1" ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        usage
        exit 1
    fi

    args=($(add_u_option_if_python "$@"))

    # Default to all GPUs if not specified
    CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3}

    srun \
        --nodes=$SLURM_NNODES \
        --ntasks=4 \
        --tasks-per-node=4 \
        --gres=gpu:4 \
        --cpus-per-task=8 \
        --unbuffered \
        --export=ALL,MASTER_ADDR=$MASTER_ADDR,MASTER_PORT=$MASTER_PORT,CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES \
        "${args[@]}"
}

main "$@"

# EOF
