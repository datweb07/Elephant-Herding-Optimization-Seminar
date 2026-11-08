from dataclasses import dataclass

import numpy as np

from .config import EHOConfig


@dataclass(frozen=True)
class Generation:
    number: int
    best_fitness: float
    current_best: float
    mean_fitness: float
    worst_fitness: float
    evaluations: int
    violating_individuals: int
    violating_coordinates: int
    elapsed: float


@dataclass(frozen=True)
class PopulationSnapshot:
    population: np.ndarray
    fitness: np.ndarray
    best_index: int
    worst_index: int
    leader_index: int
    best_position: np.ndarray
    center_before: np.ndarray | None
    random_values: np.ndarray | None


@dataclass(frozen=True)
class EHOResult:
    best_position: np.ndarray
    best_fitness: float
    initial_best_fitness: float
    final_population: np.ndarray
    final_fitness_values: np.ndarray
    history: tuple[Generation, ...]
    population_history: tuple[PopulationSnapshot, ...]
    completed_generations: int
    total_evaluations: int
    execution_time_seconds: float
    configuration: EHOConfig
    random_seed: int | None
    termination_reason: str

    @property
    def best_fitness_history(self):
        return [row.best_fitness for row in self.history]

    @property
    def current_best_history(self):
        return [row.current_best for row in self.history]

    @property
    def mean_fitness_history(self):
        return [row.mean_fitness for row in self.history]

    @property
    def worst_fitness_history(self):
        return [row.worst_fitness for row in self.history]

    @property
    def evaluation_history(self):
        return [row.evaluations for row in self.history]

    @property
    def violating_individuals(self):
        return sum(row.violating_individuals for row in self.history)

    @property
    def violating_coordinates(self):
        return sum(row.violating_coordinates for row in self.history)
