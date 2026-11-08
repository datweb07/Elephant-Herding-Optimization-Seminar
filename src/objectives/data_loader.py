import csv
import json
from dataclasses import fields
from pathlib import Path

import numpy as np

from .pump_allocation import PumpScenario


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_pump_scenarios(path=None):
    """Đọc CSV giả lập, kiểm tra schema, kiểu dữ liệu và tên trùng."""
    path = DATA_DIR / "pump_scenarios.csv" if path is None else Path(path)
    names = [field.name for field in fields(PumpScenario)]
    scenarios = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if sorted(reader.fieldnames or []) != sorted(names):
            raise ValueError("CSV máy bơm không đúng danh sách cột.")
        for row in reader:
            try:
                if None in row:
                    raise ValueError("Thừa giá trị.")
                name = row["scenario_name"].strip()
                scenario = PumpScenario(name, **{key: float(row[key]) for key in names[1:]})
                if name in scenarios:
                    raise ValueError("Tên kịch bản trùng.")
            except (ValueError, TypeError, AttributeError) as error:
                raise ValueError(f"CSV dòng {reader.line_num}: {error}") from error
            scenarios[name] = scenario
    if not scenarios:
        raise ValueError("CSV cần ít nhất một kịch bản.")
    return scenarios


def load_book_example(path=None):
    """Đọc các giá trị in ở §12.5, giữ riêng dữ liệu và kết quả tham chiếu."""
    path = DATA_DIR / "reference" / "rastrigin_book_example.json" if path is None else Path(path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    try:
        shapes = {
            "initial_population": (5, 4), "updated_population": (5, 4),
            "initial_fitness": (5,), "updated_fitness": (5,), "center": (4,),
            "regular_random": (4,), "separation_random": (4,),
            "alpha": (), "beta": (), "lower": (), "upper": (),
        }
        for key, shape in shapes.items():
            value = np.asarray(data[key], dtype=float)
            if value.shape != shape or not np.isfinite(value).all():
                raise ValueError(f"{key} sai kích thước hoặc có giá trị không hữu hạn.")
        if not data["lower"] < data["upper"]:
            raise ValueError("Cận của ví dụ sách không hợp lệ.")
        for key in ("regular_random", "separation_random", "alpha", "beta"):
            values = np.asarray(data[key], dtype=float)
            if np.any((values < 0) | (values > 1)):
                raise ValueError(f"{key} phải thuộc [0, 1].")
    except (TypeError, KeyError) as error:
        raise ValueError(f"Dữ liệu ví dụ sách không hợp lệ: {error}") from error
    return data
