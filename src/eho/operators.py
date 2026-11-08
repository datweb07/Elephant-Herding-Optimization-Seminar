import numpy as np


def update_regular_elephant(position, best_position, alpha, random_values):
    """Equation (12.1). Dịch từng tọa độ về phía nghiệm tốt nhất lịch sử."""
    return position + alpha * (best_position - position) * random_values


def calculate_population_center(population):
    """Equation (12.3). Tính trung bình theo cột của quần thể cũ."""
    return np.mean(population, axis=0)


def update_best_elephant(center, beta):
    """Equation (12.2). Đặt voi đầu đàn tại beta nhân tâm."""
    return beta * center


def separate_worst_elephant(lower, upper, random_values):
    """Equation (12.4). Tạo vị trí mới với +1 và giữ nguyên giá trị vượt cận."""
    return lower + (upper - lower + 1) * random_values


def find_best_and_worst(fitness):
    """Lấy chỉ số đầu tiên khi bằng điểm, giống Listing 12.2."""
    return int(np.argmin(fitness)), int(np.argmax(fitness))


def update_population(population, best_position, leader_index, worst_index,
                      config, rng, *, random_values=None):
    """Trả quần thể mới, tâm cũ và các số ngẫu nhiên thực dùng cho từng hàng.

    Hàng đầu đàn được ưu tiên khi hai chỉ số trùng nhau. Có thể đưa ma trận
    số r vào trực tiếp để kiểm chứng một thế hệ có đủ dữ liệu.
    """
    center = calculate_population_center(population)
    lower = np.asarray(config.lower_bounds)
    upper = np.asarray(config.upper_bounds)
    updated = np.empty_like(population, dtype=float)
    if random_values is not None:
        random_values = np.asarray(random_values, dtype=float)
        if (random_values.shape != population.shape
                or not np.isfinite(random_values).all()
                or np.any((random_values < 0) | (random_values > 1))):
            raise ValueError("Ma trận r phải cùng kích thước quần thể và thuộc [0, 1].")
    draws = np.full_like(updated, np.nan)
    for index, position in enumerate(population):
        if index == leader_index:
            updated[index] = update_best_elephant(center, config.beta)
            continue
        draws[index] = rng.random(config.dimension) if random_values is None else random_values[index]
        if index == worst_index:
            updated[index] = separate_worst_elephant(lower, upper, draws[index])
        else:
            updated[index] = update_regular_elephant(position, best_position, config.alpha, draws[index])
    return updated, center, draws
