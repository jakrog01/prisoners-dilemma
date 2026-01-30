#!/bin/bash
#SBATCH --job-name=pd_chaos
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=03:00:00

set -euo pipefail

if command -v module >/dev/null 2>&1; then module load python/3.10; fi
if [ -f ".venv/bin/activate" ]; then source .venv/bin/activate; fi

LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
MY_T_FACTOR=$(sed -n "${LINE_NUM}p" "${PARAM_FILE}")

TASK_DIR="${OUT_ROOT}/sim_${SLURM_ARRAY_TASK_ID}_b${MY_T_FACTOR}"
mkdir -p "${TASK_DIR}"

echo "Task ID: ${SLURM_ARRAY_TASK_ID} | T_Factor: ${MY_T_FACTOR} | Dir: ${TASK_DIR}"

export T_FACTOR_VALUE="${MY_T_FACTOR}"
export OUTPUT_DIR="${TASK_DIR}"
export N_RUNS=50

python3 main.py
