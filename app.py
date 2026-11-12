"""Mini App Nhóm B: Màn hình thông minh, giấc ngủ an lành.

Cấu trúc code:
1. Import và cấu hình
2. Hằng số/tên cột
3. Hàm đọc file
4. Giao diện trang chủ
5. Công cụ tự kiểm tra thói quen
6. Phân tích dữ liệu khảo sát
7. Kiến thức và an toàn
8. Chân trang
"""
import io
import pandas as pd
import streamlit as st
from logic import (
    REQUIRED_COLUMNS, prepare_dataframe, validate_dataframe,
    summarize_dataframe, calculate_sleep_hours, create_message,
)

# [1] CẤU HÌNH TRANG: tiêu đề, biểu tượng, bố cục màn hình.
st.set_page_config(
    page_title="Màn hình thông minh – Giấc ngủ an lành",
    page_icon="🌙",
    layout="wide",
)

# [2] HẰNG SỐ: tên cột phải khớp file Excel khảo sát Nhóm B.
SCREEN_COL = "Thời gian sử dụng màn hình (giờ/ngày)"
BEFORE_COL = "Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)"
BED_COL = "Giờ đi ngủ"
WAKE_COL = "Giờ thức dậy"
SLEEP_COL = "Thời lượng ngủ (giờ)"

# [3] HÀM ĐỌC FILE: hỗ trợ workbook Excel có tiêu đề ở dòng 3 hoặc CSV chuẩn.
def read_uploaded_file(uploaded_file):
    """Đọc file tải lên; file Excel của dự án có 2 dòng tiêu đề phía trên."""
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        # skiprows=2: bỏ tiêu đề lớn và dòng lưu ý; hàng tiếp theo là tên cột.
        return pd.read_excel(uploaded_file, sheet_name="Du_lieu_khao_sat", skiprows=2)
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    raise ValueError("Định dạng chưa hỗ trợ. Vui lòng tải file .xlsx hoặc .csv.")

def dataframe_to_csv(df):
    """Đóng gói bảng đã xử lý thành CSV UTF-8 để tải xuống."""
    return df.to_csv(index=False).encode("utf-8-sig")

# [4] TRANG CHỦ: giới thiệu mục tiêu và giới hạn sản phẩm.
st.title("🌙 Màn hình thông minh – Giấc ngủ an lành")
st.caption("Mini App STEM Tin học 9 | Dự án “Dữ liệu vì sức khỏe học đường” | Nhóm B")
st.info(
    "Ứng dụng học tập giúp quan sát thói quen sử dụng màn hình và giấc ngủ. "
    "Kết quả chỉ là thông tin giáo dục theo quy ước của dự án, không phải chẩn đoán y tế."
)

with st.expander("🎯 Mục tiêu và cách ứng dụng hoạt động", expanded=False):
    st.markdown(
        "- Nhập thông tin cá nhân để xem phép tính minh họa về thời lượng ngủ.\n"
        "- Tải bảng Excel/CSV để phân tích dữ liệu khảo sát đã ẩn danh.\n"
        "- Xem số lượng, tổng giờ theo nhóm và thông điệp giáo dục.\n"
        "- Python thực hiện phép tính theo quy tắc đã lập trình; app không gọi API AI trả phí."
    )

tab1, tab2, tab3 = st.tabs([
    "🧭 Tự kiểm tra thói quen",
    "📊 Phân tích khảo sát",
    "📘 Kiến thức & an toàn",
])

# [5] CÔNG CỤ TỰ KIỂM TRA: nhận đầu vào cá nhân, tính và hiển thị gợi ý.
with tab1:
    st.subheader("Tự xem lại một số thói quen")
    st.write("Nhập thông tin để xem cách ứng dụng phân tích. Không cần nhập tên hoặc thông tin định danh.")
    c1, c2 = st.columns(2)
    with c1:
        screen_hours = st.number_input(
            "Thời gian sử dụng màn hình (giờ/ngày)",
            min_value=0.0, max_value=24.0, value=3.0, step=0.5,
        )
        before_sleep = st.radio(
            "Có sử dụng màn hình trong 1 giờ trước khi ngủ?",
            ["Không", "Có"], horizontal=True,
        )
    with c2:
        bedtime = st.time_input("Giờ đi ngủ", value=pd.Timestamp("2026-01-01 22:00").time())
        wake_time = st.time_input("Giờ thức dậy", value=pd.Timestamp("2026-01-02 06:30").time())
    sleep_hours = calculate_sleep_hours(bedtime, wake_time)
    if sleep_hours is None:
        st.warning("Không tính được thời lượng ngủ. Hãy kiểm tra giờ đi ngủ và giờ thức dậy.")
    else:
        m1, m2 = st.columns(2)
        m1.metric("Thời lượng ngủ tính được", f"{sleep_hours:.1f} giờ")
        m2.metric("Nhóm thời lượng ngủ", "Dưới 8 giờ" if sleep_hours < 8 else ("8–10 giờ" if sleep_hours <= 10 else "Trên 10 giờ"))
        msg = create_message(screen_hours, before_sleep, sleep_hours)
        if msg.startswith("Cần"):
            st.warning(msg)
        else:
            st.success(msg)
    st.caption("Ngưỡng >4 giờ/ngày là quy ước học tập của dự án; mốc 8–10 giờ là khuyến nghị tham khảo phổ biến cho thanh thiếu niên 13–18 tuổi.")

