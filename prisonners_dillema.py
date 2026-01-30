import matplotlib.animation as animation
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from scipy.signal import convolve2d

COOP = 0
DEFECT = 1


class SpatialPD:
    def __init__(self, grid_size=500, t_factor=1.5, density=0.5, noise_level=0.1):
        self.grid_size = grid_size
        self.t_factor = t_factor
        self.density = density
        self.noise_level = noise_level

        self.evolution = {"coop": [], "defect": []}

        self._initialize_grids()
        self._add_to_evolution()

    def run_simulation(
        self, steps=100, make_gif=False, gif_filename="evolution.gif", gif_frames=50
    ):
        if steps <= 0:
            raise ValueError("steps must be a positive integer")
        if make_gif and gif_frames <= 0:
            raise ValueError("gif_frames must be >= 1 when make_gif=True")

        snapshots = []
        snapshot_interval = max(1, steps // max(1, gif_frames))

        for i in range(steps):
            print(f"Running step {i + 1}/{steps}", end="\r")
            self._step(make_gif, snapshots, snapshot_interval, i)

        if make_gif:
            print("\nSaving GIF...", end="\r")
            self._save_gif_from_snapshots(snapshots, gif_filename)
            print(f"\nGIF saved as {gif_filename}")

        self._plot_results()

    def _save_gif_from_snapshots(self, snapshots, filename):
        fig, ax = plt.subplots(figsize=(6, 6))

        cmap = mcolors.ListedColormap(["blue", "red", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        ax.axis("off")

        artists = []
        for grid, step_num in snapshots:
            img = ax.imshow(grid, cmap=cmap, norm=norm, interpolation="nearest")
            title = ax.text(
                0.5,
                1.01,
                f"Step: {step_num} (b={self.t_factor})",
                transform=ax.transAxes,
                ha="center",
            )
            artists.append([img, title])

        anim = animation.ArtistAnimation(fig, artists, interval=200, blit=False)
        anim.save(filename, writer="pillow", fps=10)
        plt.close(fig)

    def _count_neighbors(self):
        coop_mask = (self.grid == COOP).astype(int)
        defect_mask = (self.grid == DEFECT).astype(int)

        num_coop_neighbors = convolve2d(
            coop_mask, self.computation_kernel, mode="same", boundary="wrap"
        )
        num_defect_neighbors = convolve2d(
            defect_mask, self.computation_kernel, mode="same", boundary="wrap"
        )

        return num_coop_neighbors, num_defect_neighbors, coop_mask, defect_mask

    def _initialize_grids(self):
        self.grid = np.random.choice(
            [COOP, DEFECT],
            size=(self.grid_size, self.grid_size),
            p=[self.density, 1 - self.density],
        )

        self.payoff_grid = np.zeros((self.grid_size, self.grid_size), dtype=float)

        self.computation_kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

    def update_strategies(self):
        max_payoff = ndimage.maximum_filter(self.payoff_grid, size=3, mode="wrap")

        p_coop = np.where(self.grid == COOP, self.payoff_grid, -np.inf)
        p_defect = np.where(self.grid == DEFECT, self.payoff_grid, -np.inf)

        max_coop = ndimage.maximum_filter(p_coop, size=3, mode="wrap")
        max_defect = ndimage.maximum_filter(p_defect, size=3, mode="wrap")

        next_grid = self.grid.copy()

        wins_defect = (max_defect >= max_coop) & (max_defect == max_payoff)
        next_grid[wins_defect] = DEFECT
        wins_coop = (max_coop > max_defect) & (max_coop == max_payoff)
        next_grid[wins_coop] = COOP

        self.grid = next_grid

    def _compute_payoffs(self):
        num_coop_neighbors, num_defect_neighbors, coop_mask, defect_mask = (
            self._count_neighbors()
        )
        self.payoff_grid[:] = 0
        self.payoff_grid[coop_mask] = num_coop_neighbors[coop_mask] * 1
        self.payoff_grid[defect_mask] = num_coop_neighbors[defect_mask] * self.t_factor

        noise = np.random.uniform(
            -self.noise_level, self.noise_level, size=self.grid.shape
        )
        self.payoff_grid += noise

    def _add_to_evolution(self):
        unique, counts = np.unique(self.grid, return_counts=True)
        data = dict(zip(unique, counts))

        self.evolution["coop"].append(data.get(COOP, 0))
        self.evolution["defect"].append(data.get(DEFECT, 0))

    def _plot_results(self):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        cmap = mcolors.ListedColormap(["blue", "red", "lightgrey"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        ax1.imshow(self.grid, cmap=cmap, norm=norm, interpolation="nearest")
        ax1.set_title(f"Final State (b={self.t_factor})")
        ax1.axis("off")

        t = range(len(self.evolution["coop"]))
        ax2.plot(t, self.evolution["coop"], label="Cooperators (Blue)", color="blue")
        ax2.plot(t, self.evolution["defect"], label="Defectors (Red)", color="red")

        ax2.set_title("Population Dynamics")
        ax2.set_xlabel("Time Step")
        ax2.set_ylabel("Count")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("results.png")

    def _step(self, make_gif=False, snapshots=None, snapshot_interval=10, i=0):
        self._compute_payoffs()
        self.update_strategies()
        self._add_to_evolution()

        if make_gif:
            if snapshots is None:
                raise ValueError("snapshots must be a list when make_gif=True")
            if snapshot_interval <= 0:
                raise ValueError("snapshot_interval must be a positive integer")
            if i % snapshot_interval == 0:
                snapshots.append((self.grid.copy(), i))


if __name__ == "__main__":
    sim = SpatialPD(grid_size=500, t_factor=1.8, density=0.5, noise_level=0.1)
    sim.run_simulation(
        steps=1000, make_gif=True, gif_filename="prisoners_dilemma.gif", gif_frames=100
    )
