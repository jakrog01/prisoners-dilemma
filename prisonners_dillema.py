import matplotlib
matplotlib.use('Agg')
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from scipy.signal import convolve2d
import os
import sys

COOP = 0
DEFECT = 1

class SpatialPD:
    def __init__(self, grid_size=200, t_factor=1.6, density=0.5):
        self.grid_size = grid_size
        self.t_factor = t_factor
        self.density = density
        self.evolution = {"coop": [], "defect": []}
        self._initialize_grids()
        self._add_to_evolution()

    def run_simulation(self, steps=100, make_gif=False, gif_filename="evolution.gif", gif_frames=50, make_summary=False, summary_filename="summary.png"):
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
        cmap = mcolors.ListedColormap(["blue", "red", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        ax.axis("off")
        artists = []
        for grid, step_num in snapshots:
            img = ax.imshow(grid, cmap=cmap, norm=norm, interpolation="nearest")
            txt = ax.text(0.5, 1.01, f"Step: {step_num}", transform=ax.transAxes, ha="center")
            artists.append([img, txt])
        anim = animation.ArtistAnimation(fig, artists, interval=100, blit=False)
        anim.save(filename, writer="pillow", fps=15)
        plt.close(fig)

    def _count_neighbors(self):
        coop_mask = (self.grid == COOP)
        defect_mask = (self.grid == DEFECT)
        
        num_coop_neighbors = convolve2d(coop_mask.astype(int), self.computation_kernel, mode="same", boundary="wrap")
        num_defect_neighbors = convolve2d(defect_mask.astype(int), self.computation_kernel, mode="same", boundary="wrap")
        
        return num_coop_neighbors, num_defect_neighbors, coop_mask, defect_mask

    def _initialize_grids(self):
        self.grid = np.random.choice([COOP, DEFECT], size=(self.grid_size, self.grid_size), p=[self.density, 1 - self.density])
        self.payoff_grid = np.zeros((self.grid_size, self.grid_size), dtype=float)
        self.computation_kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

    def _update_strategies(self):
        p_coop = np.where(self.grid == COOP, self.payoff_grid, -np.inf)
        p_defect = np.where(self.grid == DEFECT, self.payoff_grid, -np.inf)
        
        max_coop_neigh = ndimage.maximum_filter(p_coop, size=3, mode='wrap')
        max_defect_neigh = ndimage.maximum_filter(p_defect, size=3, mode='wrap')

        next_grid = self.grid.copy()
        
        mask_c_to_d = (self.grid == COOP) & (max_defect_neigh > max_coop_neigh)
        next_grid[mask_c_to_d] = DEFECT

        mask_d_to_c = (self.grid == DEFECT) & (max_coop_neigh > max_defect_neigh)
        next_grid[mask_d_to_c] = COOP
        
        self.grid = next_grid

    def _compute_payoffs(self):
        num_coop_neighbors, _, coop_mask, defect_mask = self._count_neighbors()
        self.payoff_grid[:] = 0
        self.payoff_grid[coop_mask] = num_coop_neighbors[coop_mask] * 1.0
        self.payoff_grid[defect_mask] = num_coop_neighbors[defect_mask] * self.t_factor

    def _add_to_evolution(self):
        unique, counts = np.unique(self.grid, return_counts=True)
        data = dict(zip(unique, counts))
        self.evolution["coop"].append(data.get(COOP, 0))
        self.evolution["defect"].append(data.get(DEFECT, 0))
    
    def _step(self, make_gif, snapshots, snapshot_interval, i):
        self._compute_payoffs()
        self._update_strategies()
        self._add_to_evolution()
        if make_gif and i % snapshot_interval == 0:
            snapshots.append((self.grid.copy(), i))
    
    def _plot_results(self, filename):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        cmap = mcolors.ListedColormap(["blue", "red", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        ax1.imshow(self.grid, cmap=cmap, norm=norm, interpolation="nearest")
        ax1.set_title(f"Final State (b={self.t_factor:.4f})")
        ax1.axis("off")

        t = range(len(self.evolution["coop"]))
        ax2.plot(t, self.evolution["coop"], label="Cooperators", color="blue")
        ax2.plot(t, self.evolution["defect"], label="Defectors", color="red")
        ax2.legend()
        plt.tight_layout()
        plt.savefig(filename)
        plt.close(fig)

    def get_coop_ratio(self):
        return np.sum(self.grid == COOP) / (self.grid_size ** 2)

if __name__ == "__main__":
    try:
        t_fac = float(os.environ.get("T_FACTOR_VALUE"))
        n_runs = int(os.environ.get("N_RUNS", "50"))
        output_dir = os.environ.get("OUTPUT_DIR", ".")
    except (TypeError, ValueError):
        print("Error: Env variables T_FACTOR_VALUE or OUTPUT_DIR not set.")
        sys.exit(1)

    print(f"Processing b={t_fac} | Runs={n_runs} | Out={output_dir}")
    
    ratios = []

    for run_idx in range(n_runs):
        sim = SpatialPD(grid_size=200, t_factor=t_fac, density=0.5)
        is_first = (run_idx == 0)
        
        sim.run_simulation(
            steps=300,
            make_gif=is_first,
            gif_filename=os.path.join(output_dir, "vis.gif"),
            gif_frames=60,
            make_summary=is_first,
            summary_filename=os.path.join(output_dir, "summary.png")
        )
        
        ratio = sim.get_coop_ratio()
        ratios.append(ratio)
        print(f"Run {run_idx+1}/{n_runs}: {ratio:.4f}")

    avg_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)
    
    with open(os.path.join(output_dir, "stats.txt"), "w") as f:
        f.write(f"T_FACTOR: {t_fac}\n")
        f.write(f"MEAN: {avg_ratio:.6f}\n")
        f.write(f"STD: {std_ratio:.6f}\n")
        f.write(f"DATA: {ratios}\n")

    print("Done.")