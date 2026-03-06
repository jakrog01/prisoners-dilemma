import glob
import os

OUTPUT_ROOT = "output_scan_b"
files = glob.glob(os.path.join(OUTPUT_ROOT, "sim_*/stats.txt"))
results = []

for filepath in files:
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            data = {}
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()

            if "T_FACTOR" in data:
                b_val = float(data["T_FACTOR"])
                mean_c = float(data.get("MEAN_COOP", 0.0))
                mean_env = float(data.get("MEAN_ENV", 0.0))
                
                results.append({"b": b_val, "c": mean_c, "e": mean_env})

    except Exception:
        pass

results.sort(key=lambda x: x["b"])

b_vals = [r["b"] for r in results]
coops = [r["c"] for r in results]

print(f"b_values = {b_vals}")
print(f"coop_means = {coops}")