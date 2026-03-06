import glob

files = glob.glob("output/sim_*/stats.txt")
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

            if "T_FACTOR" in data and "MEAN" in data:
                t_val = float(data["T_FACTOR"])
                mean_val = float(data["MEAN"])
                std_val = float(data.get("STD", 0.0))
                results.append((t_val, mean_val, std_val))
    except Exception as e:
        print(e)

results.sort(key=lambda x: x[0])

b_values = [r[0] for r in results]
means = [r[1] for r in results]
stds = [r[2] for r in results]

print("\n" + "=" * 40)
print("=" * 40 + "\n")

print(f"b_values = {b_values}")
print(f"coop_means = {means}")
print(f"coop_stds = {stds}")
