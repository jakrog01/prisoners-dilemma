import os
import subprocess
import numpy as np
from multiprocessing import Pool, cpu_count
import sys

START_VAL = 1.5
END_VAL = 4.0
NUM_JOBS = 26
N_RUNS_PER_JOB = 50   
SCRIPT_NAME = "src/prisonners_dillema_loner.py" 
OUTPUT_ROOT = "output"          

def run_simulation(args):
    idx, b_factor = args
    task_dir = os.path.join(OUTPUT_ROOT, f"sim_{idx}_b{b_factor:.6f}")
    os.makedirs(task_dir, exist_ok=True)

    env = os.environ.copy()
    env["B_FACTOR_VALUE"] = str(b_factor)
    env["N_RUNS"] = str(N_RUNS_PER_JOB)
    env["OUTPUT_DIR"] = task_dir

    try:
        subprocess.run(
            [sys.executable, SCRIPT_NAME],
            env=env,
            check=True,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE  
        )
    except subprocess.CalledProcessError as e:
        print(e)

if __name__ == "__main__":
    if NUM_JOBS > 1:
        b_values = np.linspace(START_VAL, END_VAL, NUM_JOBS)
    else:
        b_values = [START_VAL]

    tasks = [(i, b) for i, b in enumerate(b_values)]

    workers = max(1, cpu_count() - 2) 
    
    with Pool(processes=workers) as pool:
        pool.map(run_simulation, tasks)

