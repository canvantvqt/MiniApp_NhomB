"""Các hàm xử lý dữ liệu độc lập với giao diện Streamlit.

Học sinh có thể đọc module này trước để hiểu các phép tính cốt lõi.
Ứng dụng không gọi dịch vụ AI hoặc API trả phí khi đang chạy.
"""
from __future__ import annotations
import math
import pandas as pd

REQUIRED_COLUMNS = [
    "Mã HS",
    "Thời gian sử dụng màn hình (giờ/ngày)",
    "Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)",
    "Giờ đi ngủ",
    "Giờ thức dậy",
    "Thời lượng ngủ (giờ)",
    "Tự đánh giá ngủ đủ? (Có/Không)",
]

SCREEN_LIMIT_HOURS = 4.0  # Ngưỡng minh họa của dự án, không phải chuẩn y tế.
SLEEP_MIN_HOURS = 8.0
SLEEP_MAX_HOURS = 10.0

def _to_hour(value):
    """Đổi giá trị thời gian Excel/pandas hoặc chuỗi HH:MM thành số phút trong ngày."""
    if pd.isna(value):
        return None
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value.hour * 60 + value.minute
    text = str(value).strip()
    if not text:
        return None
    # Hỗ trợ dạng 22:30 hoặc 22:30:00.
    try:
        parts = text.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        return hour * 60 + minute
    except (ValueError, IndexError):
        return None

def calculate_sleep_hours(bedtime, wake_time):
    """Tính số giờ ngủ từ giờ đi ngủ đến giờ thức dậy, kể cả qua nửa đêm."""
    start, end = _to_hour(bedtime), _to_hour(wake_time)
    if start is None or end is None or start == end:
        return None
    minutes = (end - start) % (24 * 60)
    if minutes <= 0:
        return None
    return round(minutes / 60, 2)

def classify_screen_time(hours):
    """Phân nhóm thời gian màn hình theo ngưỡng học tập > 4 giờ/ngày."""
    if pd.isna(hours):
        return "Chưa đủ dữ liệu"
    return "Trên 4 giờ/ngày" if float(hours) > SCREEN_LIMIT_HOURS else "Không quá 4 giờ/ngày"

def classify_sleep(hours):
    """Phân nhóm thời lượng ngủ theo mốc tham khảo 8–10 giờ cho tuổi 13–18."""
    if pd.isna(hours):
        return "Chưa đủ dữ liệu"
    value = float(hours)
    if value < SLEEP_MIN_HOURS:
        return "Dưới 8 giờ"
    if value <= SLEEP_MAX_HOURS:
        return "8–10 giờ"
    return "Trên 10 giờ"

def create_message(screen_hours, before_sleep, sleep_hours):
    """Tạo thông điệp giáo dục theo quy tắc IF/OR; không phải chẩn đoán."""
    if pd.isna(screen_hours) or before_sleep not in ("Có", "Không") or pd.isna(sleep_hours):
        return "Chưa đủ dữ liệu để tạo thông điệp"
    if float(screen_hours) > SCREEN_LIMIT_HOURS or before_sleep == "Có" or float(sleep_hours) < SLEEP_MIN_HOURS:
        return "Cần xem lại thói quen màn hình và giấc ngủ"
    return "Thói quen tương đối phù hợp theo quy ước dự án"

