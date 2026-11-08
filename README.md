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