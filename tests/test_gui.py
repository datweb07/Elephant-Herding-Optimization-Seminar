import csv
import json
from time import monotonic

import pytest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.results_panel import export_result


@pytest.fixture
def window(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    demo = MainWindow()
    demo.show()
    yield demo
    if demo.worker is not None:
        demo.stop_run()
        assert demo.worker.wait(5000)
        app.processEvents()
    demo.close()


def wait_for_run(window):
    deadline = monotonic() + 10
    while window.worker is not None and monotonic() < deadline:
        QApplication.processEvents()
        QTest.qWait(5)
    assert window.worker is None


def click(button):
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def test_rastrigin_ui_export_and_reset(window, tmp_path):
    window.parameters.seed.setText("-2")
    click(window.start_button)
    assert window.worker is None
    assert "không hợp lệ" in window.statusBar().currentMessage()
    window.parameters.seed.setText("42")
    window.parameters.dimension.setValue(2)
    window.parameters.generations.setValue(4)
    click(window.start_button)
    wait_for_run(window)
    result = window.results.result
    assert result.total_evaluations == 25
    visualization = window.visualization
    assert len(visualization.convergence.lines[0].get_xdata()) == 5
    assert visualization.landscape_grid is not None
    visualization.generation.setValue(1)
    assert visualization.population.rowCount() == 5
    assert "Tâm quần thể cũ" in visualization.trace.toPlainText()

    csv_file, json_file = tmp_path / "history.csv", tmp_path / "result.json"
    export_result(csv_file, result, "Rastrigin")
    export_result(json_file, result, "Rastrigin")
    with csv_file.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert int(rows[-1]["evaluations"]) == 25
    assert json.loads(json_file.read_text(encoding="utf-8"))["best_fitness"] == result.best_fitness
    figure_file = tmp_path / "figure.png"
    visualization.figure.savefig(figure_file)
    assert figure_file.stat().st_size > 0

    click(window.reset_button)
    assert window.results.result is None
    assert visualization.population.rowCount() == 0


def test_stop_then_run_pump(window):
    window.parameters.generations.setValue(10000)
    click(window.start_button)
    click(window.stop_button)
    wait_for_run(window)
    assert window.results.result.termination_reason == "stopped"
    window.parameters.objective.setCurrentIndex(1)
    window.parameters.generations.setValue(5)
    click(window.start_button)
    wait_for_run(window)
    assert window.results.result.configuration.dimension == 2
    assert window.results.result.completed_generations == 5
    assert "Nghiệm EHO tốt nhất" in window.application.toPlainText()
