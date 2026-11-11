from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QGridLayout, QGroupBox, QLabel, QLineEdit,
    QSpinBox, QVBoxLayout, QWidget,
)

from eho import EHOConfig
from objectives import rastrigin


class ParameterPanel(QWidget):
    def __init__(self, scenarios):
        super().__init__()
        self.scenarios = scenarios
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        problem, problem_grid = self.section("BÀI TOÁN")
        layout.addWidget(problem)
        self.objective = QComboBox()
        self.objective.addItems(["Rastrigin", "Pump Allocation"])
        self.scenario = QComboBox()
        self.scenario.addItems(list(scenarios))
        self.scenario.setCurrentText("Normal Demand")
        self.add_field(problem_grid, 0, 0, "Hàm mục tiêu", self.objective, span=2)
        self.add_field(problem_grid, 2, 0, "Kịch bản giả lập", self.scenario, span=2)
        self.lower = self.make_spin(-100000, 100000, -5.12)
        self.upper = self.make_spin(-100000, 100000, 5.12)
        self.add_field(problem_grid, 4, 0, "Cận dưới", self.lower)
        self.add_field(problem_grid, 4, 1, "Cận trên", self.upper)

        herd, herd_grid = self.section("THAM SỐ EHO")
        layout.addWidget(herd)
        self.population = self.make_spin(2, 1000, 5)
        self.dimension = self.make_spin(1, 100, 4)
        self.alpha = self.make_spin(0, 1, 0.5)
        self.beta = self.make_spin(0, 1, 0.1)
        self.add_field(herd_grid, 0, 0, "Số cá thể", self.population)
        self.add_field(herd_grid, 0, 1, "Số chiều", self.dimension)
        self.add_field(herd_grid, 2, 0, "Alpha (α)", self.alpha)
        self.add_field(herd_grid, 2, 1, "Beta (β)", self.beta)

        execution, execution_grid = self.section("ĐIỀU KIỆN CHẠY")
        layout.addWidget(execution)
        self.generations = self.make_spin(1, 10000, 50)
        self.seed = QLineEdit("42")
        self.add_field(execution_grid, 0, 0, "Số thế hệ", self.generations)
        self.add_field(execution_grid, 0, 1, "Seed", self.seed)
        layout.addStretch(1)
        self.objective.currentIndexChanged.connect(self.refresh_fields)
        self.refresh_fields()

    @staticmethod
    def section(title):
        group = QGroupBox(title)
        grid = QGridLayout(group)
        grid.setContentsMargins(10, 14, 10, 9)
        grid.setHorizontalSpacing(9)
        grid.setVerticalSpacing(3)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        return group, grid

    @staticmethod
    def add_field(grid, row, column, label_text, control, *, span=1):
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        grid.addWidget(label, row, column, 1, span)
        grid.addWidget(control, row + 1, column, 1, span)

    @staticmethod
    def make_spin(lower, upper, value):
        if isinstance(value, float):
            control = QDoubleSpinBox()
            control.setDecimals(4)
            control.setSingleStep(0.05)
        else:
            control = QSpinBox()
        control.setRange(lower, upper)
        control.setValue(value)
        return control

    def refresh_fields(self):
        pump = self.objective.currentIndex() == 1
        self.scenario.setEnabled(pump)
        for control in (self.dimension, self.lower, self.upper):
            control.setEnabled(not pump)

    def settings(self):
        try:
            seed = int(self.seed.text())
        except ValueError as error:
            raise ValueError("Seed phải là số nguyên không âm.") from error
        objective = rastrigin
        dimension = self.dimension.value()
        lower, upper = self.lower.value(), self.upper.value()
        if self.objective.currentIndex() == 1:
            objective = self.scenarios[self.scenario.currentText()]
            dimension, lower, upper = 2, 0, objective.upper_bounds
        config = EHOConfig(
            population_size=self.population.value(), dimension=dimension,
            alpha=self.alpha.value(), beta=self.beta.value(),
            max_generations=self.generations.value(), lower_bounds=lower, upper_bounds=upper,
            random_seed=seed,
        )
        return config, objective
