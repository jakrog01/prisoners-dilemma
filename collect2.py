import glob
import math

files = glob.glob("output/sim_*/stats.txt")
results = []

def safe_float(value_str):
    try:
        val = float(value_str)
        if math.isnan(val):
            return 0.0
        return val
    except (ValueError, TypeError):
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

            if "B_FACTOR" in data:
                b_val = float(data["B_FACTOR"])

                mean_c = safe_float(data.get("MEAN_COOP", data.get("MEAN", 0.0)))
                std_c = safe_float(data.get("STD_COOP", data.get("STD", 0.0)))

                mean_d = safe_float(data.get("MEAN_DEFECT", 0.0))
                std_d = safe_float(data.get("STD_DEFECT", 0.0))

                mean_l = safe_float(data.get("MEAN_LONER", 0.0))
                std_l = safe_float(data.get("STD_LONER", 0.0))

                results.append(
                    {
                        "b": b_val,
                        "c_m": mean_c,
                        "c_s": std_c,
                        "d_m": mean_d,
                        "d_s": std_d,
                        "l_m": mean_l,
                        "l_s": std_l,
                    }
                )

    except Exception as e:
        print(e)

results.sort(key=lambda x: x["b"])

b_values = [r["b"] for r in results]

coop_means = [r["c_m"] for r in results]
coop_stds = [r["c_s"] for r in results]

defect_means = [r["d_m"] for r in results]
defect_stds = [r["d_s"] for r in results]

loner_means = [r["l_m"] for r in results]
loner_stds = [r["l_s"] for r in results]

print("\n" + "=" * 50)
print("=" * 50 + "\n")

print(f"b_values = {b_values}")
print("")
print(f"coop_means = {coop_means}")
print(f"coop_stds = {coop_stds}")
print("")
print(f"defect_means = {defect_means}")
print(f"defect_stds = {defect_stds}")
print("")
print(f"loner_means = {loner_means}")
print(f"loner_stds = {loner_stds}")
