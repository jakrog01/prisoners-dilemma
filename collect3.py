import glob
import math
import os

OUTPUT_ROOT = "output_eco_cd"
files = glob.glob(os.path.join(OUTPUT_ROOT, "sim_*/stats.txt"))
results = []

def safe_float(value_str):
    try:
        val = float(value_str)
        return val if not math.isnan(val) else 0.0
    except:
        return 0.0


for filepath in files:
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            data = {}
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()

            if "REG_RATE" in data:
                reg_val = float(data["REG_RATE"])

                mean_env = safe_float(data.get("MEAN_ENV", 0.0))
                std_env = safe_float(data.get("STD_ENV", 0.0))
                mean_c = safe_float(data.get("MEAN_COOP", 0.0))

                results.append(
                    {"reg": reg_val, "env_m": mean_env, "env_s": std_env, "c_m": mean_c}
                )

    except Exception as e:
        print(e)

results.sort(key=lambda x: x["reg"])

reg_values = [r["reg"] for r in results]
env_means = [r["env_m"] for r in results]
env_stds = [r["env_s"] for r in results]
coop_means = [r["c_m"] for r in results]

print("\n" + "=" * 60)
print("=" * 60)
print(f"reg_values = {reg_values}")
print(f"env_means = {env_means}")
print(f"env_stds = {env_stds}")
print(f"coop_means = {coop_means}")
print("=" * 60)
