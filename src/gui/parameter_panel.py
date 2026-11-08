from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QLineEdit, QSpinBox,
)

from eho import EHOConfig
from objectives import rastrigin


class ParameterPanel(QGroupBox):
    def __init__(self, scenarios):
        super().__init__("Cấu hình lần chạy")
        self.scenarios = scenarios
        form = QFormLayout(self)
        self.objective = QComboBox()
        self.objective.addItems(["Rastrigin", "Pump Allocation"])
        self.scenario = QComboBox()
        self.scenario.addItems(list(scenarios))
        self.scenario.setCurrentText("Normal Demand")
        form.addRow("Hàm mục tiêu", self.objective)
        form.addRow("Kịch bản giả lập", self.scenario)
        self.population = self.spin(form, "Số cá thể", 2, 1000, 5)
        self.dimension = self.spin(form, "Số chiều", 1, 100, 4)
        self.alpha = self.spin(form, "Alpha", 0, 1, 0.5)
        self.beta = self.spin(form, "Beta", 0, 1, 0.1)
        self.generations = self.spin(form, "Số thế hệ", 1, 10000, 50)
        self.lower = self.spin(form, "Cận dưới", -100000, 100000, -5.12)
        self.upper = self.spin(form, "Cận trên", -100000, 100000, 5.12)
        self.seed = QLineEdit("42")
        form.addRow("Seed", self.seed)
        self.objective.currentIndexChanged.connect(self.refresh_fields)
        self.refresh_fields()

    @staticmethod
    def spin(form, label, lower, upper, value):
        if isinstance(value, float):
            control = QDoubleSpinBox()
            control.setDecimals(4)
            control.setSingleStep(0.05)
        else:
            control = QSpinBox()
        control.setRange(lower, upper)
        control.setValue(value)
        form.addRow(label, control)
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
