# Phân bổ lưu lượng hai máy bơm

Một trạm bơm giả lập cần đáp ứng lưu lượng D với chi phí vận hành thấp. Hai mức lưu lượng
liên tục q₁, q₂ tính bằng m³/h phù hợp với vector đầu vào của EHO. Giới hạn từng bơm là
0 đến Q₁,max hoặc Q₂,max. Nhu cầu được mô hình hóa mềm, qua mức thiếu và dư.

- Năng lượng mô phỏng là `a1*q1² + b1*q1 + a2*q2² + b2*q2`.
- Thiếu là `max(0, D − q1 − q2)`, dư là `max(0, q1 + q2 − D)`.
- Phạt lưu lượng là `lambda_s*thiếu² + lambda_e*dư²`.
- Phạt cận là `lambda_b * sum(max(0, −qi)² + max(0, qi − Ui)²)`.
- Fitness là tổng năng lượng, phạt lưu lượng và phạt cận.

Ba kịch bản Low, Normal và Peak có nhu cầu 35, 70 và 105 m³/h. Công suất tối đa lần lượt
65 và 55 m³/h. Hệ số được giả định để minh họa sự đánh đổi giữa chi phí và nhu cầu.
Hàm mục tiêu có thể đánh giá cả điểm vượt cận, sau đó GUI báo cờ trong cận, độ thiếu/dư và từng
thành phần chi phí. Cờ trong cận chỉ phản ánh giới hạn công suất. Mức đáp ứng nhu cầu đọc từ
tổng lưu lượng và độ thiếu/dư.

Chọn Pump Allocation và kịch bản ở form. GUI đặt số chiều bằng 2 và nạp cận từ CSV.
Experiment 4 đối chiếu với lưới đều 81 × 81 trong cận. Đây là mốc trên tập điểm hữu hạn.
Cực tiểu liên tục có thể nằm giữa hai điểm lưới. Mô hình mô phỏng không có đường đặc tính,
áp suất, lịch bật tắt hoặc hiệu suất theo điểm vận hành.
