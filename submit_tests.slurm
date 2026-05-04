#!/bin/bash
#SBATCH --job-name=scitex-tests
#SBATCH --output=logs/test_run_%j.log
#SBATCH --error=logs/test_run_%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=normal

set -e

cd /home/ywatanabe/proj/scitex-python

echo "====== Starting test suite ======"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Timestamp: $(date)"

python -m pytest tests/ -v --tb=short -n auto
