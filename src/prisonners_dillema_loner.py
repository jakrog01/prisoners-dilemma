import matplotlib

matplotlib.use("Agg")
import os
import sys

import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from scipy.signal import convolve2d

COOP = 0
DEFECT = 1
LONER = 2


class SpatialPD:
    def __init__(self, grid_size=200, t_factor=1.6, density=0.33, loner_payoff=0.6):
        self.grid_size = grid_size
        self.t_factor = t_factor
        self.density = density
        self.loner_payoff = loner_payoff
        self.evolution = {"coop": [], "defect": [], "loner": []}
        self._initialize_grids()
        self._add_to_evolution()

    def run_simulation(
        self,
        steps=100,
        make_gif=False,
        gif_filename="evolution.gif",
        gif_frames=50,
        make_summary=False,
        summary_filename="summary.png",
    ):
        snapshots = []
        snapshot_interval = max(1, steps // max(1, gif_frames))

        for i in range(steps):
            self._step(make_gif, snapshots, snapshot_interval, i)

        if make_gif:
            self._save_gif_from_snapshots(snapshots, gif_filename)

        if make_summary:
            self._plot_results(summary_filename)

    def _save_gif_from_snapshots(self, snapshots, filename):
        fig, ax = plt.subplots(figsize=(6, 6))
        cmap = mcolors.ListedColormap(["blue", "red", "green", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        ax.axis("off")
        artists = []
        for grid, step_num in snapshots:
            img = ax.imshow(grid, cmap=cmap, norm=norm, interpolation="nearest")
            txt = ax.text(
                0.5, 1.01, f"Step: {step_num}", transform=ax.transAxes, ha="center"
            )
            artists.append([img, txt])
        anim = animation.ArtistAnimation(fig, artists, interval=100, blit=False)
        anim.save(filename, writer="pillow", fps=15)
        plt.close(fig)

    def _count_neighbors(self):
        coop_mask = self.grid == COOP
        num_coop_neighbors = convolve2d(
            coop_mask.astype(int), self.computation_kernel, mode="same", boundary="wrap"
        )
        return num_coop_neighbors, coop_mask

    def _initialize_grids(self):
        remaining_density = 1 - 2 * self.density
        if remaining_density < 0:
            remaining_density = 0 

        probs = [self.density, self.density, remaining_density]
        total_p = sum(probs)
        probs = [p / total_p for p in probs]

        self.grid = np.random.choice(
            [COOP, DEFECT, LONER], size=(self.grid_size, self.grid_size), p=probs
        )
        self.payoff_grid = np.zeros((self.grid_size, self.grid_size), dtype=float)
        self.computation_kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    def _update_strategies(self):
        p_coop = np.where(self.grid == COOP, self.payoff_grid, -np.inf)
        p_defect = np.where(self.grid == DEFECT, self.payoff_grid, -np.inf)
        p_loner = np.where(self.grid == LONER, self.payoff_grid, -np.inf)

        max_coop_neigh = ndimage.maximum_filter(p_coop, size=3, mode="wrap")
        max_defect_neigh = ndimage.maximum_filter(p_defect, size=3, mode="wrap")
        max_loner_neigh = ndimage.maximum_filter(p_loner, size=3, mode="wrap")

        best_is_coop = (max_coop_neigh > max_defect_neigh) & (
            max_coop_neigh > max_loner_neigh
        )
        best_is_defect = (max_defect_neigh > max_coop_neigh) & (
            max_defect_neigh > max_loner_neigh
        )
        best_is_loner = (max_loner_neigh > max_coop_neigh) & (
            max_loner_neigh > max_defect_neigh
        )

        next_grid = self.grid.copy()

        mask_coop = self.grid == COOP
        next_grid[mask_coop & best_is_defect] = DEFECT
        next_grid[mask_coop & best_is_loner] = LONER

        mask_defect = self.grid == DEFECT
        next_grid[mask_defect & best_is_coop] = COOP
        next_grid[mask_defect & best_is_loner] = LONER

        mask_loner = self.grid == LONER
        next_grid[mask_loner & best_is_coop] = COOP
        next_grid[mask_loner & best_is_defect] = DEFECT

        self.grid = next_grid

    def _compute_payoffs(self):
        num_coop_neighbors, coop_mask = self._count_neighbors()
        self.payoff_grid[:] = 0
        self.payoff_grid[coop_mask] = num_coop_neighbors[coop_mask] * 1.0

        defect_mask = self.grid == DEFECT
        self.payoff_grid[defect_mask] = num_coop_neighbors[defect_mask] * self.t_factor

        loner_mask = self.grid == LONER
        self.payoff_grid[loner_mask] = self.loner_payoff * 9.0

    def _add_to_evolution(self):
        unique, counts = np.unique(self.grid, return_counts=True)
        data = dict(zip(unique, counts))
        self.evolution["coop"].append(data.get(COOP, 0))
        self.evolution["defect"].append(data.get(DEFECT, 0))
        self.evolution["loner"].append(data.get(LONER, 0))

    def _step(self, make_gif, snapshots, snapshot_interval, i):
        self._compute_payoffs()
        self._update_strategies()
        self._add_to_evolution()
        if make_gif and i % snapshot_interval == 0:
            snapshots.append((self.grid.copy(), i))

    def _plot_results(self, filename):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        cmap = mcolors.ListedColormap(["blue", "red", "green", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        ax1.imshow(self.grid, cmap=cmap, norm=norm, interpolation="nearest")
        ax1.set_title(f"Final State (c={self.loner_payoff:.4f}), b = {self.t_factor:.4f}")
        ax1.axis("off")

        t = range(len(self.evolution["coop"]))
        ax2.plot(t, self.evolution["coop"], label="Kooperanci", color="blue")
        ax2.plot(t, self.evolution["defect"], label="Zdrajcy", color="red")
        ax2.plot(t, self.evolution["loner"], label="Samotni", color="green")
        ax2.legend()
        plt.tight_layout()
        plt.savefig(filename)
        plt.close(fig)

    def get_ratios(self):
        total = self.grid_size**2
        u, c = np.unique(self.grid, return_counts=True)
        counts = dict(zip(u, c))
        return (
            counts.get(COOP, 0) / total,
            counts.get(DEFECT, 0) / total,
            counts.get(LONER, 0) / total,
        )
    
    def plot_phase_diagram(self, filename="phase_trajectory.png"):
        total = self.grid_size ** 2
        fc_history = np.array(self.evolution["coop"]) / total
        fd_history = np.array(self.evolution["defect"]) / total

        plt.figure(figsize=(10, 10))
        
        points = len(fc_history)
        if points > 1:
            base_color = "midnightblue"
            
            for i in range(points - 1):
                current_alpha = 0.1 + (0.9 * (i / points))
                plt.plot(fd_history[i:i+2], fc_history[i:i+2], 
                         color=base_color, lw=1.5, alpha=current_alpha)

            plt.scatter(fd_history[0], fc_history[0], color='midnightblue', s=20, label='Start', zorder=5)
        
        plt.xlabel('Ułamek Zdrajców ($f_D$)', fontsize=14)
        plt.ylabel('Ułamek Kooperantów ($f_C$)', fontsize=14)
        plt.title(f'Ewolucja Trajektorii Fazowej (b={self.t_factor}, c={self.loner_payoff})', fontsize=16)
        
        plt.grid(True, linestyle=':', alpha=0.4)
        plt.plot([0, 1], [1, 0], color="grey", linestyle="--", alpha=0.3, label="$f_C + f_D = 1$")
        
        plt.xlim(-0.01, 1.01)
        plt.ylim(-0.01, 1.01)
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()

    def plot_ternary(self, filename="ternary_trajectory.png"):
        total = self.grid_size ** 2
        fc = np.array(self.evolution["coop"]) / total
        fd = np.array(self.evolution["defect"]) / total
        fl = np.array(self.evolution["loner"]) / total
        def transform(c, d, l):
            x = d + 0.5 * l
            y = (np.sqrt(3) / 2) * l
            return x, y

        x, y = transform(fc, fd, fl)

        plt.figure(figsize=(10, 9))
        
        plt.plot([0, 1, 0.5, 0], [0, 0, np.sqrt(3)/2, 0], color="black", lw=2, zorder=1)
        
        points = len(x)
        base_color = "midnightblue"
        for i in range(points - 1):
            alpha = 0.1 + (0.9 * (i / points))
            plt.plot(x[i:i+2], y[i:i+2], color=base_color, lw=2, alpha=alpha, zorder=2)

        plt.scatter(x[0], y[0], color='midnightblue', s=20, label='Start', zorder=5)

        plt.text(-0.05, -0.05, "Kooperanci (C)", fontsize=14, fontweight='bold', ha='center')
        plt.text(1.05, -0.05, "Zdrajcy (D)", fontsize=14, fontweight='bold', ha='center')
        plt.text(0.5, (np.sqrt(3)/2) + 0.05, "Samotnicy (L)", fontsize=14, fontweight='bold', ha='center')

        plt.axis('off')
        plt.title(f"Diagram Ternarny Populacji (b={self.t_factor}, c={self.loner_payoff})", fontsize=16, pad=30)
        plt.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()

if __name__ == "__main__":
    try:
        b_fac = float(os.environ.get("B_FACTOR_VALUE", "1.9"))
        n_runs = int(os.environ.get("N_RUNS", "1"))
        output_dir = os.environ.get("OUTPUT_DIR", ".")
    except (TypeError, ValueError):
        print("Error: Env variables B_FACTOR_VALUE or OUTPUT_DIR not set.")
        sys.exit(1)

    print(f"Processing b={b_fac} | Runs={n_runs} | Out={output_dir}")

    results_c = []
    results_d = []
    results_l = []

    for run_idx in range(n_runs):
        sim = SpatialPD(grid_size=100, t_factor=b_fac, density=0.33, loner_payoff=0.6)
        is_first = run_idx == 0

        sim.run_simulation(
            steps=1000,
            make_gif=is_first,
            gif_filename=os.path.join(output_dir, "vis.gif"),
            gif_frames=60,
            make_summary=is_first,
            summary_filename=os.path.join(output_dir, "summary.png"),
        )

        if is_first:
            sim.plot_phase_diagram(os.path.join(output_dir, "phase_trajectory.png"))
            sim.plot_ternary(os.path.join(output_dir, "ternary_trajectory.png"))

        rc, rd, rl = sim.get_ratios()
        results_c.append(rc)
        results_d.append(rd)
        results_l.append(rl)

        print(f"Run {run_idx+1}/{n_runs}: C={rc:.4f} D={rd:.4f} L={rl:.4f}")

    with open(os.path.join(output_dir, "stats.txt"), "w") as f:
        f.write(f"B_FACTOR: {b_fac}\n")
        f.write(f"MEAN_COOP: {np.mean(results_c):.6f}\n")
        f.write(f"STD_COOP: {np.std(results_c):.6f}\n")

        f.write(f"MEAN_DEFECT: {np.mean(results_d):.6f}\n")
        f.write(f"STD_DEFECT: {np.std(results_d):.6f}\n")

        f.write(f"MEAN_LONER: {np.mean(results_l):.6f}\n")
        f.write(f"STD_LONER: {np.std(results_l):.6f}\n")
