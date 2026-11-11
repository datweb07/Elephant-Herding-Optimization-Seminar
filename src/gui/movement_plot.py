import numpy as np
from matplotlib.patches import Rectangle


def display_points(positions):
    """Giữ hai tọa độ đầu, hoặc đặt điểm 1D trên cùng một trục."""
    positions = np.atleast_2d(positions)
    if positions.shape[1] == 1:
        return np.column_stack((positions[:, 0], np.zeros(len(positions))))
    return positions[:, :2]


def position_axes(axis, config, pump):
    if pump:
        axis.set(xlabel="Lưu lượng bơm 1 (m³/h)", ylabel="Lưu lượng bơm 2 (m³/h)")
    else:
        axis.set_xlabel("x₁")
        if config.dimension >= 2:
            axis.set_ylabel("x₂")
    if config.dimension == 1:
        axis.set_yticks([])


def draw_movement(axis, config, current, previous, number, *, pump=False):
    """Vẽ đúng hai snapshot liền kề. Không tính lại bước EHO."""
    axis.clear()
    position_axes(axis, config, pump)
    title = "Quần thể khởi tạo" if previous is None else f"Bước cập nhật {number - 1} → {number}"
    if config.dimension > 2:
        title += f"  |  Chiếu x₁, x₂ từ {config.dimension} chiều"
    axis.set_title(title)
    low = display_points(config.lower_bounds)[0]
    high = display_points(config.upper_bounds)[0]
    if config.dimension > 1:
        axis.add_patch(Rectangle(low, *(high - low), fill=False, edgecolor="0.55",
                                 linestyle="--", linewidth=1, label="Cận danh nghĩa"))
    else:
        axis.axvspan(low[0], high[0], facecolor="0.94", label="Cận danh nghĩa")

    new = display_points(current.population)
    axis.scatter(*new.T, s=22, color="#60A5FA", label="Vị trí mới" if previous else "Cá thể")
    if previous is None:
        axis.scatter(*display_points(current.best_position).T, marker="*", s=105,
                     color="#FBBF24", label="Best khởi tạo")
    else:
        old = display_points(previous.population)
        axis.scatter(*old.T, s=23, facecolors="none", edgecolors="#94A3B8", label="Vị trí cũ")
        leader = previous.leader_index
        worst = previous.worst_index
        regular = np.ones(len(new), dtype=bool)
        regular[[leader, worst]] = False

        def arrows(mask, color, label, width):
            starts = old[mask]
            deltas = new[mask] - starts
            axis.quiver(*starts.T, *deltas.T, angles="xy", scale_units="xy", scale=1,
                        color=color, width=width, label=label, zorder=3)

        if regular.any():
            arrows(regular, "#94A3B8", "(12.1) Tiến về best", 0.003)
        arrows([leader], "#2563EB", f"(12.2) Đầu đàn #{leader + 1}", 0.005)
        if worst != leader:
            arrows([worst], "#F97316", f"(12.4) Tách #{worst + 1}", 0.005)
        axis.scatter(*display_points(previous.best_position).T, marker="*", s=105,
                     color="#FBBF24", label="Best lịch sử trước bước", zorder=4)
        axis.scatter(*display_points(current.center_before).T, marker="+", s=85,
                     color="#2563EB", label="Tâm quần thể cũ", zorder=4)
        if len(new) <= 15:
            for index, point in enumerate(new, 1):
                axis.annotate(str(index), point, xytext=(4, 4), textcoords="offset points", fontsize=8)
    axis.autoscale_view()
    if config.dimension > 1:
        axis.set_aspect("equal", adjustable="box")
    axis.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=8, frameon=False)
