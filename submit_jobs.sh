#!/usr/bin/env bash
set -euo pipefail

export ACCOUNT="${ACCOUNT:-g100-2263}"
export PARTITION="${PARTITION:-topola}"
export MAX_PARALLEL="${MAX_PARALLEL:-60}"
export OUT_ROOT="${OUT_ROOT:-$(pwd)/output}"

mkdir -p "${OUT_ROOT}"
mkdir -p "${OUT_ROOT}/_slurm"

NUM_JOBS=50
START_VAL=1.6
END_VAL=1.7
PARAM_FILE="${OUT_ROOT}/f_factors_list.txt"

echo "Generating parameters..."

python3 -c "
start = $START_VAL
end = $END_VAL
steps = $NUM_JOBS
step_size = (end - start) / (steps - 1) if steps > 1 else 0
for i in range(steps):
    print(f'{start + (i * step_size):.6f}')
" > "${PARAM_FILE}"

ARRAY_MAX=$((NUM_JOBS - 1))

echo "Submitting array job 0-${ARRAY_MAX}..."

sbatch \
  --account="${ACCOUNT}" \
  --partition="${PARTITION}" \
  --array="0-${ARRAY_MAX}%${MAX_PARALLEL}" \
  --output="${OUT_ROOT}/_slurm/%A_%a.out" \
  --error="${OUT_ROOT}/_slurm/%A_%a.err" \
  --export=ALL,OUT_ROOT="${OUT_ROOT}",PARAM_FILE="${PARAM_FILE}" \
  slurm_array.sbatch
