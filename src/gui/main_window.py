import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QProgressBar, QPushButton,
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


OVERVIEW = """## EHO tìm nghiệm như thế nào?

Hãy hình dung bạn đang tìm chỗ thấp trên một bản đồ đồi núi. Mỗi con voi là
một điểm đang được thử. Độ cao tại điểm đó là **fitness**. Trong ví dụ này,
điểm càng thấp thì nghiệm càng tốt.

Ở mỗi bước, các cá thể thường tiến về phía điểm tốt nhất đã tìm thấy. Vị trí
của cá thể đầu đàn được tính từ tâm của cả nhóm. Cá thể kém nhất thường được
đặt ở một điểm mới để thử một vùng khác.

Để xem một bước thật, chọn **Rastrigin**, đặt **Số chiều = 2**, bấm **Start**
rồi chọn **Bước đầu (0 → 1)**. Trong hình, vòng rỗng là chỗ cũ, chấm đặc là
chỗ mới và mũi tên cho biết mỗi cá thể đã đổi vị trí ra sao.

Nguồn: N. K. Meena, J. Yang và A. Slowik, *Swarm Intelligence Algorithms: A Tutorial*,
Chương 12, tr. 149–162.
"""

ALGORITHM = """# Một thế hệ EHO

### Trước khi chạy

Chọn cách tính điểm (hàm mục tiêu), số cá thể, số tọa độ của mỗi điểm và khoảng
giá trị dùng để khởi tạo. Alpha (α) và beta (β) điều khiển cách đổi vị trí.
Seed giúp lặp lại cùng một lần chạy khi các thiết lập giống nhau.

### Khởi tạo và đánh giá

Mỗi tọa độ ban đầu được lấy theo LB + r × (UB − LB). LB là cận dưới, UB là
cận trên, còn r là số ngẫu nhiên từ 0 đến dưới 1. Tính fitness cho từng cá thể.
Trong quần thể hiện tại, điểm thấp nhất là best và điểm cao nhất là worst.
Nếu nhiều cá thể bằng điểm, lấy cá thể đứng trước trong bảng.

### Cập nhật quần thể

1. **(12.1) Cá thể thường.** x′ = x + α × (pbest − x) × r.
   Mỗi tọa độ tiến một đoạn từ vị trí cũ x về phía pbest, tức điểm tốt nhất
   đã tìm thấy từ đầu lần chạy. Độ dài đoạn này phụ thuộc vào α và r.
2. **(12.2–12.3) Đầu đàn.** x′ = β × tâm. Tính tâm bằng cách lấy trung bình
   từng tọa độ của các điểm cũ, rồi nhân kết quả với β.
3. **(12.4) Tách cá thể.** x′ = LB + r × (UB − LB + 1). Cá thể kém nhất
   nhận một vị trí mới từ công thức này. Số +1 có thể làm vị trí mới vượt cận trên.
   Nếu cá thể đó cũng giữ vai trò đầu đàn, dùng công thức đầu đàn.

### Kết thúc thế hệ

Tính điểm cho các vị trí mới. Nếu một điểm tốt hơn kỷ lục trước đó, lưu điểm
mới và dùng cá thể tìm ra nó làm đầu đàn cho bước sau. Nếu kỷ lục giữ nguyên,
hàng đầu đàn cũng giữ nguyên. Cá thể kém nhất được chọn lại sau mỗi bước.
Khi đủ số thế hệ hoặc bấm Stop, xem điểm tốt nhất đã tìm được trong Results.
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elephant Herding Optimization")
        self.resize(1200, 680)
        self.setMinimumSize(840, 580)
        self.worker = None
        self.active_objective = None
        self.close_pending = False
        scenarios = load_pump_scenarios()
        central = QWidget()
        self.setCentralWidget(central)
        shell = QVBoxLayout(central)
        shell.setContentsMargins(18, 16, 18, 12)
        shell.setSpacing(14)
        header = QFrame()
        header.setObjectName("hero")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        heading = QLabel("Elephant Herding Optimization")
        heading.setObjectName("title")
        subtitle = QLabel("Khám phá cách đàn voi tìm nghiệm tốt qua từng thế hệ")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(heading, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        shell.addWidget(header)
        body = QHBoxLayout()
        body.setSpacing(14)
        shell.addLayout(body, 1)

        controls = QWidget()
        controls.setObjectName("sidebar")
        controls.setMinimumWidth(235)
        control_layout = QVBoxLayout(controls)
        self.parameters = ParameterPanel(scenarios)
        control_layout.addWidget(self.parameters)
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        self.stop_button.setEnabled(False)
        buttons = QHBoxLayout()
        for button, slot in ((self.start_button, self.start_run), (self.stop_button, self.stop_run),
                             (self.reset_button, self.reset)):
            button.clicked.connect(slot)
            buttons.addWidget(button)
        control_layout.addLayout(buttons)
        control_layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(controls)
        scroll.setMaximumWidth(315)
        body.addWidget(scroll)

        self.tabs = QTabWidget()
        body.addWidget(self.tabs, 1)
        self.tabs.addTab(self.overview_page(), "Overview")
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
        self.status_tags = {}
        for key, value in (("state", "Sẵn sàng"), ("warning", "Cảnh báo: 0"),
                           ("best", "Best: —"), ("time", "Thời gian: —")):
            tag = QLabel(value)
            tag.setObjectName("statusTag")
            self.status_tags[key] = tag
            self.statusBar().addPermanentWidget(tag)
        self.statusBar().showMessage("Sẵn sàng")
        self.parameters.scenario.currentTextChanged.connect(self.show_application)
        self.show_application()

    @staticmethod
    def text_page(markdown):
        page = QTextBrowser()
        page.setMarkdown(markdown)
        return page

    @staticmethod
    def overview_page():
        page = QTextBrowser()
        page.setHtml("""<!doctype html><html><body style="font-family: 'Segoe UI'; color: #F8FAFC;">
