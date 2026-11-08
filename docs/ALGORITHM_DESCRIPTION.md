# Thuật toán Elephant Herding Optimization

Đàn voi thường đi theo voi cái đầu đàn. Voi đực trưởng thành có thể rời đàn.
§12.1–12.2 dùng hai hành vi này để minh họa việc khai thác quanh nghiệm tốt và tìm kiếm vùng mới.
Trong Python, một hàng của quần thể là một nghiệm liên tục, một cột là một biến. Objective nhận
cả vector và trả fitness cần tối thiểu hóa.

| Tham số | Vai trò | Mặc định demo |
|---|---|---|
| P | Số cá thể, ít nhất 2 | 5 |
| d | Số chiều dương | 4 |
| α | Ảnh hưởng của pbest lịch sử, [0,1] | 0,5 |
| β | Hệ số của tâm cũ, [0,1] | 0,1 |
| G | Số thế hệ tối đa, ít nhất 1 | 50 |
| LB, UB | Cận danh nghĩa mỗi tọa độ, LB < UB | −5,12 và 5,12 |
| Seed | Khởi tạo bộ sinh ngẫu nhiên cục bộ | 42 |

## Phương trình

- Khởi tạo từng tọa độ theo `LB + (UB − LB) × r`, với r đồng đều trong [0,1).
- (12.1) Voi thường dùng `x_new = x + α × (pbest − x) × r`. Mỗi tọa độ có r riêng.
- (12.3) Tâm là `mean(population, axis=0)`. Dữ liệu là quần thể cũ.
- (12.2) Hàng đầu đàn dùng `x_new = β × tâm`.
- (12.4) Worst dùng `x_new = LB + r × (UB − LB + 1)`. Số hạng +1 có thể làm vượt cận.

## Giả mã

```text
Khởi tạo quần thể, đánh giá mọi hàng, lấy best và worst đầu tiên
Lưu pbest và chỉ số đầu đàn, ghi thế hệ 0
Lặp đến G hoặc có yêu cầu dừng
    Tính tâm từ quần thể cũ
    Tạo từng hàng mới theo đầu đàn, worst hoặc cá thể thường
    Đánh giá mọi hàng mới, xác định best và worst hiện tại
    Nếu best mới cải thiện nghiêm ngặt, cập nhật kỷ lục và chỉ số đầu đàn
    Thay quần thể, ghi chỉ số và các vi phạm
Trả nghiệm tốt nhất lịch sử, số lần đánh giá và lịch sử đã lưu
```

Một lần hoàn tất G thế hệ gọi objective đúng P × (G + 1) lần. Best lịch sử chỉ giảm hoặc
giữ nguyên. Current Best và Mean có thể tăng. Thời gian core loại thời gian callback cập nhật GUI.
Số lượt vi phạm tính theo mỗi snapshot, nên một cá thể còn ngoài cận nhiều thế hệ sẽ được đếm lại.

Toán tử ngắn và dễ kiểm tra. Core dùng lại được cho objective khác. Chất lượng phụ thuộc tham số,
ngân sách và seed. Với beta bằng 0, (12.2) đưa đầu đàn về gốc, trùng cực tiểu của Rastrigin.
Điều này giúp giải thích kết quả ở benchmark đó và cần được xem xét khi đổi objective.
