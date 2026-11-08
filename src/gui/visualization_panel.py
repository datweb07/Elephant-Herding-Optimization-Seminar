import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QFormLayout, QHBoxLayout, QHeaderView, QLabel, QPlainTextEdit, QPushButton, QSpinBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from objectives import rastrigin
from objectives.rastrigin import rastrigin_landscape
from .movement_plot import display_points, draw_movement, position_axes


def vector(values):
    return np.array2string(np.asarray(values), precision=5, max_line_width=110)


class VisualizationPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.metrics = QLabel()
        self.metrics.setWordWrap(True)
        layout.addWidget(self.metrics)
        generation_controls = QHBoxLayout()
        self.generation = QSpinBox()
        self.generation.setAccessibleName("Thế hệ đang xem")
        self.first_step = QPushButton("Bước đầu (0 → 1)")
        self.first_step.clicked.connect(self.select_first_step)
        generation_controls.addWidget(QLabel("Thế hệ đang xem"))
        generation_controls.addWidget(self.generation)
        generation_controls.addWidget(self.first_step)
        generation_controls.addStretch()
        layout.addLayout(generation_controls)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.figure = Figure(layout="constrained")
        self.convergence, self.landscape = self.figure.subplots(1, 2)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.tabs.addTab(self.canvas, "Hội tụ và không gian nghiệm")
        movement = QWidget()
        movement_layout = QVBoxLayout(movement)
        self.movement_caption = QLabel()
        self.movement_caption.setWordWrap(True)
        movement_layout.addWidget(self.movement_caption)
        self.movement_figure = Figure(layout="constrained")
        self.movement_axis = self.movement_figure.subplots()
        self.movement_canvas = FigureCanvasQTAgg(self.movement_figure)
        movement_layout.addWidget(self.movement_canvas, 1)
        self.tabs.addTab(movement, "Đàn voi di chuyển")
        inspection = QWidget()
        inspect_layout = QVBoxLayout(inspection)
        selection = QFormLayout()
        self.elephant = QSpinBox()
        self.elephant.setMinimum(1)
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
        self.tabs.addTab(inspection, "Generation Inspector")
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
        with QSignalBlocker(self.generation):
            self.generation.setRange(0, 0)
        self.first_step.setEnabled(False)
        self.elephant.setEnabled(False)
        self.population.setRowCount(0)
        self.previous_population.setRowCount(0)
        self.trace.clear()
        self.convergence.clear()
        self.landscape.clear()
        self.convergence.set_title("Hội tụ")
        self.landscape.set_title("Không gian nghiệm")
        self.clear_movement("Bấm Start để xem các bước cập nhật quần thể.")
        self.canvas.draw_idle()

    def clear_movement(self, message):
        self.movement_caption.setText(message)
        self.movement_axis.clear()
        self.movement_axis.set_axis_off()
        self.movement_canvas.draw_idle()

    def select_first_step(self):
        self.generation.setValue(1)
        self.tabs.setCurrentIndex(1)

    def begin(self, config, objective):
        self.clear()
        self.config, self.objective = config, objective
        if objective is rastrigin and config.dimension == 2:
            xs = np.linspace(config.lower_bounds[0], config.upper_bounds[0], 90)
            ys = np.linspace(config.lower_bounds[1], config.upper_bounds[1], 90)
            grid_x, grid_y = np.meshgrid(xs, ys)
            self.landscape_grid = grid_x, grid_y, rastrigin_landscape(np.stack([grid_x, grid_y], axis=-1))

    def update_progress(self, row, snapshot, previous):
        self.rows.append(row)
        with QSignalBlocker(self.generation):
            self.generation.setRange(0, row.number)
            self.generation.setValue(row.number)
        self.render(row, snapshot)
        self.render_movement(row.number, snapshot, previous)

    def finish(self, result):
        self.result = result
        self.rows = result.history
        with QSignalBlocker(self.generation):
            self.generation.setRange(0, result.completed_generations)
            self.generation.setValue(result.completed_generations)
        self.generation.setEnabled(bool(result.population_history))
        self.first_step.setEnabled(bool(result.population_history) and result.completed_generations > 0)
        if result.population_history:
            self.select_generation(result.completed_generations)
        else:
            self.trace.setPlainText("Lần chạy lớn. Lịch sử chi tiết đã tắt để giới hạn bộ nhớ.")
            self.render(result.history[-1], None, result.final_population, result.best_position)
            self.clear_movement("Lần chạy lớn: không lưu lịch sử để phát lại. Xem quần thể cuối ở tab hội tụ.")

    def select_generation(self, index):
        if self.result and self.result.population_history:
            current = self.result.population_history[index]
            self.render(self.rows[index], current)
            previous = None
            if index:
                previous = self.result.population_history[index - 1]
                self.fill_population(self.previous_population, previous.population, previous.fitness, previous)
            else:
                self.previous_population.setRowCount(0)
            self.render_movement(index, current, previous)

    def render_movement(self, number, current, previous):
        self.movement_axis.set_axis_on()
        draw_movement(self.movement_axis, self.config, current, previous, number,
                      pump=self.objective is not rastrigin)
        if previous is None:
            caption = "Thế hệ 0 cho thấy vị trí khởi tạo. Chọn bước 0 → 1 để xem ba toán tử."
        else:
            caption = ("Vòng rỗng là vị trí cũ, chấm đặc là vị trí mới. Mỗi mũi tên cho thấy một cá thể "
                       "đã đi từ đâu đến đâu. Dấu sao đánh dấu điểm tốt nhất tìm được trước bước này.")
            if previous.worst_index == previous.leader_index:
                caption += " Đầu đàn cũng là cá thể có điểm kém nhất, nên bước này dùng công thức đầu đàn cho nó."
        self.movement_caption.setText(caption)
        self.movement_canvas.draw_idle()

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
        self.draw_landscape(population, best_position)
        if final_population is not None:
            self.fill_population(self.population, final_population, self.result.final_fitness_values)
        elif snapshot is not None:
            self.fill_population(self.population, population, snapshot.fitness, snapshot)
            self.show_trace()
        with QSignalBlocker(self.elephant):
            self.elephant.setMaximum(len(population))
        self.elephant.setEnabled(bool(self.result and self.result.population_history))
        self.canvas.draw_idle()

    def draw_landscape(self, population, best):
        axis = self.landscape
        axis.clear()
        dimension = self.config.dimension
        title = "Phân bố một chiều"
        if self.landscape_grid is not None:
            axis.contour(*self.landscape_grid, levels=15, colors="0.75", linewidths=0.65)
            title = "Rastrigin 2D · Contour"
        elif dimension > 2:
            title = f"Chiếu tọa độ 1–2 từ {dimension}D"
        elif dimension == 2:
            title = "Phân bố lưu lượng máy bơm"
        axis.scatter(*display_points(population).T, color="0.25", s=23, label="Cá thể")
        axis.scatter(*display_points(best).T, marker="*", s=125, color="#245d80", label="Best lịch sử")
        axis.set_title(title)
        position_axes(axis, self.config, self.objective is not rastrigin)
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
