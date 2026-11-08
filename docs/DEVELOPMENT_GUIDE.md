# Hướng dẫn phát triển

`eho` chỉ phụ thuộc NumPy. Config chuẩn hóa cận. Operators tính toán từng nhánh và giữ ma trận
cũ tách khỏi ma trận mới. Optimizer gọi objective theo hàng, lưu best và lịch sử. GUI bọc core
qua QThread, gửi signal về main thread và gộp cập nhật biểu đồ theo thời gian. Notebook dùng runner
và plotting chung. Sample data được đọc từ thư mục repo khi cài editable.

Để bổ sung objective, viết callable nhận vector một chiều và trả về số thực hữu hạn.
Tạo `EHOConfig` với chiều và cận phù hợp rồi gọi `ElephantHerdingOptimizer(objective, config).run()`.
Giữ các quy tắc riêng của bài toán trong objective. Dùng `save_population=True` khi cần truy vết
đầy đủ và giới hạn kích thước chạy để kiểm soát bộ nhớ.

Dùng tên thể hiện ý nghĩa, ưu tiên hàm ngắn và lưu seed trong kết quả. Chạy `python -m pytest -q`
từ root. Kiểm thử Qt dùng offscreen. Thí nghiệm mới nên dùng cùng seed trong mỗi nhóm, công bố
ngân sách và chỉ so sánh các điểm cùng thang đo. Từ root có thể chạy:

```powershell
python -m nbconvert --execute --to notebook --output-dir outputs/quick/notebooks 'Experiment/*.ipynb'
```

Review thay đổi core dựa vào BOOK_ALIGNMENT, các công thức, tính đúng của bestloc, số lần gọi
objective và kết quả Book Replay. Chạy QUICK cho mọi notebook khi sửa runner hoặc core.
