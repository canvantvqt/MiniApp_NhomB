"""Mini App Nhóm B: Màn hình thông minh, giấc ngủ an lành.

Giao diện được nâng cấp theo nhận diện Nhóm B – Lớp 9C.
Các phép tính và quy tắc xử lí vẫn sử dụng module logic.py hiện có.
"""
import pandas as pd
import streamlit as st
from pathlib import Path

from logic import (
    REQUIRED_COLUMNS, prepare_dataframe, validate_dataframe,
    summarize_dataframe, calculate_sleep_hours, create_message,
)

# [1] CẤU HÌNH TRANG
st.set_page_config(
    page_title="Màn hình thông minh – Giấc ngủ an lành",
    page_icon="🌙",
    layout="wide",
)

# [2] HẰNG SỐ / TÊN CỘT – giữ khớp workbook khảo sát
SCREEN_COL = "Thời gian sử dụng màn hình (giờ/ngày)"
BEFORE_COL = "Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)"
BED_COL = "Giờ đi ngủ"
WAKE_COL = "Giờ thức dậy"
SLEEP_COL = "Thời lượng ngủ (giờ)"

# [3] HÀM ĐỌC FILE – giữ nguyên quy tắc đọc dữ liệu
def read_uploaded_file(uploaded_file):
    """Đọc Excel có tiêu đề ở dòng 3 hoặc CSV chuẩn."""
    name = uploaded_file.name.lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(
            uploaded_file,
            sheet_name="Du_lieu_khao_sat",
            skiprows=2
        )
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    raise ValueError("Định dạng chưa hỗ trợ. Vui lòng tải file .xlsx hoặc .csv.")


def dataframe_to_csv(df):
    """Đóng gói bảng đã xử lý thành CSV UTF-8 để tải xuống."""
    return df.to_csv(index=False).encode("utf-8-sig")