# [6] PHÂN TÍCH DỮ LIỆU: tải file, chuẩn hóa, kiểm tra, thống kê, biểu đồ.
with tab2:
    st.subheader("Phân tích dữ liệu khảo sát lớp 9B")
    st.write("Tải file Excel Nhóm B hoặc CSV có đủ các trường dữ liệu. Dữ liệu phải được ẩn danh.")
    uploaded = st.file_uploader("Chọn file Excel hoặc CSV", type=["xlsx", "xls", "csv"], key="survey_upload")
    if uploaded is not None:
        try:
            raw = read_uploaded_file(uploaded)
            df = prepare_dataframe(raw)
            st.success(f"Đã đọc {len(df)} dòng dữ liệu.")
            issues = validate_dataframe(df)
            if issues:
                st.warning("Cần rà soát dữ liệu trước khi sử dụng kết quả:")
                for issue in issues:
                    st.write(f"- {issue}")
            else:
                st.success("Kiểm tra cơ bản: chưa phát hiện cảnh báo.")

            summary = summarize_dataframe(df)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Số mã HS", summary["total"])
            k2.metric("Màn hình >4 giờ/ngày", summary["screen_over"])
            k3.metric("Ngủ dưới 8 giờ", summary["sleep_under"])
            k4.metric("Dùng màn hình trước ngủ", summary["before_bed_yes"])

            st.markdown("#### Bảng thống kê tổng hợp")
            stat_df = pd.DataFrame([
                ["Số HS có mã", summary["total"], "Đếm bản ghi có mã"],
                ["Số HS màn hình >4 giờ/ngày", summary["screen_over"], "Tương đương COUNTIF"],
                ["Số HS ngủ dưới 8 giờ", summary["sleep_under"], "Tương đương COUNTIF"],
                ["Số HS dùng màn hình trong 1 giờ trước ngủ", summary["before_bed_yes"], "Tương đương COUNTIF"],
                ["Tổng giờ màn hình của nhóm >4 giờ/ngày", round(summary["sum_screen_over"], 1), "Tương đương SUMIF"],
                ["Tổng giờ ngủ của nhóm ngủ dưới 8 giờ", round(summary["sum_sleep_under"], 1), "Tương đương SUMIF"],
            ], columns=["Chỉ tiêu", "Kết quả", "Cách tính"])
            st.dataframe(stat_df, use_container_width=True, hide_index=True)

            st.markdown("#### Biểu đồ phân nhóm")
            chart_data = pd.DataFrame({
                "Nhóm": ["Màn hình trên 4 giờ/ngày", "Ngủ dưới 8 giờ", "Dùng màn hình trước ngủ"],
                "Số học sinh": [summary["screen_over"], summary["sleep_under"], summary["before_bed_yes"]],
            }).set_index("Nhóm")
            st.bar_chart(chart_data)

            st.markdown("#### Dữ liệu đã chuẩn hóa")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Tải dữ liệu đã xử lý (CSV)",
                data=dataframe_to_csv(df),
                file_name="ket_qua_phan_tich_nhom_B.csv",
                mime="text/csv",
            )
        except Exception as exc:
            st.error(f"Không thể xử lý file: {exc}")
            st.caption("Kiểm tra đúng tên sheet Du_lieu_khao_sat, hàng tiêu đề và tên các cột theo mẫu Nhóm B.")
    else:
        st.info("Chưa tải file. Có thể dùng tab “Tự kiểm tra thói quen” để thử phép tính cá nhân.")

# [7] KIẾN THỨC & AN TOÀN: giải thích quy tắc và bảo vệ người học.
with tab3:
    st.subheader("Kiến thức nền và cách đọc kết quả")
    st.markdown(
        "**Một số điểm cần nhớ**\n"
        "- Thanh thiếu niên 13–18 tuổi thường được khuyến nghị ngủ khoảng 8–10 giờ mỗi ngày.\n"
        "- Sử dụng màn hình sát giờ ngủ có thể làm giảm thời gian dành cho nghỉ ngơi hoặc gây khó thư giãn.\n"
        "- Khảo sát tự báo cáo có thể có sai số; dữ liệu lớp học nhỏ không đại diện cho tất cả học sinh."
    )
    st.markdown("**Quy tắc của dự án**")
    st.write("- Thời gian màn hình >4 giờ/ngày: gắn nhãn cần lưu ý theo quy ước học tập.")
    st.write("- Thời lượng ngủ dưới 8 giờ: nhóm dưới mốc khuyến nghị tham khảo.")
    st.write("- Có sử dụng màn hình trong 1 giờ trước khi ngủ: đưa ra gợi ý xem lại thói quen.")
    st.warning(
        "Không dùng ứng dụng để chẩn đoán, xếp loại sức khỏe hoặc so sánh công khai từng học sinh. "
        "Nếu khó ngủ/mệt mỏi kéo dài, hãy trao đổi với cha mẹ/người chăm sóc hoặc nhân viên y tế."
    )
    st.markdown("**Vai trò của AI trong dự án**")
    st.write(
        "AI có thể hỗ trợ học sinh và giáo viên trong giai đoạn phát triển: gợi ý cấu trúc, "
        "tạo bản nháp code, giải thích lỗi. Khi ứng dụng đang chạy, các phép tính do Python "
        "thực hiện theo quy tắc lập trình; không có kết nối API AI trả phí."
    )

# [8] CHÂN TRANG.
st.divider()
st.caption("Sản phẩm học tập STEM – Tin học 9 | Nhóm B | Dữ liệu vì sức khỏe học đường")
