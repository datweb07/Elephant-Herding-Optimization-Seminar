# Đối chiếu Chương 12

Nguồn đối chiếu là PDF được cung cấp trong repo, *Swarm Intelligence Algorithms: A Tutorial*,
Chương 12 của N. K. Meena, J. Yang và A. Slowik, trang in 149–162 (trang PDF 174–187).

| Căn cứ trong sách | Python | Cách kiểm tra |
|---|---|---|
| (12.1), tr. 151–152 | `update_regular_elephant` | Bước tính x1 với r đã in và test độc lập |
| (12.2), tr. 152 | `update_best_elephant` | Bước tính x3, dùng tâm chưa làm tròn |
| (12.3), tr. 152 | `calculate_population_center` | Trung bình từng cột của 5 hàng |
| (12.4), tr. 152–153 | `separate_worst_elephant` | Bước tính x2 và trường hợp vượt cận bắt buộc |
| (12.5), tr. 157–158 | `rastrigin` | Điểm gốc và 10 fitness từ các tọa độ in |
| Algorithm 11, tr. 153–154 | `initialize_population`, `run` | Test khởi tạo, thế hệ, bộ đếm, trạng thái kết thúc |
| Listing 12.1, tr. 153–155 | `update_population`, `run` | Test dùng quần thể cũ và giữ chỉ số đầu đàn |
| Listing 12.2, tr. 155–157 | `find_best_and_worst` và ba nhánh | Test bằng điểm, ưu tiên đầu đàn khi trùng hàng |
| §12.5, tr. 157–161 | `verify_book_example` | 26 giá trị đối chiếu, x4/x5 thiếu số r |

## Bằng chứng kiểm thử

| Phương trình | Trang in | Hàm Python | Ca kiểm thử trong `tests/test_core.py` | Kết quả |
|---|---|---|---|---|
| (12.1) | 151–152 | `update_regular_elephant` | `test_regular_center_matriarch`, `test_book_replay_all_printed_values` | PASS |
| (12.2) | 152 | `update_best_elephant` | `test_regular_center_matriarch`, `test_tie_prefers_first_and_matriarch_precedes_separation` | PASS |
| (12.3) | 152 | `calculate_population_center` | `test_generation_uses_old_population_and_explicit_draws` | PASS |
| (12.4) | 152–153 | `separate_worst_elephant` | `test_separation_preserves_plus_one_and_overshoot` | PASS |
| (12.5) | 157–158 | `rastrigin` | `test_rastrigin_origin`, `test_book_replay_all_printed_values` | PASS |

## Ký hiệu và cách biểu diễn

| MATLAB/C++ | Python | Ý nghĩa |
|---|---|---|
| `N` | `population_size` | Số hàng trong listings |
| `nc` | `dimension` | Số cột trong listings |
| `pp`, `pp_new` | `population`, `updated` | Ma trận cũ và mới, mỗi hàng một nghiệm |
| `OF`, `Fitness` | `objective_function`, `fitness` | Hàm trên cả hàng và vector điểm |
| `LB`, `UB` | `lower_bounds`, `upper_bounds` | Cận theo từng cột |
| `pp_center` | `center` | Trung bình theo cột |
| `bestloc_new`, `worstloc` | `current_best`, `worst` | Cực trị trong quần thể đang xét |
| `bestloc` | `leader` / `leader_index` | Hàng dùng công thức đầu đàn ở lần cập nhật tới |
| `pbest`, `fbest` | `best_position`, `best_fitness` | Nghiệm và giá trị kỷ lục lịch sử |
| `Gmax`, `gen` | `max_generations`, `number` | Ngân sách và số thế hệ hoàn tất |

§12.1–12.2 mô tả nhiều clan sinh học, mỗi clan có voi đầu đàn. Listings đánh giá mỗi hàng đầy đủ
và chọn cực trị theo hàng. §12.5 dùng `N` cho số chiều và `nc` cho số cá thể, đảo cách dùng
trong listings. Python dùng ma trận `(population_size, dimension)` để giữ phép đánh giá và
phép tính tâm như ví dụ. MATLAB dùng chỉ số từ 1, Python và C++ dùng từ 0.

## Các quyết định ảnh hưởng đến kết quả

1. **Thứ tự cập nhật.** Algorithm 11 bước 18 có biểu thức khó đọc. Listing 12.1 dòng 43–56
   và Listing 12.2 dòng 55–75 cho thấy ba nhánh riêng. Python đọc ma trận cũ, xây ma trận mới
   theo hàng, sau đó đánh giá từng hàng. Listings xen đánh giá sau khi cập nhật xong mỗi hàng.
   Với objective xác định và độc lập với RNG của EHO, kết quả và thứ tự đánh giá tương đương.
2. **Best hiện tại và best lịch sử.** Listing 12.1 dòng 59–77, Listing 12.2 dòng 79–99
   đổi `bestloc` cùng `pbest` và `fbest` khi cải thiện nghiêm ngặt. Nếu không cải thiện, hàng
   đầu đàn có thể khác best hiện tại. Python giữ hành vi này. Worst được tính lại mỗi thế hệ.
   Ma trận mới được lưu nguyên, nên bản sao pbest lịch sử có thể nằm ngoài quần thể hiện tại.
3. **Bằng điểm.** MATLAB `find` có thể trả nhiều chỉ số. Python theo `min_element` và
   `max_element` của Listing 12.2 dòng 35–41 và 79–85, lấy lần xuất hiện đầu tiên. Nếu chỉ
   số đầu đàn và worst trùng, nhánh đầu đàn đứng trước như dòng 60–71. Khi đó thế hệ bỏ qua
   phép tách và không rút r cho hàng đó.
4. **Random.** Algorithm 11 bước 8 và (12.1), (12.4) lấy một số cho mỗi tọa độ. Python dùng
   NumPy `default_rng(seed)`, phân phối đều thực trong [0,1), tương tự ý nghĩa của MATLAB.
   Listing 12.2 dòng 13 dùng lưới 0,001 và dòng 20 seed theo thời gian. Cùng seed Python tái lập
   được Python trong cùng môi trường. `update_population` nhận ma trận r trực tiếp để kiểm thử.
5. **Cận.** (12.4) và hai listings đều có +1. Kết quả giữ nguyên sau cập nhật, kể cả ngoài cận.
   Bộ đếm đo số lượt cá thể và tọa độ ngoài cận trên mọi thế hệ. (12.2) cũng có thể đưa nghiệm
   ngoài miền nếu miền không chứa gốc. Penalty bơm thuộc objective.
6. **Làm tròn.** §12.5 in tọa độ và fitness tới khoảng ba chữ số. Đối chiếu tọa độ và tâm
   dùng dung sai 0,00051, fitness dùng 0,001. Fitness mới tính lại từ đúng tọa độ đã in.
   x4 và x5 thiếu r. Kiểm chứng toàn bộ fitness từ tọa độ in là **MATCH**, tái hiện cả chuỗi
   cập nhật là **NOT FULLY REPRODUCIBLE**.
