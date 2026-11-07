# Block Flow — Sơ đồ khối dự thảo EHO

Sơ đồ dưới đây là **bản phác thảo cho giai đoạn thiết kế**, sẽ phải kiểm tra lại từng nhánh với Algorithm 11 và mã mẫu trong Chương 12 trước khi nộp seminar.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Nhập hàm mục tiêu, alpha, beta, số vòng lặp và giới hạn biến]
    B --> C[Khởi tạo quần thể và đánh giá fitness]
    C --> D[Xác định nghiệm tốt nhất và kém nhất]
    D --> E{Đã đủ số vòng lặp?}
    E -- Chưa --> F[Đi qua từng nghiệm và từng chiều]
    F --> G{Phân loại nghiệm}
    G -- Thông thường --> H[Cập nhật theo phương trình 12.1]
    G -- Tốt nhất --> I[Cập nhật theo phương trình 12.2 và 12.3]
    G -- Kém nhất --> J[Tạo vị trí mới theo phương trình 12.4]
    H --> K[Đánh giá lại toàn bộ quần thể]
    I --> K
    J --> K
    K --> L[Cập nhật nghiệm tốt nhất lịch sử và quần thể]
    L --> M[Tăng bộ đếm vòng lặp]
    M --> E
    E -- Rồi --> N[Trả về nghiệm tốt nhất và dữ liệu biểu đồ]
    N --> O([Kết thúc])
```

### Ghi chú cho thuyết trình

- Nêu rõ phân biệt **best trong quần thể** và **best từ trước đến nay** khi diễn giải các listing.
- Giải thích công thức nào thuộc nhánh nào, không chỉ mô tả bằng phép ẩn dụ về đàn voi.
- Cần có slide sơ đồ khối và một slide mô phỏng cập nhật tọa độ từ ví dụ §12.5.
