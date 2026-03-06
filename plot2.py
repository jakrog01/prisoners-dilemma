import matplotlib.pyplot as plt

b_values = [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9000000000000004, 3.0, 3.1, 3.2, 3.3, 3.4000000000000004, 3.5, 3.6, 3.7, 3.8000000000000003, 3.9000000000000004, 4.0]

coop_means = [0.99298, 0.992412, 0.989994, 0.896254, 0.315226, 0.752976, 0.159094, 0.150868, 0.067854, 0.006584, 0.081214, 0.044994, 0.001374, 0.000828, 0.000834, 0.001362, 0.0, 0.0, 0.0, 2.4e-05, 0.0, 0.0, 0.0, 0.0, 0.0, 1.2e-05]
coop_stds = [0.003179, 0.004487, 0.005805, 0.013559, 0.015841, 0.058929, 0.291371, 0.276141, 0.188824, 0.022138, 0.25941, 0.187398, 0.005744, 0.004278, 0.004104, 0.008218, 0.0, 0.0, 0.0, 0.000118, 0.0, 0.0, 0.0, 0.0, 0.0, 8.4e-05]

defect_means = [0.00702, 0.007492, 0.010006, 0.103742, 0.50258, 0.228774, 0.03605, 0.036538, 0.03094, 0.00639, 0.009322, 0.01025, 0.002344, 0.001626, 0.001696, 0.00223, 0.0, 0.0, 0.0, 6e-05, 0.0, 0.0, 0.0, 0.0, 0.0, 3e-05]
defect_stds = [0.003179, 0.004457, 0.005805, 0.013551, 0.028438, 0.047916, 0.034842, 0.040177, 0.0386, 0.014122, 0.014849, 0.017033, 0.008014, 0.006315, 0.005765, 0.011376, 0.0, 0.0, 0.0, 0.000294, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00021]

loner_means = [0.0, 9.6e-05, 0.0, 4e-06, 0.182194, 0.01825, 0.804856, 0.812594, 0.901206, 0.987026, 0.909464, 0.944756, 0.996282, 0.997546, 0.99747, 0.996408, 1.0, 1.0, 1.0, 0.999916, 1.0, 1.0, 1.0, 1.0, 1.0, 0.999958]
loner_stds = [0.0, 0.000109, 0.0, 2.8e-05, 0.02552, 0.023695, 0.316814, 0.307829, 0.203083, 0.035197, 0.268874, 0.195083, 0.013727, 0.01057, 0.009837, 0.01958, 0.0, 0.0, 0.0, 0.000412, 0.0, 0.0, 0.0, 0.0, 0.0, 0.000294]


plt.figure(figsize=(10, 6))

plt.errorbar(
    b_values,
    coop_means,
    yerr=coop_stds,
    label="Kooperanci",
    fmt="d",
    color="blue",
    ecolor="blue",
    capthick=2,
    capsize=5,
    markersize=8,
    markeredgewidth=2,
    linewidth=2,
    alpha=0.8,
)

plt.errorbar(
    b_values,
    defect_means,
    yerr=defect_stds,
    label="Zdrajcy",
    fmt="s",
    color="red",
    ecolor="red",
    capthick=2,
    capsize=5,
    markersize=8,
    markeredgewidth=2,
    linewidth=2,
    alpha=0.8,
)

plt.errorbar(
    b_values,
    loner_means,
    yerr=loner_stds,
    label="Samotnicy",
    fmt="^",
    color="green",
    ecolor="green",
    capthick=2,
    capsize=5,
    markersize=8,
    markeredgewidth=2,
    linewidth=2,
    alpha=0.8,
)

plt.xlabel("Wartość współczynnika zdrajcy (b)", fontsize=14)

plt.ylabel("Średni odsetek populacji", fontsize=14)
plt.title(
    "Rozkład strategii w zależności od parametru b, c = 0.6",
    fontsize=16,
    fontweight="bold",
)

plt.tick_params(axis="both", which="major", labelsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12, loc="center right")

plt.ylim(-0.05, 1.05)
plt.tight_layout()
plt.show()
