from dataclasses import dataclass
from numbers import Integral

import numpy as np


@dataclass(frozen=True)
class EHOConfig:
    population_size: int = 5
    dimension: int = 4
    alpha: float = 0.5
    beta: float = 0.1
    max_generations: int = 50
    lower_bounds: float | tuple[float, ...] = -5.12
    upper_bounds: float | tuple[float, ...] = 5.12
    random_seed: int | None = 42

    def __post_init__(self):
        """Chuẩn hóa cận vô hướng hoặc vector thành tuple bất biến."""
        for name, minimum in (("population_size", 2), ("dimension", 1), ("max_generations", 1)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
                raise ValueError(f"{name} phải là số nguyên từ {minimum} trở lên.")
            object.__setattr__(self, name, int(value))
        for name in ("alpha", "beta"):
            value = float(getattr(self, name))
            if not 0 <= value <= 1:
                raise ValueError(f"{name} phải thuộc [0, 1].")
            object.__setattr__(self, name, value)
        for name in ("lower_bounds", "upper_bounds"):
            values = np.asarray(getattr(self, name), dtype=float)
            if values.ndim == 0:
                values = np.full(self.dimension, values)
            if values.shape != (self.dimension,) or not np.isfinite(values).all():
                raise ValueError(f"{name} phải hữu hạn và có đúng {self.dimension} tọa độ.")
            object.__setattr__(self, name, tuple(values.tolist()))
        lower, upper = np.asarray(self.lower_bounds), np.asarray(self.upper_bounds)
        with np.errstate(over="ignore"):
            if np.any(lower >= upper) or not np.isfinite(upper - lower + 1).all():
                raise ValueError("Mỗi cận dưới phải nhỏ hơn cận trên và độ rộng phải hữu hạn.")
        seed = self.random_seed
        if seed is not None:
            if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
                raise ValueError("Seed phải là số nguyên không âm.")
            object.__setattr__(self, "random_seed", int(seed))
