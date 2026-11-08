import pytest

from objectives.data_loader import load_book_example, load_pump_scenarios


def test_sample_scenarios_and_cost():
    scenarios = load_pump_scenarios()
    assert set(scenarios) == {"Low Demand", "Normal Demand", "Peak Demand"}
    scenario = scenarios["Normal Demand"]
    at_demand = scenario.breakdown([40, 30])
    assert at_demand["within_capacity"]
    assert at_demand["objective"] == at_demand["energy"]
    assert scenario.breakdown([40, 29])["flow_penalty"] == scenario.shortage_penalty
    assert scenario.breakdown([40, 31])["flow_penalty"] == scenario.excess_penalty
    invalid = scenario.breakdown([66, -1])
    assert not invalid["within_capacity"]
    assert invalid["bounds_penalty"] == 2 * scenario.boundary_penalty


def test_data_loads_outside_repository(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert load_pump_scenarios()
    assert len(load_book_example()["initial_population"]) == 5


def test_reject_invalid_schema(tmp_path):
    bad = tmp_path / "pump.csv"
    bad.write_text("scenario_name,demand\nLow Demand,55")
    with pytest.raises(ValueError):
        load_pump_scenarios(bad)