<h2 style="color:#F8FAFC;">EHO tìm nghiệm như thế nào?</h2>
<p>Hãy hình dung bạn đang tìm chỗ thấp trên một bản đồ đồi núi. Mỗi con voi là
một điểm đang được thử. Độ cao tại điểm đó là <b>fitness</b>. Trong ví dụ này,
điểm càng thấp thì nghiệm càng tốt.</p>
<p>Ở mỗi bước, các cá thể thường tiến về phía điểm tốt nhất đã tìm thấy. Vị trí
của cá thể đầu đàn được tính từ tâm của cả nhóm. Cá thể kém nhất thường được
đặt ở một điểm mới để thử một vùng khác.</p>
<div style="background:#0F172A; border-left:3px solid #3B82F6; padding:10px 12px; margin:14px 0;">
<b style="color:#93C5FD;">Thử một bước thật</b><br>
Chọn <b>Rastrigin</b>, đặt <b>Số chiều = 2</b>, bấm <b>Start</b> rồi chọn
<b>Bước đầu (0 → 1)</b>. Vòng rỗng là chỗ cũ, chấm đặc là chỗ mới và mũi tên
cho biết mỗi cá thể đã đổi vị trí ra sao.</div>
<p style="color:#94A3B8;">Nguồn: N. K. Meena, J. Yang và A. Slowik,
<i>Swarm Intelligence Algorithms: A Tutorial</i>, Chương 12, tr. 149–162.</p>
</body></html>""")
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
        self.set_status_tags("Đang chạy", "Cảnh báo: 0", "Best: —", "Thời gian: —")
        self.set_busy(True)
        save_population = config.population_size * config.dimension * (config.max_generations + 1) <= 1_000_000
        self.worker = OptimizerWorker(ElephantHerdingOptimizer(objective, config), save_population, self)
        self.worker.progress.connect(self.report_progress)
        self.worker.succeeded.connect(self.present_result)
        self.worker.failed.connect(self.report_error)
        self.worker.finished.connect(self.release_worker)
        self.statusBar().showMessage("Đang chạy")
        self.worker.start()

    def report_progress(self, row, snapshot, previous):
        self.progress.setValue(row.number)
        self.visualization.update_progress(row, snapshot, previous)
        if self.worker and not self.worker.stop_requested.is_set():
            self.status_tags["best"].setText(f"Best: {row.best_fitness:.6g}")
            self.status_tags["time"].setText(f"Thời gian: {row.elapsed:.3f} s")

    def present_result(self, result):
        self.visualization.finish(result)
        self.progress.setValue(result.completed_generations)
        objective = self.active_objective
        scenario = objective if isinstance(objective, PumpScenario) else None
        name = f"Pump Allocation / {scenario.scenario_name}" if scenario else "Rastrigin"
        self.results.present(result, name, scenario)
        self.show_application()
        status = "Đã dừng" if result.termination_reason == "stopped" else "Hoàn tất"
        self.set_status_tags(status, f"Cảnh báo: {result.violating_coordinates}",
                             f"Best: {result.best_fitness:.6g}",
                             f"Thời gian: {result.execution_time_seconds:.3f} s")
        self.statusBar().showMessage("Kết quả lần chạy đã sẵn sàng")

    def report_error(self, message):
        self.status_tags["state"].setText("Lỗi")
        self.statusBar().showMessage(f"Lỗi chạy EHO · {message}")

    def set_status_tags(self, state, warning, best, elapsed):
        for key, value in (("state", state), ("warning", warning),
                           ("best", best), ("time", elapsed)):
            self.status_tags[key].setText(value)
        has_warning = warning != "Cảnh báo: 0"
        warning_tag = self.status_tags["warning"]
        warning_tag.setProperty("warning", has_warning)
        warning_tag.style().unpolish(warning_tag)
        warning_tag.style().polish(warning_tag)

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
        self.set_status_tags("Sẵn sàng", "Cảnh báo: 0", "Best: —", "Thời gian: —")
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
    palette = QPalette(QColor("#0F172A"), QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Window, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1E293B"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#263449"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1E293B"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563EB"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(palette)
    gui_dir = Path(__file__).parent
    stylesheet = (gui_dir / "styles.qss").read_text(encoding="utf-8")
    for icon in ("chevron-up.svg", "chevron-down.svg"):
        stylesheet = stylesheet.replace(f"icons/{icon}", (gui_dir / "icons" / icon).as_posix())
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    return app.exec()
