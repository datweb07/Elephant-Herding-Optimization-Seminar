import numpy as np


def rastrigin_landscape(coordinates):
    """Tính Rastrigin dọc theo trục cuối, kể cả lưới tọa độ để vẽ."""
    return np.sum(coordinates ** 2 + 10 * (1 - np.cos(2 * np.pi * coordinates)), axis=-1)


def rastrigin(position):
    """Equation (12.5). Hàm Rastrigin chuẩn, cực tiểu bằng 0 tại gốc."""
    coordinates = np.asarray(position, dtype=float)
    if coordinates.ndim != 1 or not coordinates.size or not np.isfinite(coordinates).all():
        raise ValueError("Rastrigin cần một vector hữu hạn khác rỗng.")
    return float(rastrigin_landscape(coordinates))
