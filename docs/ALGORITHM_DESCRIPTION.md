# Algorithm Description — Bản thảo seminar

## 1. Nguồn gốc

EHO là thuật toán tối ưu hóa lấy cảm hứng từ đàn voi, các voi đầu đàn và việc voi đực trưởng thành rời đàn. Phần mô tả sinh học nằm ở §12.1, tr. 149–151.

## 2. Biểu diễn nghiệm

Đối với cách triển khai minh họa trong Listings 12.1–12.2, quần thể là một ma trận, mỗi hàng là một nghiệm có `dimension` biến liên tục và mỗi hàng được đánh giá bằng một giá trị objective function. Cần giải thích rõ sự khác nhau với mô tả nhiều clan ở phần lý thuyết.

## 3. Các bước chính

1. Nhập hàm mục tiêu, miền biến, kích thước quần thể, alpha, beta, số vòng lặp.
2. Khởi tạo ngẫu nhiên quần thể và đánh giá fitness.
3. Xác định nghiệm tốt nhất và kém nhất.
4. Áp dụng công thức (12.1) cho nghiệm thông thường.
5. Áp dụng công thức (12.2)–(12.3) cho nghiệm tốt nhất.
6. Áp dụng công thức (12.4) cho nghiệm kém nhất.
7. Tính lại fitness và cập nhật best lịch sử.
8. Lặp đến giới hạn số vòng lặp; trả về nghiệm tốt nhất.

## 4. Công thức bắt buộc

- (12.1): `p_new = p + alpha * (p_best - p) * random`
- (12.2): `p_best_new = beta * p_center`
- (12.3): `p_center = mean(population, axis=0)` trong biểu diễn ma trận mẫu
- (12.4): `p_worst_new = lower + random * (upper - lower + 1)` **(đúng theo sách)**

## 5. Cần bổ sung khi viết mã

Bảng tham số, số ví dụ tái hiện, ý nghĩa từng cột trong GUI và những trường hợp thuật toán không bảo đảm tìm được cực tiểu toàn cục.