def prepare_dataframe(raw_df):
    """Chuẩn hóa dữ liệu đầu vào, tính lại cột suy ra và kiểm tra lỗi cơ bản."""
    df = raw_df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing))

    # Chỉ giữ các trường đã thống nhất trong bảng Excel Nhóm B.
    df = df[REQUIRED_COLUMNS].copy()
    df["Mã HS"] = df["Mã HS"].astype("string").str.strip()
    df["Thời gian sử dụng màn hình (giờ/ngày)"] = pd.to_numeric(
        df["Thời gian sử dụng màn hình (giờ/ngày)"], errors="coerce"
    )
    yes_no_cols = [
        "Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)",
        "Tự đánh giá ngủ đủ? (Có/Không)",
    ]
    for col in yes_no_cols:
        df[col] = df[col].astype("string").str.strip().str.capitalize()

    # Tính lại từ giờ đi ngủ/thức dậy để không phụ thuộc cached formula trong Excel.
    sleep_values = [
        calculate_sleep_hours(bed, wake)
        for bed, wake in zip(df["Giờ đi ngủ"], df["Giờ thức dậy"])
    ]
    df["Thời lượng ngủ (giờ)"] = sleep_values
    screen_col = "Thời gian sử dụng màn hình (giờ/ngày)"
    before_col = yes_no_cols[0]
    df["Nhóm thời gian màn hình"] = df[screen_col].apply(classify_screen_time)
    df["Nhóm thời lượng ngủ"] = df["Thời lượng ngủ (giờ)"].apply(classify_sleep)
    df["Thông điệp gợi ý"] = [
        create_message(s, b, h)
        for s, b, h in zip(df[screen_col], df[before_col], df["Thời lượng ngủ (giờ)"])
    ]
    return df

def validate_dataframe(df):
    """Trả về danh sách cảnh báo dữ liệu, không tự sửa/đoán câu trả lời."""
    issues = []
    id_col = "Mã HS"
    if df[id_col].isna().any() or (df[id_col].astype("string").str.len() == 0).any():
        issues.append("Có dòng chưa có mã học sinh.")
    duplicates = df.loc[df[id_col].notna(), id_col].duplicated()
    if duplicates.any():
        issues.append("Có mã học sinh bị trùng.")
    screen_col = "Thời gian sử dụng màn hình (giờ/ngày)"
    invalid_screen = df[screen_col].notna() & ~df[screen_col].between(0, 24)
    if invalid_screen.any():
        issues.append(f"Có {int(invalid_screen.sum())} giá trị thời gian màn hình ngoài khoảng 0–24 giờ.")
    for col in [
        "Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)",
        "Tự đánh giá ngủ đủ? (Có/Không)",
    ]:
        bad = df[col].notna() & ~df[col].isin(["Có", "Không"])
        if bad.any():
            issues.append(f"Cột “{col}” có giá trị khác Có/Không.")
    if df["Thời lượng ngủ (giờ)"].isna().any():
        issues.append(f"Có {int(df['Thời lượng ngủ (giờ)'].isna().sum())} dòng chưa tính được thời lượng ngủ.")
    if df["Thời lượng ngủ (giờ)"].notna().any() and (df["Thời lượng ngủ (giờ)"] > 16).any():
        issues.append("Có thời lượng ngủ trên 16 giờ; cần xác minh lại giờ đi ngủ/thức dậy.")
    return issues

def summarize_dataframe(df):
    """Tạo bảng thống kê tổng hợp, tương đương các phép COUNTIF và SUMIF."""
    screen_col = "Thời gian sử dụng màn hình (giờ/ngày)"
    sleep_col = "Thời lượng ngủ (giờ)"
    screen_group = "Nhóm thời gian màn hình"
    sleep_group = "Nhóm thời lượng ngủ"
    return {
        "total": int(df["Mã HS"].notna().sum()),
        "screen_over": int((df[screen_group] == "Trên 4 giờ/ngày").sum()),
        "sleep_under": int((df[sleep_group] == "Dưới 8 giờ").sum()),
        "before_bed_yes": int((df["Có sử dụng màn hình trong 1 giờ trước khi ngủ? (Có/Không)"] == "Có").sum()),
        "sum_screen_over": float(df.loc[df[screen_group] == "Trên 4 giờ/ngày", screen_col].sum()),
        "sum_sleep_under": float(df.loc[df[sleep_group] == "Dưới 8 giờ", sleep_col].sum()),
    }
