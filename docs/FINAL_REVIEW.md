# Nghiệm thu EHO cho seminar

Bản nghiệm thu giữ cấu trúc Python, Qt và bốn notebook hiện tại. Mọi kết quả tiếp tục dùng chung EHO Core.
Bản demo ưu tiên hình trước–sau của từng cá thể để giải thích vì sao quần thể đổi vị trí.

## Thành phần đã xác minh

| Thành phần | Phương pháp | Kết quả |
|---|---|---|
| EHO, Rastrigin, Book Replay | Đọc lại Chương 12 từ PDF cục bộ, chạy `tests/test_core.py` | PASS, 23 test, 26/26 giá trị sách nằm trong dung sai |
| Dữ liệu và objective máy bơm | CSV, dữ liệu lỗi, tính năng lượng và penalty, chạy notebook | PASS, 3 test |
| PySide6 | Qt offscreen và nền tảng Windows, điều khiển nút bằng QTest | PASS, 3 test mỗi nền tảng |
| Thực nghiệm | Kernel Jupyter mới cho từng notebook, kiểm tra các bảng và PNG | PASS, 4 notebook mỗi chế độ QUICK/FULL |
| Phụ thuộc | Python 3.11.9, cài editable trong `.venv-eho`, chạy lại cài requirements và `pip check` | PASS |
| Trình chiếu | Đã kiểm thử kích thước cửa sổ 1366×768 và 1920×1080 bằng Qt | NOT VERIFIED trên máy chiếu của phòng học |

Toàn bộ pytest có **29 test đạt**. Các phiên bản chính của môi trường kiểm thử là NumPy 2.4.6,
Matplotlib 3.11.2, Pandas 3.1.1 và PySide6 6.12.0.

## Các thay đổi sau khi rà soát

- `src/gui` dùng giao diện phẳng, giảm chiều cao mặc định và xếp Start, Stop, Reset cùng hàng.
  Bảng màu sáng của Qt được đặt tường minh để tránh chữ trắng trên ô trắng khi Windows dùng theme tối.
  Đồ thị chuyển động vẽ từ các snapshot liền kề thật, kể cả khi worker lấy mẫu tiến độ để giảm tải.
  Bước đầu và Inspector dùng cùng bộ chọn thế hệ. Trục bơm hiện đúng đơn vị lưu lượng.
- `results_panel.py` bổ sung cờ trong cận của best lịch sử trong Results và JSON.
- Experiment 4 ban đầu có cấu hình chuyển trùng với cấu hình cơ sở trên cả hai tập seed.
  Đối chứng mới dùng 5 cá thể, giữ cùng số evaluations với cấu hình chuyển. Chênh lệch với
  mốc lưới được lưu theo từng seed. Experiment 3 bổ sung fitness trên mỗi chiều.
- Hai ZIP tham khảo đã được chuyển từ docs sang `outputs/reference-archives/`.
  PDF sách có trong máy cục bộ và không nằm trong danh sách tệp Git theo dõi.
- README, hướng dẫn người dùng, phân công, đối chiếu sách và thực nghiệm đã cập nhật.
  [Demo Guide](DEMO_GUIDE.md) và [Checklist](SEMINAR_CHECKLIST.md) dùng để chuẩn bị trình bày.

## Đối chiếu thuật toán

Công thức (12.1)–(12.5), luồng Algorithm 11 và cách lưu `bestloc` của hai listing được
đối chiếu trong [BOOK_ALIGNMENT](BOOK_ALIGNMENT.md). EHO giữ quần thể cũ trong suốt bước cập nhật.
Khi điểm bằng nhau, lấy chỉ số đầu tiên. Khi leader trùng worst, ưu tiên nhánh đầu đàn.
Nghiệm tốt nhất lịch sử được lưu riêng và công thức (12.4) giữ +1. Mã core giữ nguyên.

Fitness mới của x4 và x5 được tính lại từ tọa độ đã in. Phép tái hiện nguyên chuỗi r vẫn mang nhãn
`NOT FULLY REPRODUCIBLE`.

## Phạm vi kiểm tra GUI