# [4] HỆ THỐNG GIAO DIỆN
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Be Vietnam Pro','Segoe UI',Arial,sans-serif;}
.stApp {background:#f7f8fc;color:#202b45;}
.block-container {max-width:1480px;padding-top:1rem;padding-bottom:2rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#fff0f7 0%,#f2f4ff 100%);border-right:1px solid #eaddec;}
[data-testid="stSidebar"] .stRadio label {font-weight:650;color:#26345a;}
.top-strip {background:linear-gradient(90deg,#fff0f7,#eef3ff);border:1px solid #f0dce9;border-radius:15px;padding:.75rem 1rem;margin:.15rem 0 1rem;color:#39415c;}
.top-strip strong {color:#bd1765;}
.hero-title {background:linear-gradient(110deg,#172f70,#315fc4 62%,#7b66c8);padding:1.05rem 1.4rem;border-radius:18px;color:white;margin:.6rem 0 1rem;box-shadow:0 8px 24px #243e831c;}
.hero-title h1 {color:white!important;font-size:clamp(1.45rem,2.7vw,2.1rem);font-weight:800;margin:.1rem 0 .25rem;}
.hero-title p {color:#eaf0ff;margin:0;}
.eyebrow {display:inline-block;background:#ffffff20;border:1px solid #ffffff55;border-radius:99px;padding:.28rem .7rem;font-size:.76rem;font-weight:800;letter-spacing:.03em;}
.section-title {font-size:1.3rem;font-weight:800;color:#243d83;margin:.3rem 0;}
.section-sub {color:#69738c;margin-bottom:1rem;}
.feature-card {height:100%;min-height:158px;background:linear-gradient(145deg,#fff,#f6f7ff);border:1px solid #e2e5f3;border-radius:17px;padding:1rem 1.05rem;box-shadow:0 4px 14px #263c8010;}
.feature-card h3 {font-size:1rem;color:#263d80;font-weight:800;margin:.35rem 0;}
.feature-card p {font-size:.88rem;line-height:1.5;color:#59647d;margin:0;}
.feature-icon {font-size:2rem;line-height:1.2;}
.pill-row {display:flex;flex-wrap:wrap;gap:.45rem;margin:.55rem 0 1rem;}
.pill {background:#fff;border:1px solid #e1dff0;color:#45517b;border-radius:99px;padding:.38rem .7rem;font-size:.8rem;font-weight:700;}
.panel {background:#fff;border:1px solid #e5e6f1;border-radius:16px;padding:1rem 1.1rem;margin:.4rem 0 1rem;}
div[data-testid="stMetric"] {background:#fff;border:1px solid #e3e5f1;border-radius:15px;padding:.85rem .95rem;}
div[data-testid="stMetricValue"] {color:#243d83;font-weight:800;}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button {border-radius:11px;font-weight:750;min-height:2.55rem;}
div[data-testid="stDataFrame"] {border:1px solid #e3e5f1;border-radius:12px;overflow:hidden;}
div[data-testid="stTabs"] button {font-weight:750;}
.footer {text-align:center;color:#69738c;font-size:.82rem;line-height:1.7;padding:1rem .5rem;}
.note {font-size:.8rem;color:#737d94;}
</style>
""", unsafe_allow_html=True)

# [5] NHẬN DIỆN DỰ ÁN VÀ TRANG CHỦ
st.markdown(
    '<div class="top-strip">🏫 <strong>TRƯỜNG TH, THCS & THPT TRƯNG VƯƠNG</strong>'
    ' &nbsp; · &nbsp; DỰ ÁN STEM TIN HỌC 9'
    ' &nbsp; · &nbsp; <strong>NHÓM B – LỚP 9C</strong></div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("## 🌙 MINI APP · NHÓM B")
    st.markdown("**MÀN HÌNH THÔNG MINH – GIẤC NGỦ AN LÀNH**")
    st.caption("LỚP 9C · DỮ LIỆU VÌ SỨC KHỎE HỌC ĐƯỜNG")
    st.divider()
    st.markdown("### 🧭 ĐIỀU HƯỚNG")
    st.caption("Chọn một khu vực chức năng ở các thẻ bên phải.")
    st.divider()
    st.markdown("🌙 **Thông điệp:** Ngủ đủ giấc – Học tốt hơn!")
    st.caption("Phiên bản học tập – không thay thế tư vấn y tế.")

hero_path = Path(__file__).with_name("hero_nhom_b.png")
if hero_path.exists():
    st.image(str(hero_path), use_container_width=True)

st.markdown(
    '<div class="hero-title">'
    '<span class="eyebrow">MINI APP STEM · NHÓM B · LỚP 9C</span>'
    '<h1>🌙 Màn hình thông minh – Giấc ngủ an lành</h1>'
    '<p>Quan tâm hôm nay – Sức khỏe ngày mai | Sử dụng màn hình có kiểm soát, ngủ đủ và đúng giờ.</p>'
    '</div>',
    unsafe_allow_html=True
)

# Dùng tabs để giữ nguyên luồng chức năng của bản gốc
tab1, tab2, tab3 = st.tabs([
    "🌙 Tự kiểm tra thói quen",
    "📊 Phân tích khảo sát",
    "📘 Kiến thức & an toàn",
])

# [6] CÔNG CỤ TỰ KIỂM TRA
with tab1:
    st.markdown(
        '<div class="section-title">💗 Tự xem lại một số thói quen</div>'
        '<div class="section-sub">Nhập thông tin để xem cách ứng dụng phân tích. '
        'Không cần nhập tên hoặc thông tin định danh.</div>',
        unsafe_allow_html=True
    )
    left, right = st.columns([1.15, 1])
    with left:
        with st.container(border=True):
            st.markdown("#### 📱 Thói quen sử dụng màn hình")
            screen_hours = st.number_input(
                "Thời gian sử dụng màn hình (giờ/ngày)",
                min_value=0.0, max_value=24.0, value=3.0, step=0.5,
            )
            before_sleep = st.radio(
                "Có sử dụng màn hình trong 1 giờ trước khi ngủ?",
                ["Không", "Có"], horizontal=True,
            )
    with right:
        with st.container(border=True):
            st.markdown("#### 🛏️ Lịch trình nghỉ ngơi")
            bedtime = st.time_input(
                "🌙 Giờ đi ngủ",
                value=pd.Timestamp("2026-01-01 22:00").time()
            )
            wake_time = st.time_input(
                "☀️ Giờ thức dậy",
                value=pd.Timestamp("2026-01-02 06:30").time()
            )

    sleep_hours = calculate_sleep_hours(bedtime, wake_time)
    if sleep_hours is None:
        st.warning("Không tính được thời lượng ngủ. Hãy kiểm tra giờ đi ngủ và giờ thức dậy.")
    else:
        st.markdown("#### 📌 Kết quả tự kiểm tra")
        msg = create_message(screen_hours, before_sleep, sleep_hours)
        m1, m2, m3 = st.columns(3)
        m1.metric("🛌 Thời lượng ngủ tính được", f"{sleep_hours:.1f} giờ")
        sleep_group = (
            "Dưới 8 giờ" if sleep_hours < 8
            else ("8–10 giờ" if sleep_hours <= 10 else "Trên 10 giờ")
        )
        m2.metric("🌙 Nhóm thời lượng ngủ", sleep_group)
        m3.metric("📱 Màn hình mỗi ngày", f"{screen_hours:.1f} giờ")

        if msg.startswith("Cần"):
            st.warning(f"💡 {msg}")
        else:
            st.success(f"🌟 {msg}")

        with st.container(border=True):
            st.markdown("**🌱 Gợi ý xây dựng thói quen tốt**")
            tip1, tip2, tip3 = st.columns(3)
            tip1.markdown("📵 **Giảm màn hình**\\n\\nDành thời gian thư giãn trước giờ ngủ.")
            tip2.markdown("🕙 **Ngủ đúng giờ**\\n\\nDuy trì lịch ngủ – thức tương đối ổn định.")
            tip3.markdown("☀️ **Thức dậy khỏe khoắn**\\n\\nBắt đầu ngày mới với vận động nhẹ.")
    st.caption(
        "Ngưỡng >4 giờ/ngày là quy ước học tập của dự án; mốc 8–10 giờ "
        "là khuyến nghị tham khảo phổ biến cho thanh thiếu niên 13–18 tuổi."
    )

# [7] PHÂN TÍCH DỮ LIỆU KHẢO SÁT
with tab2:
    st.markdown(
        '<div class="section-title">📊 Phân tích dữ liệu khảo sát lớp 9B</div>'
        '<div class="section-sub">Tải bảng khảo sát đã ẩn danh để kiểm tra, '
        'tổng hợp và trực quan hóa dữ liệu.</div>',
        unsafe_allow_html=True
    )
    with st.container(border=True):
        st.markdown("#### 📂 Tải dữ liệu khảo sát")
        st.caption(
            "Excel: sheet Du_lieu_khao_sat, bỏ qua 2 dòng đầu; "
            "CSV: hàng đầu tiên là tên cột."
        )
        uploaded = st.file_uploader(
            "Chọn file Excel hoặc CSV",
            type=["xlsx", "xls", "csv"],
            key="survey_upload"
        )

    if uploaded is not None:
        try:
            raw = read_uploaded_file(uploaded)
            df = prepare_dataframe(raw)
            st.success(f"Đã đọc {len(df)} dòng dữ liệu.")
            issues = validate_dataframe(df)
            if issues:
                st.warning("Cần rà soát dữ liệu trước khi sử dụng kết quả:")
                for issue in issues:
                    st.write(f"• {issue}")
            else:
                st.success("Kiểm tra cơ bản: chưa phát hiện cảnh báo.")

            summary = summarize_dataframe(df)
            st.markdown("#### 🧪 Các chỉ số nổi bật")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("👥 Số mã HS", summary["total"])
            k2.metric("📱 Màn hình >4 giờ/ngày", summary["screen_over"])
            k3.metric("🛌 Ngủ dưới 8 giờ", summary["sleep_under"])
            k4.metric("🌙 Dùng màn hình trước ngủ", summary["before_bed_yes"])

            stat_df = pd.DataFrame([
                ["Số HS có mã", summary["total"], "Đếm bản ghi có mã"],
                ["Số HS màn hình >4 giờ/ngày", summary["screen_over"], "Tương đương COUNTIF"],
                ["Số HS ngủ dưới 8 giờ", summary["sleep_under"], "Tương đương COUNTIF"],
                ["Số HS dùng màn hình trong 1 giờ trước ngủ", summary["before_bed_yes"], "Tương đương COUNTIF"],
                ["Tổng giờ màn hình của nhóm >4 giờ/ngày", round(summary["sum_screen_over"], 1), "Tương đương SUMIF"],
                ["Tổng giờ ngủ của nhóm ngủ dưới 8 giờ", round(summary["sum_sleep_under"], 1), "Tương đương SUMIF"],
            ], columns=["Chỉ tiêu", "Kết quả", "Cách tính"])

            st.markdown("#### 🧾 Bảng thống kê tổng hợp")
            st.dataframe(stat_df, use_container_width=True, hide_index=True)

            st.markdown("#### 📈 Biểu đồ các dấu hiệu cần quan tâm")
            chart_data = pd.DataFrame({
                "Nhóm": [
                    "Màn hình trên 4 giờ/ngày",
                    "Ngủ dưới 8 giờ",
                    "Dùng màn hình trước ngủ"
                ],
                "Số học sinh": [
                    summary["screen_over"],
                    summary["sleep_under"],
                    summary["before_bed_yes"]
                ],
            })
            st.bar_chart(
                chart_data.set_index("Nhóm"),
                use_container_width=True
            )

            with st.expander("🔍 Xem dữ liệu đã chuẩn hóa"):
                st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇️ Tải dữ liệu đã xử lý (CSV)",
                data=dataframe_to_csv(df),
                file_name="ket_qua_phan_tich_nhom_B.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"Không thể xử lý file: {exc}")
            st.caption(
                "Kiểm tra đúng tên sheet Du_lieu_khao_sat, hàng tiêu đề "
                "và tên các cột theo mẫu Nhóm B."
            )
    else:
        st.info(
            "Chưa tải file. Có thể dùng tab “Tự kiểm tra thói quen” "
            "để thử phép tính cá nhân."
        )

# [8] KIẾN THỨC & AN TOÀN
with tab3:
    st.markdown(
        '<div class="section-title">📘 Kiến thức nền và sử dụng an toàn</div>'
        '<div class="section-sub">Hiểu các khuyến nghị tham khảo, quy tắc dự án '
        'và giới hạn khi diễn giải dữ liệu.</div>',
        unsafe_allow_html=True
    )
    k1, k2, k3 = st.columns(3)
    for col, icon, title, desc in [
        (k1, "🛌", "Ngủ đủ giấc", "Thanh thiếu niên 13–18 tuổi thường được khuyến nghị ngủ khoảng 8–10 giờ mỗi ngày."),
        (k2, "📵", "Dùng màn hình hợp lý", "Hạn chế thiết bị sát giờ ngủ, dành thời gian thư giãn và nghỉ ngơi."),
        (k3, "🧠", "Đọc dữ liệu thận trọng", "Khảo sát tự báo cáo có thể có sai số; dữ liệu lớp học nhỏ không đại diện cho tất cả học sinh."),
    ]:
        col.markdown(
            f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
            f'<h3>{title}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("#### 🎯 Quy tắc của dự án")
    r1, r2, r3 = st.columns(3)
    r1.metric("📱 Màn hình", "> 4 giờ/ngày")
    r2.metric("🌙 Thời lượng ngủ", "< 8 giờ")
    r3.metric("📵 Trước khi ngủ", "Trong 1 giờ")
    st.info(
        "Các mốc trên là quy ước giáo dục của dự án hoặc khuyến nghị tham khảo; "
        "không phải công cụ chẩn đoán hay đánh giá sức khỏe cá nhân."
    )

    with st.expander("🤖 Vai trò của AI trong dự án"):
        st.write(
            "AI có thể hỗ trợ học sinh và giáo viên trong giai đoạn phát triển: "
            "gợi ý cấu trúc, tạo bản nháp code, giải thích lỗi. Khi ứng dụng đang chạy, "
            "các phép tính do Python thực hiện theo quy tắc lập trình; "
            "không có kết nối API AI trả phí."
        )

    st.warning(
        "Không dùng ứng dụng để chẩn đoán, xếp loại sức khỏe hoặc so sánh công khai "
        "từng học sinh. Nếu khó ngủ/mệt mỏi kéo dài, hãy trao đổi với cha mẹ/người "
        "chăm sóc hoặc nhân viên y tế."
    )
    st.caption(
        "Dữ liệu khảo sát cần được ẩn danh, chỉ thu thập và chia sẻ khi đã được phép."
    )

# [9] CHÂN TRANG
st.divider()
st.markdown(
    '<div class="footer">'
    '🌙 <b>DỮ LIỆU VÌ SỨC KHỎE HỌC ĐƯỜNG</b><br>'
    'Mini App STEM – Tin học 9 · <b>Nhóm B – Lớp 9C</b><br>'
    'Sử dụng màn hình có kiểm soát · Ngủ đủ giấc · Học tập hiệu quả<br>'
    '<span class="note">TVS · Sản phẩm học tập, không thay thế tư vấn y tế</span>'
    '</div>',
    unsafe_allow_html=True
)

