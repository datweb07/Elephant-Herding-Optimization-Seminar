import numpy as np
import pytest

from eho import EHOConfig, ElephantHerdingOptimizer
from eho.operators import (
    calculate_population_center, separate_worst_elephant, update_best_elephant,
    update_population, update_regular_elephant,
)
from objectives import rastrigin
from objectives.book_replay import verify_book_example


@pytest.mark.parametrize("dimension", [2, 4])
def test_rastrigin_origin(dimension):
    assert rastrigin(np.zeros(dimension)) == 0


@pytest.mark.parametrize("invalid", [
    {"population_size": 1}, {"dimension": 0}, {"alpha": 1.1}, {"beta": np.nan},
    {"max_generations": 0}, {"lower_bounds": (0, 1)}, {"upper_bounds": -6},
    {"random_seed": -1},
])
def test_invalid_config(invalid):
    with pytest.raises(ValueError):
        EHOConfig(**invalid)


def test_initialization_uses_each_bound():
    config = EHOConfig(dimension=2, lower_bounds=(1, 10), upper_bounds=(3, 30))
    optimizer = ElephantHerdingOptimizer(rastrigin, config)
    population = optimizer.initialize_population(np.random.default_rng(42))
    assert population.shape == (5, 2)
    assert np.all(population >= config.lower_bounds)
    assert np.all(population < config.upper_bounds)


def test_regular_center_matriarch():
    population = np.array([[2, 4], [6, 10]])
    np.testing.assert_allclose(calculate_population_center(population), [4, 7])
    np.testing.assert_allclose(update_best_elephant(np.array([4, 7]), 0.2), [0.8, 1.4])
    np.testing.assert_allclose(
        update_regular_elephant(population[0], population[1], 0.5, np.array([0.5, 1])),
        [3, 7],
    )


def test_separation_preserves_plus_one_and_overshoot():
    result = separate_worst_elephant(np.array([-1, 0]), np.array([1, 2]), np.array([0.9, 0]))
    np.testing.assert_allclose(result, [1.7, 0])


def test_generation_uses_old_population_and_explicit_draws():
    config = EHOConfig(population_size=3, dimension=1, lower_bounds=-1, upper_bounds=1)
    population = np.array([[0.4], [-0.8], [0.8]])
    result, center, draws = update_population(
        population, population[0], 0, 2, config, None, random_values=[[0], [0.5], [0.9]],
    )
    np.testing.assert_allclose(result[:, 0], [0.4 / 30, -0.5, 1.7])
    np.testing.assert_allclose(center, [0.4 / 3])
    np.testing.assert_allclose(draws[:, 0], [np.nan, 0.5, 0.9])
    np.testing.assert_allclose(population[:, 0], [0.4, -0.8, 0.8])


def test_book_replay_all_printed_values():
    _, best, worst, rows = verify_book_example()
    assert (best, worst) == (2, 1)
    assert len(rows) == 26
    assert all(row["status"] == "MATCH" for row in rows), rows


def test_tie_prefers_first_and_matriarch_precedes_separation():
    config = EHOConfig(dimension=1, population_size=2, max_generations=1)
    result = ElephantHerdingOptimizer(lambda position: 1, config).run(
        initial_population=[[2], [4]], save_population=True,
    )
    before, after = result.population_history
    assert before.best_index == before.worst_index == 0
    assert after.population[0, 0] == pytest.approx(0.3)
    assert np.isnan(after.random_values[0, 0])
    assert after.leader_index == 0
    assert result.best_position[0] == 2


def test_listing_retains_leader_index_when_current_best_changes():
    config = EHOConfig(dimension=1, population_size=3, alpha=0, beta=1, max_generations=2)
    objective = iter([0, 1, 2, 2, 1, 3, 2, 1, 3])
    result = ElephantHerdingOptimizer(lambda position: next(objective), config).run(
        initial_population=[[0], [2], [3]], save_population=True,
    )
    middle, final = result.population_history[1:]
    assert middle.best_index == 1 and middle.leader_index == 0
    assert final.population[0, 0] == pytest.approx(middle.population.mean())
    np.testing.assert_equal(result.best_position, [0])


def test_reproducibility_and_metrics():
    calls = []

    def objective(position):
        calls.append(position)
        return rastrigin(position)

    config = EHOConfig(max_generations=10, lower_bounds=-0.2, upper_bounds=0.2)
    first = ElephantHerdingOptimizer(objective, config).run(save_population=True)
    second = ElephantHerdingOptimizer(rastrigin, config).run()
    assert first.total_evaluations == len(calls) == 55
    assert first.evaluation_history == list(range(5, 56, 5))
    assert len(first.population_history) == 11
    assert second.population_history == ()
    assert np.all(np.diff(first.best_fitness_history) <= 0)
    assert first.violating_coordinates > 0
    for snapshot, row in zip(first.population_history, first.history):
        mask = (snapshot.population < -0.2) | (snapshot.population > 0.2)
        assert row.violating_coordinates == mask.sum()
        assert row.violating_individuals == mask.any(axis=1).sum()
        assert row.mean_fitness == snapshot.fitness.mean()
    np.testing.assert_array_equal(first.best_position, second.best_position)
    assert first.best_fitness_history == second.best_fitness_history
    np.testing.assert_array_equal(first.final_population, second.final_population)


def test_stop_keeps_complete_generations():
    result = ElephantHerdingOptimizer(rastrigin, EHOConfig()).run(should_stop=lambda: True)
    assert result.completed_generations == 0
    assert result.total_evaluations == 5
    assert result.termination_reason == "stopped"


@pytest.mark.parametrize("value", [np.nan, np.inf, [1], 1j])
def test_reject_invalid_objective_result(value):
    with pytest.raises(ValueError):
        ElephantHerdingOptimizer(lambda position: value, EHOConfig()).run()
