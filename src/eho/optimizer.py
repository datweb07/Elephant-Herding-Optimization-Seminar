from time import perf_counter

import numpy as np

from .operators import find_best_and_worst, update_population
from .result import EHOResult, Generation, PopulationSnapshot


class ElephantHerdingOptimizer:
    """EHO tối thiểu hóa theo luồng dữ liệu của Listings 12.1–12.2."""

    def __init__(self, objective_function, config):
        if not callable(objective_function):
            raise TypeError("Hàm mục tiêu phải gọi được.")
        self.objective_function = objective_function
        self.config = config

    def initialize_population(self, rng):
        """Khởi tạo mỗi tọa độ đồng đều trong cận danh nghĩa."""
        config = self.config
        lower, upper = np.asarray(config.lower_bounds), np.asarray(config.upper_bounds)
        return lower + (upper - lower) * rng.random((config.population_size, config.dimension))

    def evaluate_population(self, population):
        """Gọi hàm mục tiêu đúng một lần cho mỗi hàng."""
        fitness = []
        for position in population:
            value = np.asarray(self.objective_function(position.copy()))
            if value.ndim != 0 or np.iscomplexobj(value) or not np.isfinite(float(value)):
                raise ValueError("Hàm mục tiêu phải trả một số thực hữu hạn.")
            fitness.append(float(value))
        return np.array(fitness)

    def run(self, *, initial_population=None, rng=None, save_population=False,
            on_generation=None, should_stop=None):
        """Chạy EHO và chỉ dừng ở ranh giới thế hệ.

        Callback nhận chỉ số và snapshot bất biến sau mỗi thế hệ, kể cả thế hệ 0.
        """
        config = self.config
        if rng is None:
            rng = np.random.default_rng(config.random_seed)
        lower, upper = np.asarray(config.lower_bounds), np.asarray(config.upper_bounds)
        started = perf_counter()
        if initial_population is None:
            population = self.initialize_population(rng)
        else:
            population = np.array(initial_population, dtype=float, copy=True)
            if (population.shape != (config.population_size, config.dimension)
                    or not np.isfinite(population).all()
                    or np.any((population < lower) | (population > upper))):
                raise ValueError("Quần thể ban đầu sai kích thước hoặc có tọa độ ngoài cận.")
        fitness = self.evaluate_population(population)
        evaluations = len(fitness)
        current_best, worst = find_best_and_worst(fitness)
        leader = current_best
        best_position = population[leader].copy()
        best_fitness = float(fitness[leader])
        history, snapshots = [], []
        callback_time = 0.0
        center = draws = None
        termination_reason = "max_generations"

        for number in range(config.max_generations + 1):
            violations = (population < lower) | (population > upper)
            row = Generation(
                number, best_fitness, float(fitness[current_best]),
                float(fitness.mean()), float(fitness[worst]), evaluations,
                int(violations.any(axis=1).sum()), int(violations.sum()),
                perf_counter() - started - callback_time,
            )
            history.append(row)
            if save_population or on_generation is not None:
                snapshot = PopulationSnapshot(
                    population, fitness, current_best, worst, leader, best_position, center, draws,
                )
                for array in (population, fitness, best_position, center, draws):
                    if array is not None:
                        array.setflags(write=False)
                if save_population:
                    snapshots.append(snapshot)
                if on_generation is not None:
                    before_callback = perf_counter()
                    on_generation(row, snapshot)
                    callback_time += perf_counter() - before_callback
            if number == config.max_generations:
                break
            if should_stop is not None and should_stop():
                termination_reason = "stopped"
                break
            population, center, draws = update_population(
                population, best_position, leader, worst, config, rng,
            )
            fitness = self.evaluate_population(population)
            evaluations += len(fitness)
            current_best, worst = find_best_and_worst(fitness)
            if fitness[current_best] < best_fitness:
                leader = current_best
                best_fitness = float(fitness[leader])
                best_position = population[leader].copy()

        return EHOResult(
            best_position.copy(), best_fitness, history[0].best_fitness, population.copy(),
            fitness.copy(), tuple(history), tuple(snapshots), history[-1].number, evaluations,
            perf_counter() - started - callback_time, config, config.random_seed, termination_reason,
        )
