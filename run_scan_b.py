import os
import subprocess
import sys
from multiprocessing import Pool, cpu_count

import numpy as np

START_B = 2.10
END_B = 2.20
NUM_POINTS = 50
N_RUNS = 100
SCRIPT_NAME = "src/prisonners_dillema_env.py"
OUTPUT_ROOT = "output_scan_b"


def run_simulation(args):
    idx, b_val = args
    task_dir = os.path.join(OUTPUT_ROOT, f"sim_{idx}_b{b_val:.6f}")
    os.makedirs(task_dir, exist_ok=True)

    env = os.environ.copy()
    env["B_FACTOR_VALUE"] = str(b_val)
    env["REG_RATE_VALUE"] = "0.02"

    env["N_RUNS"] = str(N_RUNS)
    env["OUTPUT_DIR"] = task_dir

    try:
        subprocess.run(
            [sys.executable, SCRIPT_NAME],
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(e)


if __name__ == "__main__":
    b_values = np.linspace(START_B, END_B, NUM_POINTS)
    tasks = [(i, b) for i, b in enumerate(b_values)]

    workers = max(1, cpu_count() - 2)
    with Pool(processes=workers) as pool:
        pool.map(run_simulation, tasks)

