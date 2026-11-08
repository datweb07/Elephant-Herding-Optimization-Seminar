import csv
import json
import os
from time import monotonic

import pytest
import numpy as np
from PIL import Image
from matplotlib.quiver import Quiver

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QTableWidget

from gui.main_window import MainWindow


@pytest.fixture
def window(monkeypatch):
    if not os.getenv("QT_QPA_PLATFORM"):
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


def test_rastrigin_ui_export_and_reset(window, tmp_path, monkeypatch):
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
    click(visualization.first_step)
    assert visualization.tabs.currentIndex() == 1
    old, new = result.population_history[:2]
    arrows = [item for item in visualization.movement_axis.collections if isinstance(item, Quiver)]
    assert len(arrows) == 3
    for artist, index in zip(arrows[1:], (old.leader_index, old.worst_index), strict=True):
        np.testing.assert_allclose(artist.XY, old.population[[index]])
        np.testing.assert_allclose(np.column_stack((artist.U, artist.V)),
                                   new.population[[index]] - old.population[[index]])
    visualization.generation.setValue(0)
    assert visualization.previous_population.rowCount() == 0
    assert "khởi tạo" in visualization.trace.toPlainText()
    visualization.generation.setValue(1)
    assert visualization.population.rowCount() == 5
    assert visualization.previous_population.rowCount() == 5
    assert "Tâm quần thể cũ" in visualization.trace.toPlainText()
    for index, formula in ((old.leader_index, "12.2"), (old.worst_index, "12.4")):
        visualization.elephant.setValue(index + 1)
        assert formula in visualization.trace.toPlainText()
    regular = next(index for index in range(5) if index not in (old.leader_index, old.worst_index))
    visualization.elephant.setValue(regular + 1)
    assert "12.1" in visualization.trace.toPlainText()
    table = window.tabs.widget(3).findChild(QTableWidget)
    assert table.rowCount() == 26
    assert all(table.item(index, 5).text() == "MATCH" for index in range(26))

    window.tabs.setCurrentWidget(window.results)
    csv_file, json_file, figure_file = (tmp_path / name for name in ("history.csv", "result.json", "figure.png"))
    paths = iter((csv_file, json_file, figure_file))

    def choose_file(*_args):
        return str(next(paths)), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", choose_file)
    for button in window.results.buttons:
        click(button)
    with csv_file.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert int(rows[-1]["evaluations"]) == 25
    assert json.loads(json_file.read_text(encoding="utf-8"))["best_fitness"] == result.best_fitness
    with Image.open(figure_file) as figure:
        assert figure.format == "PNG"
        figure.verify()

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
    assert "bơm 1" in window.visualization.landscape.get_xlabel()


def test_projection_seed_and_close_during_run(window):
    window.resize(1366, 768)
    panel = window.parameters
    panel.population.setValue(2)
    panel.dimension.setValue(4)
    panel.alpha.setValue(0)
    panel.beta.setValue(1)
    panel.generations.setValue(3)
    panel.lower.setValue(5.12)
    click(window.start_button)
    assert window.worker is None
    assert "cận" in window.statusBar().currentMessage().lower()
    panel.lower.setValue(-5.12)
    click(window.start_button)
    wait_for_run(window)
    first = window.results.result
    assert "4 chiều" in window.visualization.movement_axis.get_title()
    assert window.visualization.landscape_grid is None
    click(window.reset_button)
    click(window.start_button)
    wait_for_run(window)
    np.testing.assert_array_equal(first.final_population, window.results.result.final_population)
    window.resize(1920, 1080)
    panel.seed.setText("43")
    panel.alpha.setValue(1)
    panel.beta.setValue(0)
    click(window.start_button)
    wait_for_run(window)
    assert window.results.result.random_seed == 43
    assert window.results.result.best_fitness == 0
    panel.generations.setValue(10000)
    click(window.start_button)
    window.close()
    wait_for_run(window)
    assert not window.isVisible()
