# Elephant Herding Optimization (EHO) - AI Seminar

Seminar môn Trí tuệ nhân tạo về **Elephant Herding Optimization (EHO)** - thuật toán tối ưu hóa lấy cảm hứng từ hành vi tổ chức đàn voi. Mục tiêu là giải thích nguyên lý, mô hình toán học, sơ đồ khối, tái hiện ví dụ trong sách và xây dựng ứng dụng demo trực quan bằng Python.

## Cài đặt và chạy

Cần Python 3.11 trở lên. Mở PowerShell tại thư mục repo.

```powershell
python -m venv .venv-eho
.\.venv-eho\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-eho\Scripts\python.exe -m pip install -e .
.\.venv-eho\Scripts\python.exe -m pip check
.\.venv-eho\Scripts\python.exe main.py
.\.venv-eho\Scripts\python.exe -m pytest
.\.venv-eho\Scripts\python.exe -m notebook
```

Các lệnh dùng Python trong môi trường riêng. Nếu thấy xung đột với Streamlit hoặc TensorFlow,
kiểm tra `include-system-site-packages = false` trong `.venv-eho/pyvenv.cfg`.

## Thuật toán và demo

Mỗi cá thể là một nghiệm liên tục. EHO dùng best lịch sử và tâm quần thể để cập nhật đàn,
rồi dùng phép tách để lấy mẫu một vị trí khác. Bản Python giữ số hạng +1 của sách và báo
vượt cận khi phát sinh.

Mở **Visualization**, chọn Rastrigin 2D, bấm **Start** rồi **Bước đầu (0 → 1)**.
Tab **Đàn voi di chuyển** dùng mũi tên để ghép vị trí cũ và mới của cùng một cá thể.
Contour thể hiện độ cao của hàm mục tiêu, còn dấu sao thể hiện best lịch sử dùng để cập nhật.
**Generation Inspector** cho xem vị trí, fitness, vai trò, tâm và các số r thực dùng.
**Application** minh họa phân bổ lưu lượng hai máy bơm bằng dữ liệu giả lập.
**Results** xuất CSV, JSON và hình PNG. [Kịch bản demo 6 phút](docs/DEMO_GUIDE.md)

## Mã nguồn và thực nghiệm

```text
src/
  eho/                 Thuật toán NumPy
  objectives/          Rastrigin, máy bơm và kiểm chứng sách
  gui/                 PySide6 và Matplotlib
  experiment_helpers/  Điều phối, Pandas, thống kê và lưu kết quả
Experiment/            Bốn notebook Jupyter
data/                  Dữ liệu tham chiếu và dữ liệu giả lập
tests/                 Kiểm thử pytest
docs/                  Tài liệu seminar
```

Chọn kernel của `.venv-eho` và chạy từng notebook độc lập. QUICK dùng 5 seed.
FULL dùng 25 seed cố định. Đặt `EHO_SAVE_RESULTS=1` để lưu kết quả cục bộ.
[Thiết kế thực nghiệm](docs/EXPERIMENTS.md)

## Nguồn và nghiệm thu

N. K. Meena, J. Yang và A. Slowik, “Elephant Herding Optimization”, Chương 12,
tr. 149–162, trong *Swarm Intelligence Algorithms: A Tutorial*, CRC Press / Taylor & Francis.
Đã đối chiếu 26 giá trị trong dung sai. Sách thiếu các số r của x4 và x5.
Kết quả EHO phụ thuộc seed và ngân sách. Mốc lưới bơm là một mốc hữu hạn.
[Đối chiếu sách](docs/BOOK_ALIGNMENT.md)

- [Mô tả thuật toán](docs/ALGORITHM_DESCRIPTION.md), [sơ đồ khối](docs/FLOWCHART.md) và [ứng dụng](docs/APPLICATION.md)
- [Phân công bốn thành viên, nhóm trưởng Trương Thành Đạt](docs/TEAM_PLAN.md)
- [Hướng dẫn sử dụng](docs/USER_GUIDE.md), [checklist](docs/SEMINAR_CHECKLIST.md) và [báo cáo nghiệm thu](docs/FINAL_REVIEW.md)
