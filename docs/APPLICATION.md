# Application — Kế hoạch demo

## A. Kiểm chứng bắt buộc: Rastrigin (§12.5)

- Hàm mục tiêu: `f(x) = 10*d + sum(x_i**2 - 10*cos(2*pi*x_i))`.
- Miền giá trị: mỗi biến trong `[-5.12, 5.12]`.
- Dữ liệu ví dụ sách: `dimension = 4`, `population_size = 5`, `alpha = 0.5`, `beta = 0.1`.
- Kết quả hiển thị: nghiệm khởi tạo, fitness từng nghiệm, best/worst, các vị trí sau một vòng, lịch sử best và mean fitness.
- Kiểm thử khớp các giá trị **làm tròn** trong sách khi nạp đúng các biến ngẫu nhiên của ví dụ; không giả định seed Python khôi phục cùng dãy ngẫu nhiên.

## B. Ứng dụng minh họa: phân bổ công suất giữa hai máy bơm

**Mục đích:** Chọn hai mức vận hành liên tục sao cho tổng lưu lượng đáp ứng nhu cầu đặt ra, trong khi chi phí năng lượng thấp.

**Trạng thái:** Đây là phương án kịch bản để nhóm phát triển **sau khi** kiểm chứng Rastrigin; chưa có mô hình thực nghiệm hoặc số liệu vận hành thực tế.

Các quyết định cần chốt và mô tả trước khi code:

1. Hai biến đầu vào, đơn vị tính và miền giá trị khả thi.
2. Một hàm mục tiêu có thể tính từ hai biến, gồm chi phí năng lượng và phần phạt thiếu lưu lượng nếu cần.
3. Bộ tham số giả lập và lý do lựa chọn; các điều kiện ràng buộc.
4. Cách diễn giải kết quả EHO dưới góc nhìn vận hành.
5. Kiểm tra không nhầm kết quả của tình huống giả lập thành số liệu thực tế.

**Giới hạn:** EHO trong sách có toán tử tách voi với `+1` có thể tạo giá trị vượt cận. Phải nêu rõ vấn đề và kiểm tra miền nghiệm; không âm thầm điều chỉnh thuật toán bản gốc chỉ để kết quả ứng dụng trông hợp lệ.
