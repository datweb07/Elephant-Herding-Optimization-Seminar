import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QProgressBar, QPushButton,
    QScrollArea, QTabWidget, QTextBrowser, QVBoxLayout, QWidget,
)

from eho import ElephantHerdingOptimizer
from objectives.data_loader import load_pump_scenarios
from objectives.pump_allocation import PumpScenario

from .book_example_panel import BookExamplePanel
from .parameter_panel import ParameterPanel
from .results_panel import ResultsPanel
from .visualization_panel import VisualizationPanel
from .worker import OptimizerWorker


OVERVIEW = """# Elephant Herding Optimization

**AI Seminar · Swarm Intelligence · UEH**

EHO tìm nghiệm có fitness thấp bằng cách mô phỏng ảnh hưởng của voi đầu đàn và
việc voi đực trưởng thành rời đàn. Clan Updating kéo các nghiệm thường về phía
nghiệm tốt lịch sử và đặt hàng đầu đàn theo tâm. Separating tạo lại vị trí của hàng kém nhất.

- **Algorithm** giải thích công thức và vai trò của từng cá thể.
- **Visualization** theo dõi lần chạy Rastrigin hoặc phân bổ lưu lượng máy bơm.
- **Book Example** đối chiếu ví dụ tính tay §12.5.
- **Application** phân tích chi phí của một kịch bản máy bơm giả lập.
- **Results** xem và lưu dữ liệu lần chạy.

Nguồn: N. K. Meena, J. Yang và A. Slowik, *Swarm Intelligence Algorithms: A Tutorial*,
Chương 12, tr. 149–162.
"""

ALGORITHM = """# Một thế hệ EHO

### Đầu vào và đầu ra

Đầu vào gồm hàm mục tiêu, số cá thể, số chiều, cận từng chiều, α, β, số thế hệ và seed.
Đầu ra gồm nghiệm tốt nhất lịch sử, fitness, số đánh giá và chuỗi chỉ số theo thế hệ.

### Khởi tạo và đánh giá

Lấy mỗi tọa độ từ LB + r × (UB − LB), với r đồng đều trên [0,1).
Mỗi hàng là một nghiệm đầy đủ. Fitness nhỏ nhất là best hiện tại, lớn nhất là worst.
Khi bằng điểm, lấy hàng đầu tiên.

### Cập nhật quần thể

1. **(12.1) Cá thể thường.** x′ = x + α × (pbest − x) × r.
   x là hàng cũ, pbest là nghiệm tốt nhất lịch sử. α điều khiển lực kéo.
2. **(12.2–12.3) Đầu đàn.** x′ = β × tâm, với tâm là trung bình từng cột của quần thể cũ.
3. **(12.4) Tách cá thể.** x′ = LB + r × (UB − LB + 1), với LB và UB là cận tọa độ.
   Số hạng +1 có thể tạo nghiệm vượt cận. Giao diện đếm riêng số cá thể và số tọa độ.
   Khi hai vai trò cùng hàng, đầu đàn được ưu tiên.

### Kết thúc thế hệ

Đánh giá từng hàng mới. Chỉ đổi pbest, fitness kỷ lục và chỉ số hàng đầu đàn
khi có cải thiện nghiêm ngặt. Worst được chọn lại ở mỗi thế hệ.
Thay toàn bộ quần thể và ghi lịch sử. Trả nghiệm kỷ lục khi đủ thế hệ hoặc người dùng bấm Stop.
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elephant Herding Optimization · AI Seminar")
        self.resize(1400, 850)
        self.setMinimumSize(840, 580)
        self.worker = None
        self.active_objective = None
        self.close_pending = False
        scenarios = load_pump_scenarios()
        central = QWidget()
        self.setCentralWidget(central)
        shell = QVBoxLayout(central)
        heading = QLabel("Elephant Herding Optimization")
        heading.setObjectName("title")
        shell.addWidget(heading)
        shell.addWidget(QLabel("AI SEMINAR  /  SWARM INTELLIGENCE  /  UEH"))
        body = QHBoxLayout()
        shell.addLayout(body, 1)

        controls = QWidget()
        controls.setMinimumWidth(235)
        control_layout = QVBoxLayout(controls)
        self.parameters = ParameterPanel(scenarios)
        control_layout.addWidget(self.parameters)
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.stop_button.setEnabled(False)
        for button, slot in ((self.start_button, self.start_run), (self.stop_button, self.stop_run),
                             (self.reset_button, self.reset)):
            button.clicked.connect(slot)
            control_layout.addWidget(button)
        control_layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(controls)
        scroll.setMaximumWidth(315)
        body.addWidget(scroll)

        self.tabs = QTabWidget()
        body.addWidget(self.tabs, 1)
        self.tabs.addTab(self.text_page(OVERVIEW), "Overview")
        self.tabs.addTab(self.text_page(ALGORITHM), "Algorithm")
        self.visualization = VisualizationPanel()
        self.tabs.addTab(self.visualization, "Visualization")
        self.tabs.addTab(BookExamplePanel(), "Book Example")
        self.application = self.text_page("")
        self.tabs.addTab(self.application, "Application")
        self.results = ResultsPanel(self.visualization.figure)
        self.tabs.addTab(self.results, "Results")

        self.progress = QProgressBar()
        self.progress.setFormat("Thế hệ %v / %m")
        self.statusBar().addPermanentWidget(self.progress)
        self.statusBar().showMessage("Sẵn sàng")
        self.parameters.scenario.currentTextChanged.connect(self.show_application)
        self.show_application()

    @staticmethod
    def text_page(markdown):
        page = QTextBrowser()
        page.setMarkdown(markdown)
        return page

    def show_application(self, *_args):
        scenario = self.parameters.scenarios[self.parameters.scenario.currentText()]
        content = f"""# Phân bổ lưu lượng hai máy bơm

