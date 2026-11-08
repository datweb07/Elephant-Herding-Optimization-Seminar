import csv
import json
from dataclasses import asdict
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from .visualization_panel import vector


def result_summary(result):
    position = result.best_position.tolist()
    config = result.configuration
    return {
        "configuration": asdict(config),
        "best_position": position,
        "best_in_bounds": all(
            lower <= value <= upper
            for value, lower, upper in zip(position, config.lower_bounds, config.upper_bounds, strict=True)
        ),
        "best_fitness": result.best_fitness,
        "initial_best_fitness": result.initial_best_fitness,
        "completed_generations": result.completed_generations,
        "total_evaluations": result.total_evaluations,
        "execution_time_seconds": result.execution_time_seconds,
        "violating_individuals": result.violating_individuals,
        "violating_coordinates": result.violating_coordinates,
        "termination_reason": result.termination_reason,
    }


def export_result(path, result, objective_name, scenario=None):
    """Xuất summary và lịch sử thật của lần chạy."""
    path = Path(path)
    history = [asdict(row) for row in result.history]
    if path.suffix.lower() == ".csv":
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(history[0]))
            writer.writeheader()
            writer.writerows(history)
    else:
        document = result_summary(result)
        document["objective"] = objective_name
        document["history"] = history
        document["final_population"] = result.final_population.tolist()
        document["final_fitness_values"] = result.final_fitness_values.tolist()
        if scenario is not None:
            document["scenario"] = asdict(scenario)
            document["pump_result"] = scenario.breakdown(result.best_position)
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


class ResultsPanel(QWidget):
    def __init__(self, figure):
        super().__init__()
        self.figure = figure
        layout = QVBoxLayout(self)
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        layout.addWidget(self.report)
        actions = QHBoxLayout()
        self.buttons = []
        for label, slot in (("Export CSV", self.save_csv), ("Export JSON", self.save_json),
                            ("Save Figure", self.save_figure)):
            button = QPushButton(label)
            button.clicked.connect(slot)
            self.buttons.append(button)
            actions.addWidget(button)
        actions.addStretch()
        layout.addLayout(actions)
        self.clear()

    def clear(self):
        self.result = None
        self.report.setPlainText("Kết quả xuất hiện khi lần chạy hoàn tất hoặc đã dừng.")
        for button in self.buttons:
            button.setEnabled(False)

    def present(self, result, objective_name, scenario):
        self.result, self.objective_name, self.scenario = result, objective_name, scenario
        config = result.configuration
        bounds_status = "Trong cận" if result_summary(result)["best_in_bounds"] else "Vượt cận"
        self.report.setPlainText(
            f"{objective_name}\n"
            f"{config.population_size} cá thể × {config.dimension} chiều · "
            f"α {config.alpha} · β {config.beta} · Seed {config.random_seed}\n"
            f"Cận dưới {vector(config.lower_bounds)}\nCận trên {vector(config.upper_bounds)}\n\n"
            f"Nghiệm tốt nhất {vector(result.best_position)}\n"
            f"Miền danh nghĩa của nghiệm tốt nhất {bounds_status}\n"
            f"Fitness tốt nhất {result.best_fitness:.8g}\n"
            f"Fitness tốt nhất ban đầu {result.initial_best_fitness:.8g}\n"
            f"Thế hệ hoàn tất {result.completed_generations}/{config.max_generations}\n"
            f"Lần đánh giá {result.total_evaluations:,}\n"
            f"Thời gian thuật toán {result.execution_time_seconds:.4f} s\n"
            f"Vượt cận cộng dồn {result.violating_individuals} cá thể, {result.violating_coordinates} tọa độ\n"
            f"Lý do kết thúc {result.termination_reason}"
        )
        for button in self.buttons:
            button.setEnabled(True)

    def save_csv(self):
        self.save(".csv", "CSV (*.csv)")

    def save_json(self):
        self.save(".json", "JSON (*.json)")

    def save_figure(self):
        self.save(".png", "PNG (*.png)")

    def save(self, suffix, file_filter):
        name, _ = QFileDialog.getSaveFileName(self, "Lưu kết quả", f"eho{suffix}", file_filter)
        if not name:
            return
        path = Path(name)
        if path.suffix.lower() != suffix:
            path = path.with_suffix(suffix)
        try:
            if suffix == ".png":
                self.figure.savefig(path, dpi=150)
            else:
                export_result(path, self.result, self.objective_name, self.scenario)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Lỗi xuất dữ liệu", str(error))
