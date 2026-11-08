# Hướng dẫn sử dụng trên Windows

1. Cài Python 3.11 trở lên. Mở PowerShell tại repo và xác nhận `python --version`.
2. Chạy `python -m venv .venv-eho` rồi `.\.venv-eho\Scripts\Activate.ps1`. Nếu bị chặn,
   gọi trực tiếp `.\.venv-eho\Scripts\python.exe` ở các bước sau.
   Giữ `include-system-site-packages = false` trong `.venv-eho/pyvenv.cfg` để cô lập phụ thuộc.
3. Chạy `python -m pip install -r requirements.txt` và `python -m pip install -e .`.
4. Chạy `python main.py`. Chọn Rastrigin, giữ mặc định hoặc đặt số chiều bằng 2 để xem contour.
   Với Pump Allocation, chọn nhu cầu giả lập trong form. Cận được chọn từ kịch bản.
5. Nhập population, alpha, beta, số thế hệ và seed. Bấm Start. Lỗi cấu hình hiện ở thanh trạng thái.
   Stop yêu cầu dừng sau thế hệ đang chạy. Reset xóa kết quả và giữ các ô tham số để thử lại.
6. Đọc best lịch sử, best hiện tại, mean, worst, evaluations và cảnh báo cận trong Visualization.
   Vào Generation Inspector, chọn thế hệ và cá thể để xem công thức và các giá trị thực dùng.
   Nếu chạy vượt 1 triệu ô snapshot, biểu đồ và quần thể cuối vẫn có, lịch sử cá thể bị tắt.
7. Mở Book Example để đọc 26 so sánh và hai hàng chưa thể tái tạo r.
   Mở Application để xem lưu lượng, mức thiếu/dư và các chi phí trong lần chạy bơm.
8. Trong Results, Export CSV lưu lịch sử thế hệ. Export JSON lưu cấu hình, lịch sử và quần thể
   cuối. Save Figure lưu hình hiện tại. Dữ liệu của lần đã dừng vẫn có thể xuất.
9. Chạy `python -m notebook`, mở một file trong Experiment và chọn kernel của .venv-eho.
   Có thể đăng ký kernel bằng `python -m ipykernel install --user --name eho-seminar`,
   rồi chọn eho-seminar trong Jupyter hoặc VS Code. Chạy Run All từ ô đầu tiên.
