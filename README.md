# Mini App Nhóm B – Màn hình thông minh, giấc ngủ an lành

## 1. Mục đích
Ứng dụng STEM Tin học 9 giúp học sinh thực hành xử lý dữ liệu về thời gian sử dụng màn hình và giấc ngủ. Đây là công cụ học tập/truyền thông, không phải công cụ chẩn đoán sức khỏe.

## 2. Cấu trúc thư mục
- `app.py`: giao diện Streamlit và luồng thao tác.
- `logic.py`: các hàm tính toán/kiểm tra/ thống kê độc lập, dễ đọc và kiểm thử.
- `requirements.txt`: thư viện cần cài.
- `.streamlit/config.toml`: cấu hình giao diện.
- `data/mau_khao_sat_nhom_B.csv`: mẫu trống 30 mã HS để nhập dữ liệu thật.
- `data/du_lieu_mo_phong_30_HS.csv`: dữ liệu mô phỏng để thử app; không phải kết quả khảo sát.

## 3. Chạy trên Windows
1. Cài Python 3.10 trở lên.
2. Giải nén ZIP, mở thư mục dự án.
3. Mở Terminal/CMD tại thư mục dự án.
4. Tạo môi trường ảo (khuyến nghị): `python -m venv .venv`
5. Kích hoạt: `.venv\Scripts\activate`
6. Cài thư viện: `pip install -r requirements.txt`
7. Chạy: `streamlit run app.py`
8. Trình duyệt mở địa chỉ local do Streamlit cung cấp (thường là `http://localhost:8501`).

## 4. Dùng ứng dụng
- Tab **Tự kiểm tra thói quen**: nhập thời gian màn hình, việc dùng màn hình trước ngủ, giờ đi ngủ và thức dậy; app tính thời lượng ngủ và hiển thị thông điệp theo quy ước.
- Tab **Phân tích khảo sát**: tải file Excel Nhóm B đã tạo ở Bước 1 hoặc CSV đủ cột. Excel cần sheet `Du_lieu_khao_sat`, tiêu đề cột ở dòng 3 như file mẫu.
- App tự tính lại thời lượng ngủ từ giờ đi ngủ/thức dậy, không phụ thuộc kết quả công thức được lưu sẵn trong Excel.
- Xem các số đếm, tổng theo nhóm, biểu đồ và tải CSV đã xử lý.
- Tab **Kiến thức & an toàn**: xem các giới hạn và lưu ý.

## 5. Quy tắc phân tích
- Thời gian màn hình `> 4 giờ/ngày`: nhãn “Trên 4 giờ/ngày”. Đây là ngưỡng minh họa do dự án chọn để học IF/COUNTIF/SUMIF, không phải chuẩn y tế áp dụng cho mọi học sinh.
- Thời lượng ngủ: dưới 8 giờ; 8–10 giờ; trên 10 giờ. Mốc 8–10 giờ là khuyến nghị tham khảo phổ biến cho thanh thiếu niên 13–18 tuổi.
- Có sử dụng màn hình trong 1 giờ trước khi ngủ: app gợi ý xem lại thói quen.
- Thông điệp “Cần xem lại thói quen…” xuất hiện khi màn hình >4 giờ HOẶC dùng màn hình trong 1 giờ trước ngủ HOẶC ngủ <8 giờ.
- Thiếu dữ liệu thì không tạo thông điệp cá nhân.

## 6. Vai trò AI
AI chỉ hỗ trợ trong quá trình thiết kế, tạo bản nháp code, giải thích và sửa lỗi. Khi app chạy, Python xử lý theo các quy tắc đã lập trình; app không gọi API AI trả phí. Học sinh cần đọc, hiểu, chạy thử và giải thích code.

## 7. Triển khai GitHub + Streamlit Community Cloud
1. Tạo repository GitHub, tải toàn bộ nội dung thư mục lên (giữ nguyên cấu trúc).
2. Trên Streamlit Community Cloud, đăng nhập bằng GitHub và chọn **Create app**.
3. Chọn repository, branch và file chính `app.py`.
4. Deploy; chờ hệ thống cài thư viện từ `requirements.txt`.
5. Mở URL được cấp, thử tab tự kiểm tra và tải dữ liệu mô phỏng.
6. Không đưa dữ liệu cá nhân/nhạy cảm của học sinh lên repository công khai. Khi cần trình diễn online, dùng dữ liệu mô phỏng hoặc dữ liệu đã ẩn danh và được phép chia sẻ.

## 8. Kiểm thử tối thiểu
- 22:00 đến 06:30 phải ra 8,5 giờ.
- 23:30 đến 06:30 phải ra 7 giờ.
- 3 giờ màn hình, không dùng trước ngủ, ngủ 8,5 giờ: thông điệp tương đối phù hợp.
- 5 giờ màn hình, không dùng trước ngủ, ngủ 8,5 giờ: thông điệp cần xem lại.
- 3 giờ màn hình, có dùng trước ngủ, ngủ 8,5 giờ: thông điệp cần xem lại.
- 3 giờ màn hình, không dùng trước ngủ, ngủ 7 giờ: thông điệp cần xem lại.
- Thiếu giờ đi ngủ/thức dậy: không tính thời lượng ngủ.

## 9. Giới hạn và bảo vệ dữ liệu
Khảo sát tự báo cáo có thể sai số và mẫu lớp 9B không đại diện cho mọi học sinh. Không công khai mã cá nhân cùng kết quả; không dùng app để xếp loại sức khỏe. Nếu khó ngủ hoặc mệt mỏi kéo dài, học sinh nên trao đổi với người lớn đáng tin cậy hoặc nhân viên y tế.
