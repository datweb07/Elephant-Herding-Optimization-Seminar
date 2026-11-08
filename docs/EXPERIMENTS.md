# Thiết kế thực nghiệm

| Notebook | Nội dung |
|---|---|
| 00_Book_Reproduction | Tái tính từng bước có đủ dữ liệu, so sánh Book Value / Python Value |
| Experiment 1-2 | Alpha, beta, quần thể, số thế hệ, số chiều, lưới tương tác alpha–beta |
| Experiment 3 | Phân bố và độ ổn định với 2, 4, 8, 12 chiều |
| Experiment 4 | Rastrigin nhiều chiều, máy bơm, chuyển cấu hình, độ vượt cận |

Cài repo editable và dùng kernel của môi trường đó. Mỗi notebook chạy độc lập từ đầu.
QUICK dùng seed 11, 23, 37, 53, 71. FULL dùng 101–125. Chọn bằng biến môi trường
`EHO_EXPERIMENT_MODE=FULL` trước khi mở kernel hoặc sửa biến `MODE` trong notebook.
Book Reproduction có đầu vào cố định.

Đặt `EHO_SAVE_RESULTS=1` trước khi mở kernel để lưu kết quả theo mục vào
`outputs/quick/` hoặc `outputs/full/`. Mỗi mục có `runs.csv` chứa từng seed và cấu hình,
`summary.csv`, `metadata.json` và các hình PNG. Experiment 4 ghi cả chi phí bơm và chênh lệch
fitness từng seed so với mốc lưới. Các tệp này được lưu cục bộ.

Cấu hình cơ sở của các sweep là P=20, d=4, G=50, alpha=0,5, beta=0,1, cận ±5,12.
Thí nghiệm ghi rõ tham số thay đổi. Nhóm quần thể có hai so sánh, cùng 50 thế hệ và cùng đúng
1.200 đánh giá. Evaluations bao gồm quần thể khởi tạo. Số liệu lấy từ lời gọi objective thật.

Bảng thống kê giữ toàn bộ seed và dùng SD, variance mẫu (ddof=1). Đường hội tụ hiển thị mean
best lịch sử với dải ±1 SD, dải này mô tả phân tán mẫu. Sai số của Rastrigin là khoảng cách
tuyệt đối đến 0. Experiment 3 dùng ngưỡng 0,001 và tách tính khả thi của nghiệm. Runtime thay
đổi theo máy. Các số liệu mô tả cấu hình và seed đã chạy, đặc biệt khi so sánh bài toán có
chiều hoặc đơn vị fitness khác nhau.
