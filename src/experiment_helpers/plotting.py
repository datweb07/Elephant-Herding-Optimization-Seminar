import matplotlib.pyplot as plt
import numpy as np

from objectives.rastrigin import rastrigin_landscape


def plot_convergence(groups, *, evaluations=False):
    """Vẽ trung bình best lịch sử và vùng ±1 độ lệch chuẩn mẫu."""
    _, axis = plt.subplots(figsize=(8, 4))
    for label, results in groups.items():
        fitness = np.array([result.best_fitness_history for result in results])
        mean = fitness.mean(axis=0)
        std = fitness.std(axis=0, ddof=1) if len(fitness) > 1 else np.zeros_like(mean)
        x = results[0].evaluation_history if evaluations else np.arange(len(mean))
        axis.plot(x, mean, label=str(label))
        axis.fill_between(x, mean - std, mean + std, alpha=0.13)
    axis.set(xlabel="Số đánh giá" if evaluations else "Thế hệ", ylabel="Best lịch sử")
    axis.legend()
    axis.grid(alpha=0.2)
    return axis


def plot_fitness_comparison(summary):
    _, axis = plt.subplots(figsize=(8, 4), layout="constrained")
    axis.bar(range(len(summary)), summary["mean"], yerr=summary["std"].fillna(0), capsize=3)
    axis.set_xticks(range(len(summary)), list(map(str, summary.index)), rotation=25, ha="right")
    axis.set_ylabel("Best fitness trung bình ± SD")
    return axis


def plot_fitness_distribution(frame):
    groups = list(frame.groupby("group", sort=False))
    figure, axes = plt.subplots(1, len(groups), figsize=(3.5 * len(groups), 3), squeeze=False,
                               layout="constrained")
    for axis, (label, group) in zip(axes[0], groups):
        axis.hist(group["fitness"], bins="auto", color="#2359a9")
        axis.set(title=str(label), xlabel="Best fitness cuối", ylabel="Tần số")
    return figure


def plot_parameter_heatmap(table):
    _, axis = plt.subplots(layout="constrained")
    image = axis.imshow(table.to_numpy(), cmap="Blues")
    axis.set_xticks(range(len(table.columns)), table.columns)
    axis.set_yticks(range(len(table.index)), table.index)
    axis.set(xlabel="Alpha", ylabel="Beta")
    for (row, column), value in np.ndenumerate(table.to_numpy()):
        color = "white" if image.norm(value) > 0.6 else "#152d47"
        axis.text(column, row, f"{value:.3g}", ha="center", va="center", color=color)
    axis.figure.colorbar(image, ax=axis, label="Mean best fitness")
    return axis


def plot_rastrigin_contour(result):
    config = result.configuration
    if config.dimension != 2:
        raise ValueError("Contour Rastrigin cần đúng 2 chiều.")
    points = [np.linspace(low, high, 120) for low, high in zip(config.lower_bounds, config.upper_bounds)]
    grid_x, grid_y = np.meshgrid(*points)
    _, axis = plt.subplots(figsize=(6, 5), layout="constrained")
    axis.contourf(grid_x, grid_y, rastrigin_landscape(np.stack([grid_x, grid_y], axis=-1)),
                  levels=24, cmap="Blues")
    axis.scatter(*result.final_population.T, s=18, color="#d66c31", label="Quần thể cuối")
    axis.scatter(*result.best_position, marker="*", s=120, color="#14825c", label="Best lịch sử")
    axis.set(xlabel="x₁", ylabel="x₂", title=f"Rastrigin 2D · seed {result.random_seed}")
    axis.legend()
    return axis


def plot_runtime_comparison(summary):
    _, axis = plt.subplots(figsize=(8, 4), layout="constrained")
    axis.bar(range(len(summary)), summary["seconds"], color="#14825c")
    axis.set_xticks(range(len(summary)), list(map(str, summary.index)), rotation=25, ha="right")
    axis.set_ylabel("Thời gian thuật toán trung bình (s)")
    return axis
