# Dữ liệu seminar

- `reference/rastrigin_book_example.json` chứa ma trận 5 × 4, alpha, beta, cận, tâm,
  fitness trước/sau và hai vector r in ở Chương 12, §12.5, tr. 158–160. Đọc UTF-8.
  Các trường fitness và tọa độ mới là dữ liệu đối chiếu. Ví dụ có đủ r cho x1, x2.
- `pump_scenarios.csv` chứa ba kịch bản **giả lập**. Cột `scenario_name` phải duy nhất.
  `demand` và `pump_*_max_flow` có đơn vị m³/h. Các cột `*_coefficient` mô tả chi phí
  giả định. Ba trọng số phạt là số dương. Nhu cầu nằm trong tổng công suất.

Loader mặc định giải đường dẫn từ mã nguồn, nên hoạt động độc lập với thư mục làm việc khi
cài editable. Có thể truyền đường dẫn riêng khi kiểm tra dữ liệu mới.
