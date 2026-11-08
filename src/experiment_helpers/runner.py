from dataclasses import asdict, replace
from itertools import product

import numpy as np
import pandas as pd

from eho import ElephantHerdingOptimizer


def seeds_for(mode):
    """Trả tập seed cố định cho chế độ thí nghiệm."""
    if mode == "QUICK":
        return [11, 23, 37, 53, 71]
    if mode == "FULL":
        return list(range(101, 126))
    raise ValueError("Chế độ phải là QUICK hoặc FULL.")


def run_multiple_seeds(objective, config, seeds, *, save_population=False):
    """Chạy mọi seed đã khai báo, giữ cả những lần có kết quả kém."""
    return [
        ElephantHerdingOptimizer(objective, replace(config, random_seed=seed)).run(
            save_population=save_population,
        )
        for seed in seeds
    ]


def compare_configurations(objective, configs, seeds, *, save_population=False):
    seeds = tuple(seeds)
    return {
        label: run_multiple_seeds(objective, config, seeds, save_population=save_population)
        for label, config in configs.items()
    }


def results_frame(groups):
    """Tổng hợp một hàng cho mỗi cấu hình và seed."""
    rows = []
    for group, results in groups.items():
        for result in results:
            config = result.configuration
            position = result.best_position
            rows.append({
                "group": group, "seed": result.random_seed, "alpha": config.alpha,
                "beta": config.beta, "dimension": config.dimension,
                "population": config.population_size, "generations": result.completed_generations,
                "lower_bounds": config.lower_bounds, "upper_bounds": config.upper_bounds,
                "best_position": tuple(position.tolist()),
                "fitness": result.best_fitness, "initial": result.initial_best_fitness,
                "seconds": result.execution_time_seconds, "evaluations": result.total_evaluations,
                "violating_individuals": result.violating_individuals,
                "violating_coordinates": result.violating_coordinates,
                "violating_generations": sum(row.violating_coordinates > 0 for row in result.history),
                "best_in_bounds": bool(np.all((position >= config.lower_bounds) & (position <= config.upper_bounds))),
            })
    return pd.DataFrame(rows)


def assert_reproducible(objective, config, seed):
    """Kiểm tra chính xác các đại lượng xác định, bỏ đồng hồ thực thi."""
    first, second = run_multiple_seeds(objective, config, [seed, seed], save_population=True)
    np.testing.assert_array_equal(first.best_position, second.best_position)
    for left, right in zip(first.history, second.history, strict=True):
        left_metrics, right_metrics = asdict(left), asdict(right)
        del left_metrics["elapsed"], right_metrics["elapsed"]
        assert left_metrics == right_metrics
    for left, right in zip(first.population_history, second.population_history, strict=True):
        np.testing.assert_array_equal(left.population, right.population)
        np.testing.assert_array_equal(left.fitness, right.fitness)
        np.testing.assert_array_equal(left.random_values, right.random_values)


def pump_grid_reference(scenario, points=81):
    """Mốc hữu hạn trên lưới đều trong cận, độc lập với lần chạy EHO."""
    candidates = product(*(np.linspace(0, upper, points) for upper in scenario.upper_bounds))
    position = min(candidates, key=scenario)
    return position, scenario(position)


def maximum_overshoot(result):
    """Độ vượt cận lớn nhất trong lịch sử chi tiết."""
    if not result.population_history:
        raise ValueError("Độ vượt cận cần lịch sử quần thể.")
    config = result.configuration
    return max(
        max(0.0, float(np.max(config.lower_bounds - snapshot.population)),
            float(np.max(snapshot.population - config.upper_bounds)))
        for snapshot in result.population_history
    )
