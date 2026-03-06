import os
import subprocess
import numpy as np
from multiprocessing import Pool, cpu_count
import sys

START_VAL = 0.0     
END_VAL = 0.01       
NUM_JOBS = 100        
N_RUNS_PER_JOB = 50
SCRIPT_NAME = "src/prisonners_dillema_env.py"
OUTPUT_ROOT = "output_eco_cd"          

def run_simulation(args):
    idx, reg_rate = args
    task_dir = os.path.join(OUTPUT_ROOT, f"sim_{idx}_reg{reg_rate:.6f}")
    os.makedirs(task_dir, exist_ok=True)

    env = os.environ.copy()
    env["REG_RATE_VALUE"] = str(reg_rate)
    env["B_FACTOR_VALUE"] = "1.9"
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
        reg_values = np.linspace(START_VAL, END_VAL, NUM_JOBS)
    else:
        reg_values = [START_VAL]

    tasks = [(i, r) for i, r in enumerate(reg_values)]
    
    workers = max(1, cpu_count() - 2) 
    with Pool(processes=workers) as pool:
        pool.map(run_simulation, tasks)
