# Kịch bản demo EHO trong 6 phút

Mở `python main.py` bằng Python trong `.venv-eho`. Chuẩn bị sẵn notebook đã chạy và hình trong `outputs/full/` để trình chiếu khi cần.

| Thời gian | Thao tác | Điều cần giải thích |
|---|---|---|
| 0:00–0:40 | Mở **Overview** | Một cá thể là một nghiệm. Với Rastrigin 2D, mỗi nghiệm là một điểm có hai tọa độ. Mục tiêu là tìm điểm có fitness thấp. |
| 0:40–1:25 | Mở **Algorithm**, đối chiếu sơ đồ khối | Cập nhật đàn dùng best lịch sử và tâm cũ. Tách cá thể tạo vị trí mới từ cận và r. Phép tách giữ +1. |
| 1:25–2:10 | Mở **Book Example** | Chỉ vào cột sai lệch và dung sai. Phân biệt tọa độ tái tính được với fitness tính từ tọa độ in. Các số r của x4 và x5 thiếu trong sách. |
| 2:10–3:25 | Chọn **Rastrigin**, số chiều 2, 5 cá thể, α=0,5, β=0,1, 50 thế hệ, cận ±5,12, seed 42. Bấm **Start** và **Bước đầu (0 → 1)** | Vòng rỗng và chấm đặc là cùng một cá thể trước và sau bước. Mũi tên thường hướng các tọa độ về best lịch sử, mũi tên đầu đàn kết thúc tại β × tâm, mũi tên tách dẫn đến vị trí lấy mẫu mới. Xem thêm thế hệ cuối và đường hội tụ. |
| 3:25–4:15 | Mở **Generation Inspector**, chọn cùng thế hệ và lần lượt chọn cá thể thường, đầu đàn, worst | So sánh hai quần thể. Chỉ vào r, tâm, fitness và công thức thực dùng. Vai trò lấy từ thế hệ trước. |
| 4:15–5:20 | Chọn **Pump Allocation**, **Normal Demand**, 20 cá thể, 50 thế hệ, giữ α, β, seed. Bấm **Start**, rồi mở **Application** và **Results** | Tọa độ là lưu lượng hai bơm. Đọc thiếu/dư, cờ trong cận và từng khoản chi phí. Kết quả có thể xuất CSV, JSON hoặc PNG. |
| 5:20–6:00 | Mở bảng FULL về ngân sách đánh giá và mốc lưới bơm | Đọc mean, độ phân tán và chênh lệch với mốc lưới. Beta bằng 0 đưa đầu đàn về gốc trên Rastrigin, một tính chất riêng của benchmark. |

Nếu cửa sổ gặp lỗi trong buổi trình bày, dùng notebook Book Reproduction và các hình FULL. Có thể mở
[phần đối chiếu](BOOK_ALIGNMENT.md) và [sơ đồ khối](FLOWCHART.md) để giải thích các toán tử bằng ví dụ sách.
