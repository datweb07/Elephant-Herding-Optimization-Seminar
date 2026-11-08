import numpy as np
from PySide6.QtWidgets import (
    QHeaderView, QLabel, QPlainTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from objectives.book_replay import verify_book_example


class BookExamplePanel(QWidget):
    def __init__(self):
        super().__init__()
        data, best, worst, rows = verify_book_example()
        layout = QVBoxLayout(self)
        matched = sum(row["status"] == "MATCH" for row in rows)
        heading = QLabel(
            f"§12.5 · {matched}/{len(rows)} giá trị MATCH trong dung sai · "
            "NOT FULLY REPRODUCIBLE cho toàn bộ chuỗi r của x4 và x5."
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)
        matrices = QPlainTextEdit()
        matrices.setReadOnly(True)
        matrices.setPlainText(
            f"Quần thể in ban đầu\n{np.asarray(data['initial_population'])}\n"
            f"Best x{best + 1} · Worst x{worst + 1} · α = {data['alpha']} · β = {data['beta']}\n\n"
            f"(12.1) x + α × (best − x) × r; r của x1 = {data['regular_random']}\n"
            "(12.2) β × tâm; (12.3) tâm = trung bình theo cột\n"
            f"(12.4) LB + r × (UB − LB + 1); r của x2 = {data['separation_random']}\n\n"
            f"Quần thể sau cập nhật được in trong sách\n{np.asarray(data['updated_population'])}\n"
            "Fitness mới được tính từ ma trận in ở trên. Dung sai phản ánh số chữ số in."
        )
        layout.addWidget(matrices)
        table = QTableWidget(len(rows), 6)
        table.setHorizontalHeaderLabels(["Đại lượng", "Book Value", "Python Value", "Δ", "Dung sai", "Trạng thái"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for index, row in enumerate(rows):
            for column, key in enumerate(("step", "book", "python", "delta", "tolerance", "status")):
                value = row[key]
                table.setItem(index, column, QTableWidgetItem(f"{value:.8g}" if isinstance(value, float) else value))
        layout.addWidget(table, 2)
