from dataclasses import dataclass, fields
from math import isfinite

import numpy as np


@dataclass(frozen=True)
class PumpScenario:
    scenario_name: str
    demand: float
    pump_1_max_flow: float
    pump_2_max_flow: float
    pump_1_quadratic_coefficient: float
    pump_1_linear_coefficient: float
    pump_2_quadratic_coefficient: float
    pump_2_linear_coefficient: float
    shortage_penalty: float
    excess_penalty: float
    boundary_penalty: float

    def __post_init__(self):
        if not self.scenario_name.strip():
            raise ValueError("Tên kịch bản không được rỗng.")
        for field in fields(self)[1:]:
            value = getattr(self, field.name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{field.name} phải hữu hạn và không âm.")
        if min(self.upper_bounds) <= 0 or not 0 < self.demand <= sum(self.upper_bounds):
            raise ValueError("Công suất phải dương và nhu cầu không được vượt tổng công suất.")
        if min(self.shortage_penalty, self.excess_penalty, self.boundary_penalty) <= 0:
            raise ValueError("Các trọng số phạt phải dương.")

    @property
    def upper_bounds(self):
        return self.pump_1_max_flow, self.pump_2_max_flow

    def breakdown(self, position):
        """Tách chi phí vận hành, phạt lưu lượng và phạt cận của nghiệm."""
        coordinates = np.asarray(position, dtype=float)
        if coordinates.shape != (2,) or not np.isfinite(coordinates).all():
            raise ValueError("Cần đúng hai lưu lượng hữu hạn.")
        flow_1, flow_2 = coordinates.tolist()
        total = flow_1 + flow_2
        shortage = max(0.0, self.demand - total)
        excess = max(0.0, total - self.demand)
        energy = (self.pump_1_quadratic_coefficient * flow_1 ** 2
                  + self.pump_1_linear_coefficient * flow_1
                  + self.pump_2_quadratic_coefficient * flow_2 ** 2
                  + self.pump_2_linear_coefficient * flow_2)
        flow_penalty = self.shortage_penalty * shortage ** 2 + self.excess_penalty * excess ** 2
        violations = np.maximum(0, -coordinates) + np.maximum(0, coordinates - self.upper_bounds)
        bounds_penalty = self.boundary_penalty * float(violations @ violations)
        return {
            "flow_1": flow_1, "flow_2": flow_2, "total_flow": total,
            "shortage": shortage, "excess": excess, "within_capacity": not bool(violations.any()),
            "energy": energy, "flow_penalty": flow_penalty, "bounds_penalty": bounds_penalty,
            "objective": energy + flow_penalty + bounds_penalty,
        }

    def __call__(self, position):
        return self.breakdown(position)["objective"]
