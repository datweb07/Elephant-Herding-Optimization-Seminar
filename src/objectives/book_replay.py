import numpy as np

from eho.operators import (
    calculate_population_center, find_best_and_worst, separate_worst_elephant,
    update_best_elephant, update_regular_elephant,
)

from .data_loader import load_book_example
from .rastrigin import rastrigin


def verify_book_example():
    """Đối chiếu số in trong sách với phép tính từ các toán tử thật."""
    data = load_book_example()
    initial = np.asarray(data["initial_population"])
    initial_fitness = [rastrigin(position) for position in initial]
    best, worst = find_best_and_worst(initial_fitness)
    center = calculate_population_center(initial)
    regular = update_regular_elephant(initial[0], initial[best], data["alpha"],
                                      np.asarray(data["regular_random"]))
    matriarch = update_best_elephant(center, data["beta"])
    separation = separate_worst_elephant(data["lower"], data["upper"],
                                         np.asarray(data["separation_random"]))
    updated_fitness = [rastrigin(position) for position in data["updated_population"]]
    rows = []

    def compare(label, actual, expected, tolerance):
        for index, (value, reference) in enumerate(zip(actual, expected), 1):
            delta = float(value - reference)
            rows.append({
                "step": f"{label} [{index}]", "book": reference, "python": float(value),
                "delta": delta, "tolerance": tolerance,
                "status": "MATCH" if abs(delta) <= tolerance else "MISMATCH",
            })

    compare("Fitness ban đầu", initial_fitness, data["initial_fitness"], 0.001)
    compare("Tâm", center, data["center"], 0.00051)
    compare("x1 (12.1)", regular, data["updated_population"][0], 0.00051)
    compare("x2 (12.4)", separation, data["updated_population"][1], 0.00051)
    compare("x3 (12.2)", matriarch, data["updated_population"][2], 0.00051)
    compare("Fitness từ tọa độ in", updated_fitness, data["updated_fitness"], 0.001)
    return data, best, worst, rows
