import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QFormLayout, QHeaderView, QLabel, QPlainTextEdit, QSpinBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from objectives import rastrigin
from objectives.rastrigin import rastrigin_landscape


def vector(values):
    return np.array2string(np.asarray(values), precision=5, max_line_width=110)


class VisualizationPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.metrics = QLabel()
        self.metrics.setWordWrap(True)
        layout.addWidget(self.metrics)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        self.figure = Figure(layout="constrained")
        self.convergence, self.landscape = self.figure.subplots(1, 2)
        self.canvas = FigureCanvasQTAgg(self.figure)
        tabs.addTab(self.canvas, "Hội tụ và không gian nghiệm")
        inspection = QWidget()
        inspect_layout = QVBoxLayout(inspection)
        selection = QFormLayout()
        self.generation = QSpinBox()
        self.elephant = QSpinBox()
        self.elephant.setMinimum(1)
        selection.addRow("Thế hệ", self.generation)
        selection.addRow("Cá thể", self.elephant)
        inspect_layout.addLayout(selection)
        self.population = self.population_table()
        self.previous_population = self.population_table()
        populations = QTabWidget()
        populations.addTab(self.population, "Quần thể đã chọn")
        populations.addTab(self.previous_population, "Quần thể trước cập nhật")
        inspect_layout.addWidget(populations)
        self.trace = QPlainTextEdit()
        self.trace.setReadOnly(True)
        inspect_layout.addWidget(self.trace)
        tabs.addTab(inspection, "Generation Inspector")
        self.generation.valueChanged.connect(self.select_generation)
        self.elephant.valueChanged.connect(self.show_trace)
        self.clear()

    @staticmethod
    def population_table():
        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Cá thể", "Vị trí", "Fitness", "Vai trò"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def clear(self):
        self.result = self.config = self.objective = self.snapshot = None
        self.rows = []
        self.landscape_grid = None
        self.metrics.setText("Chọn tham số và bấm Start để theo dõi một lần chạy.")
        self.generation.setEnabled(False)
        self.elephant.setEnabled(False)
        self.population.setRowCount(0)
        self.previous_population.setRowCount(0)
        self.trace.clear()
        self.convergence.clear()
        self.landscape.clear()
        self.convergence.set_title("Hội tụ")
        self.landscape.set_title("Không gian nghiệm")
        self.canvas.draw_idle()

    def begin(self, config, objective):
        self.clear()
        self.config, self.objective = config, objective
        if objective is rastrigin and config.dimension == 2:
            xs = np.linspace(config.lower_bounds[0], config.upper_bounds[0], 90)
            ys = np.linspace(config.lower_bounds[1], config.upper_bounds[1], 90)
            grid_x, grid_y = np.meshgrid(xs, ys)
            self.landscape_grid = grid_x, grid_y, rastrigin_landscape(np.stack([grid_x, grid_y], axis=-1))

    def update_progress(self, row, snapshot):
        self.rows.append(row)
        self.render(row, snapshot)

    def finish(self, result):
        self.result = result
        self.rows = result.history
        with QSignalBlocker(self.generation):
            self.generation.setRange(0, result.completed_generations)
            self.generation.setValue(result.completed_generations)
        self.generation.setEnabled(bool(result.population_history))
        if result.population_history:
            self.select_generation(result.completed_generations)
        else:
            self.trace.setPlainText("Lần chạy lớn. Lịch sử chi tiết đã tắt để giới hạn bộ nhớ.")
            self.render(result.history[-1], self.snapshot, result.final_population, result.best_position)

    def select_generation(self, index):
        if self.result and self.result.population_history:
            self.render(self.rows[index], self.result.population_history[index])
            if index:
                previous = self.result.population_history[index - 1]
                self.fill_population(self.previous_population, previous.population, previous.fitness, previous)
            else:
                self.previous_population.setRowCount(0)

    def render(self, row, snapshot, final_population=None, final_best=None):
        self.snapshot = snapshot
        self.metrics.setText(
            f"Thế hệ {row.number}/{self.config.max_generations}  ·  Best lịch sử {row.best_fitness:.6g}  ·  "
            f"Best hiện tại {row.current_best:.6g}  ·  Mean {row.mean_fitness:.6g}  ·  Worst {row.worst_fitness:.6g}\n"
            f"Đánh giá {row.evaluations:,}  ·  {row.elapsed:.3f} s  ·  "
            f"Vượt cận {row.violating_individuals} cá thể / {row.violating_coordinates} tọa độ"
        )
        self.metrics.setStyleSheet("color: #a34406;" if row.violating_coordinates else "")
        axis = self.convergence
        axis.clear()
        numbers = [item.number for item in self.rows]
        for attribute, label in (("best_fitness", "Best lịch sử"), ("mean_fitness", "Trung bình"),
                                 ("current_best", "Best hiện tại")):
            axis.plot(numbers, [getattr(item, attribute) for item in self.rows], label=label)
        axis.axvline(row.number, color="#64748b", alpha=0.35)
        axis.set(xlabel="Thế hệ", ylabel="Fitness", title="Hội tụ")
        axis.legend(loc="best")
        axis.grid(alpha=0.15)
        population = final_population if final_population is not None else snapshot.population
        best_position = final_best if final_best is not None else snapshot.best_position
        self.draw_landscape(row, population, best_position)
        if final_population is not None:
            self.fill_population(self.population, final_population, self.result.final_fitness_values)
        elif snapshot is not None:
            self.fill_population(self.population, population, snapshot.fitness, snapshot)
            self.show_trace()
        with QSignalBlocker(self.elephant):
            self.elephant.setMaximum(len(population))
        self.elephant.setEnabled(bool(self.result and self.result.population_history))
        self.canvas.draw_idle()

    def draw_landscape(self, row, population, best):
        axis = self.landscape
        axis.clear()
        dimension = self.config.dimension
        horizontal, vertical = population[:, 0], np.zeros(len(population))
        best_vertical = 0
        if dimension >= 2:
            vertical, best_vertical = population[:, 1], best[1]
        title = "Phân bố một chiều"
        if self.landscape_grid is not None:
            axis.contourf(*self.landscape_grid, levels=20, cmap="Blues", alpha=0.72)
            title = "Rastrigin 2D · Contour"
        elif dimension > 2:
            title = f"Chiếu tọa độ 1–2 từ {dimension}D"
        elif dimension == 2:
            title = "Phân bố lưu lượng máy bơm"
        if self.result and self.result.population_history and row.number > 0 and dimension == 2:
            previous = self.result.population_history[row.number - 1].population
            for old, new in zip(previous[:100], population[:100]):
                axis.plot([old[0], new[0]], [old[1], new[1]], color="#64748b", alpha=0.25)
        axis.scatter(horizontal, vertical, color="#df7333", s=23, label="Cá thể")
        axis.scatter([best[0]], [best_vertical], marker="*", s=125, color="#16825b", label="Best lịch sử")
        axis.set(xlabel="Tọa độ 1", title=title)
        if dimension >= 2:
            axis.set_ylabel("Tọa độ 2")
        else:
            axis.set_yticks([])
        axis.legend(loc="best")

    @staticmethod
    def fill_population(table, population, fitness, snapshot=None):
        table.setRowCount(len(population))
        best, worst = int(np.argmin(fitness)), int(np.argmax(fitness))
        for index, position in enumerate(population):
            roles = []
            if index == best:
                roles.append("Best")
            if index == worst:
                roles.append("Worst")
            if snapshot and index == snapshot.leader_index:
                roles.append("Đầu đàn")
            for column, value in enumerate((str(index + 1), vector(position),
                                             f"{fitness[index]:.6g}", " / ".join(roles) or "Regular")):
                table.setItem(index, column, QTableWidgetItem(value))

    def show_trace(self):
        if not self.result or not self.result.population_history:
            return
        number = self.generation.value()
        current = self.result.population_history[number]
        index = self.elephant.value() - 1
        if number == 0:
            self.trace.setPlainText("Thế hệ 0 là quần thể khởi tạo. Chọn thế hệ từ 1 để xem phép cập nhật.")
            return
        old = self.result.population_history[number - 1]
        draws = current.random_values[index]
        detail = (f"Cũ {vector(old.population[index])}  ·  Fitness {old.fitness[index]:.6g}\n"
                  f"Best cũ #{old.best_index + 1}  ·  Worst cũ #{old.worst_index + 1}  ·  "
                  f"Hàng đầu đàn #{old.leader_index + 1}\n"
                  f"Tâm quần thể cũ {vector(current.center_before)}\n")
        if index == old.leader_index:
            detail += f"(12.2) β × tâm, với β = {self.config.beta}\n"
        elif index == old.worst_index:
            detail += (f"(12.4) LB + r × (UB − LB + 1), với r = {vector(draws)}\n"
                       f"LB {vector(self.config.lower_bounds)}  ·  UB {vector(self.config.upper_bounds)}\n")
        else:
            detail += (f"(12.1) x + α × (best lịch sử − x) × r, với α = {self.config.alpha}\n"
                       f"Best lịch sử cũ {vector(old.best_position)}  ·  r {vector(draws)}\n")
        detail += (f"Mới {vector(current.population[index])}  ·  Fitness {current.fitness[index]:.6g}\n"
                   f"Best lịch sử sau cập nhật {vector(current.best_position)}")
        self.trace.setPlainText(detail)
