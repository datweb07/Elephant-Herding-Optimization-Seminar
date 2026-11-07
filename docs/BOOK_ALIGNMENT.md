# Book Alignment — Kiểm tra mức độ bám sát Chương 12

**Nguồn duy nhất cho logic EHO:** Nand K. Meena, Jin Yang, Adam Slowik, Chapter 12, *Swarm Intelligence Algorithms: A Tutorial*, trang in 149–162, tương ứng trang PDF 174–187.

## 1. Quy chiếu giữa sách và mã nguồn dự kiến

| Thành phần dự kiến | Căn cứ trong sách | Điều kiện nghiệm thu |
|---|---|---|
| Population initialization | Algorithm 11, bước 1–12; Listings 12.1/12.2 | Khởi tạo nghiệm trong phạm vi, đánh giá OF trên từng nghiệm |
| Regular elephant update | Công thức (12.1); phần cập nhật trong Listings 12.1/12.2 | Đúng alpha, đúng vị trí tốt nhất, đúng cách lấy random |
| Best elephant update | Công thức (12.2)–(12.3) | Đúng beta nhân trung bình vị trí |
| Worst elephant separation | Công thức (12.4) | Tránh tự ý bỏ `+1` khi kiểm chứng bản sách |
| Fitness evaluation | Algorithm 11 và Listings 12.1/12.2 | Tính trên một nghiệm hoàn chỉnh; chọn min đối với Rastrigin |
| Best history | Listings 12.1/12.2 | Ghi giá trị tốt nhất đã tìm thấy khi qua các thế hệ |
| Rastrigin example | §12.5, công thức (12.5), trang 157–161 | Đối chiếu dữ liệu khởi tạo và kết quả tính một vòng trong sách |

## 2. Những điểm cần lưu ý, không được tự sửa ngầm

1. **Ngữ nghĩa clan / chiều biến:** Phần mô tả thuật toán nói nhiều đàn độc lập, nhưng mã MATLAB/C++ trong chương dùng `pp[j,c]`: `j` là hàng nghiệm, `c` là chiều / cột. Hàm OF đánh giá hàng nghiệm hoàn chỉnh và tìm `bestloc`/`worstloc` toàn cục theo hàng. Để tái hiện Listing 12.1–12.2, cần nêu rõ biểu diễn này trong tài liệu và GUI.
2. **Phương trình (12.4) có `+1`:** Đây là công thức đúng như in trong sách. Với biến liên tục, công thức có thể tạo vị trí vượt cận trên. Đây là vấn đề của nguồn tham khảo; không tự gắn clipping hoặc loại bỏ `+1` rồi nói là nguyên bản. Nếu cần một biến thể xử lý cận, bắt buộc tách riêng, ghi là điều chỉnh và không dùng để kiểm chứng bản nguyên gốc.
3. **Thuật ngữ / chỉ số:** Ký hiệu `N`, `nc` ở phần giả mã, code và ví dụ minh họa chưa hoàn toàn đồng nhất. Đặt tên rõ ràng trong Python thành `population_size` và `dimension`; có bảng đối chiếu tên với sách.
4. **Điều kiện giả mã:** Một biểu thức `if` tại Algorithm 11 có cú pháp khó hiểu khi so với các listing. Cần dựa vào ba nhánh best / worst / ordinary elephant được thể hiện rõ trong mã MATLAB/C++, đồng thời ghi lại điểm chưa thống nhất này.
5. **Điểm tốt nhất lịch sử / vị trí index:** Mã mẫu ghi nhận `fbest` và `pbest` tốt nhất theo lịch sử; vị trí hàng `bestloc` trong quần thể mới cần đọc kỹ khi hiện thực. Không tự giới thiệu cơ chế elitism thay thế cá thể nếu sách không mô tả.
6. **Random trong ví dụ:** Số ngẫu nhiên được ấn định trong bước tính tay của sách; seed của Python không đảm bảo tạo trùng chính xác dãy của MATLAB/C++. Kiểm chứng một bước phải cho phép nạp giá trị ngẫu nhiên cố định của sách.
7. **Giới hạn của ứng dụng:** Sách trình bày ví dụ Rastrigin, không cung cấp mô hình, dữ liệu hoặc thông số cho bài toán vận hành máy bơm. Phải dán nhãn toàn bộ dữ liệu ứng dụng là do nhóm giả lập.

## 3. Quy tắc khi code

- Mỗi toán tử quan trọng được chú thích nguồn theo số phương trình/trang.
- Có unit test tính toán thủ công cho từng công thức.
- Mỗi lần thay đổi thuật toán phải so với chương sách trước khi merge.
- Không dùng kết quả trên benchmark làm bằng chứng rằng bài toán thực tế đã được giải thành công.