QTest chạy trên Windows và offscreen, qua nhập seed/cận sai, các đầu mút α và β, quần thể 2 cá thể,
Rastrigin 2D và chiếu từ 4D, đọc bước 0, 1, cuối, so khớp hướng và độ dài mũi tên, chọn ba nhánh
Inspector và kiểm tra 26 hàng Book Example. Kiểm tra lại cùng seed, đổi seed, dừng, reset, chạy bơm,
đóng trong khi đang chạy và giải phóng worker. Các nút xuất CSV, JSON, PNG được nhấn trong test,
với đường dẫn hộp thoại được cấp tự động. Cả ba định dạng được mở lại để kiểm tra.
Entry point `main.py` được chạy với vòng sự kiện Qt Windows và cấu hình Rastrigin 2D 50 thế hệ.
Ảnh chụp trực tiếp từ cửa sổ được lưu cục bộ tại `outputs/gui-movement.png`.

## Thực nghiệm đã chạy

- QUICK dùng 5 seed 11, 23, 37, 53, 71 và ghi **270 lượt chạy** trong các bảng.
- FULL dùng 25 seed liên tiếp 101–125 và ghi **1.350 lượt chạy**. Hai số trên tính theo dòng
  báo cáo, gồm cả các cấu hình xuất hiện ở nhiều mục. Book Reproduction và các lượt chạy phụ
  để kiểm tra tái lập không tính vào số này.
- Mỗi chế độ có 4 notebook đã thực thi, 30 CSV và 24 PNG đã mở kiểm tra định dạng, ngoài
  metadata JSON. Các tệp nằm trong `outputs/quick/` và `outputs/full/`.
- Cùng 50 thế hệ, P=40 có mean tốt nhất trong nhóm quần thể FULL. Cùng 1.200 evaluations,
  P=20 có mean tốt nhất. Beta bằng 0 đặt hàng đầu đàn ở gốc Rastrigin.
- Cận hẹp ghi 1.766 lượt tọa độ vượt cận, so với 228 ở cận chuẩn, trên cùng 25 seed.
  Mức vượt lớn nhất tương ứng khoảng 0,99975 và 0,98854.
- Ở Peak Demand, với đúng 1.020 evaluations mỗi lượt, mean của cấu hình chuyển là 295,64,
  mean đối chứng là 983,63 và mốc lưới là 162,76. Cả 25 lượt của mỗi cấu hình đều có fitness
  cao hơn mốc lưới. Chỉ số dùng chi phí mô phỏng và penalty.

## Giới hạn

EHO tìm best quan sát được trong ngân sách. Kết quả thay đổi theo seed. Phép tách có thể
vượt cận và penalty bơm không bắt buộc nghiệm đáp ứng đủ lưu lượng. Grid Search chỉ đánh giá
một lưới hữu hạn, còn hệ số máy bơm là giả lập. Các kết luận thực nghiệm áp dụng cho cấu hình
và tập seed đã chạy. Lịch sử chi tiết tắt cho lần chạy GUI vượt ngưỡng 1 triệu ô snapshot.

## Lệnh chạy

```powershell
python -m venv .venv-eho
.\.venv-eho\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-eho\Scripts\python.exe -m pip install -e .
.\.venv-eho\Scripts\python.exe -m pip check
.\.venv-eho\Scripts\python.exe main.py
.\.venv-eho\Scripts\python.exe -m pytest -q
.\.venv-eho\Scripts\python.exe -m notebook
```

## Yêu cầu giảng viên

| Yêu cầu | Trạng thái | Bằng chứng |
|---|---|---|
| Algorithm Description | PASS | [Mô tả và ví dụ](ALGORITHM_DESCRIPTION.md), test core |
| Block Flow | PASS | [Sơ đồ nguồn](FLOWCHART.md) đã so với luồng core |
| Application | PASS | [Mô hình bơm](APPLICATION.md), test dữ liệu, Experiment 4 |
| Demo | PASS | Test Qt Windows và offscreen, [kịch bản demo](DEMO_GUIDE.md) |
| Task Distribution | PASS | [Bốn vai trò và phần trình bày](TEAM_PLAN.md) |