**Dữ liệu giả lập · {scenario.scenario_name}**

Nhu cầu **{scenario.demand:g} m³/h**. Công suất tối đa hai bơm lần lượt là
**{scenario.pump_1_max_flow:g}** và **{scenario.pump_2_max_flow:g} m³/h**.

Năng lượng mô phỏng dùng a × q² + b × q cho mỗi bơm.
(a₁, b₁) = ({scenario.pump_1_quadratic_coefficient:g}, {scenario.pump_1_linear_coefficient:g}).
(a₂, b₂) = ({scenario.pump_2_quadratic_coefficient:g}, {scenario.pump_2_linear_coefficient:g}).

Fitness = năng lượng + {scenario.shortage_penalty:g} × thiếu²
+ {scenario.excess_penalty:g} × dư²
+ {scenario.boundary_penalty:g} × tổng bình phương khoảng vượt cận.
"""
        result = self.results.result
        if result is not None and self.active_objective == scenario:
            values = scenario.breakdown(result.best_position)
            capacity = "Trong cận" if values["within_capacity"] else "Vượt cận"
            content += f"""
### Nghiệm EHO tốt nhất

- Bơm 1 **{values['flow_1']:.4f} m³/h**, bơm 2 **{values['flow_2']:.4f} m³/h**.
- Tổng **{values['total_flow']:.4f}**, thiếu **{values['shortage']:.4f}**, dư **{values['excess']:.4f} m³/h**.
- Giới hạn công suất **{capacity}**.
- Chi phí năng lượng **{values['energy']:.4f}**, phạt lưu lượng **{values['flow_penalty']:.4f}**,
  phạt cận **{values['bounds_penalty']:.4f}**, fitness tổng **{values['objective']:.4f}**.
"""
        else:
            content += "\nChọn Pump Allocation và bấm Start để tính nghiệm cho kịch bản này."
        self.application.setMarkdown(content)

    def set_busy(self, busy):
        self.parameters.setEnabled(not busy)
        self.start_button.setEnabled(not busy)
        self.stop_button.setEnabled(busy)
        self.reset_button.setEnabled(not busy)

    def start_run(self):
        if self.worker is not None:
            return
        try:
            config, objective = self.parameters.settings()
        except ValueError as error:
            self.statusBar().showMessage(f"Cấu hình không hợp lệ · {error}")
            return
        self.active_objective = objective
        self.results.clear()
        self.show_application()
        self.visualization.begin(config, objective)
        self.tabs.setCurrentWidget(self.visualization)
        self.progress.setRange(0, config.max_generations)
        self.progress.setValue(0)
        self.set_busy(True)
        save_population = config.population_size * config.dimension * (config.max_generations + 1) <= 1_000_000
        self.worker = OptimizerWorker(ElephantHerdingOptimizer(objective, config), save_population, self)
        self.worker.progress.connect(self.report_progress)
        self.worker.succeeded.connect(self.present_result)
        self.worker.failed.connect(self.report_error)
        self.worker.finished.connect(self.release_worker)
        self.statusBar().showMessage("Đang chạy")
        self.worker.start()

    def report_progress(self, row, snapshot):
        self.progress.setValue(row.number)
        self.visualization.update_progress(row, snapshot)
        if self.worker and not self.worker.stop_requested.is_set():
            self.statusBar().showMessage(f"Đang chạy · Best {row.best_fitness:.6g} · {row.elapsed:.3f} s")

    def present_result(self, result):
        self.visualization.finish(result)
        self.progress.setValue(result.completed_generations)
        objective = self.active_objective
        scenario = objective if isinstance(objective, PumpScenario) else None
        name = f"Pump Allocation / {scenario.scenario_name}" if scenario else "Rastrigin"
        self.results.present(result, name, scenario)
        self.show_application()
        status = "Đã dừng" if result.termination_reason == "stopped" else "Hoàn tất"
        if result.violating_coordinates:
            status += f" · Cảnh báo {result.violating_coordinates} lượt tọa độ vượt cận"
        self.statusBar().showMessage(f"{status} · Best {result.best_fitness:.6g} · {result.execution_time_seconds:.3f} s")

    def report_error(self, message):
        self.statusBar().showMessage(f"Lỗi chạy EHO · {message}")

    def release_worker(self):
        self.worker.deleteLater()
        self.worker = None
        self.set_busy(False)
        if self.close_pending:
            self.close()

    def stop_run(self):
        if self.worker is not None:
            self.worker.stop_requested.set()
            self.stop_button.setEnabled(False)
            self.statusBar().showMessage("Đang dừng sau thế hệ hiện tại…")

    def reset(self):
        self.visualization.clear()
        self.results.clear()
        self.active_objective = None
        self.show_application()
        self.progress.setValue(0)
        self.statusBar().showMessage("Sẵn sàng")

    def closeEvent(self, event):
        if self.worker is not None:
            self.close_pending = True
            self.stop_run()
            event.ignore()
        else:
            super().closeEvent(event)


def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(Path(__file__).with_name("styles.qss").read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    return app.exec()
