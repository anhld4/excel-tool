import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.express as px
from collections import OrderedDict

st.set_page_config(page_title="CHI TIẾT SỐ CODE SỬ DỤNG", layout="centered")

st.title("📋 CHI TIẾT SỐ CODE SỬ DỤNG")

# ✅ Cache hàm đọc file để tránh reload nhiều lần
@st.cache_data
def load_excel(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl", skiprows=4)

# 📁 Tải file
uploaded_file = st.file_uploader("📁 Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
        df = load_excel(uploaded_file)

    st.subheader("📋 Dữ liệu gốc")
    st.dataframe(df, use_container_width=True)

    required_columns = ['Ngày', 'Mã thẻ GG']
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ File thiếu một trong các cột: {required_columns}")
    else:
        df['Ngày'] = pd.to_datetime(df['Ngày'], errors='coerce')

        # Giao diện nhập điều kiện lọc
        with st.expander("⚙️ Bộ lọc", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                start_of_month = datetime.today().replace(day=1).date()
                start_date_input = st.date_input("🗓️ Từ ngày", value=start_of_month)
            with col2:
                end_date_input = st.date_input("🗓️ Đến ngày", value=datetime.today().date())

            code_input = st.text_input(
                "🔢 Nhập các mã cần lọc (cách nhau bằng dấu phẩy)",
                value="1394,1395,1396"
            )
            target_codes = {code.strip() for code in code_input.split(",") if code.strip().isdigit()}

        # 👇 Nhấn nút để bắt đầu lọc dữ liệu
        if st.button("📥 Lọc dữ liệu"):
            start_date = datetime.combine(start_date_input, time(0, 0, 0))
            end_date = datetime.combine(end_date_input, time(23, 59, 59))

            # Lọc theo khoảng ngày
            df_filtered_date = df[df['Ngày'].between(start_date, end_date)]

            def count_matching_codes(ma_gg):
                if pd.isna(ma_gg):
                    return 0
                codes = {x.strip().split("-")[0] for x in str(ma_gg).split(",")}
                return len(codes.intersection(target_codes))

            df_filtered_date['matching_count'] = df_filtered_date['Mã thẻ GG'].apply(count_matching_codes)
            df_final = df_filtered_date[df_filtered_date['matching_count'] > 0]

            st.subheader("📋 Dữ liệu sau khi lọc")
            st.dataframe(df_final, use_container_width=True)

            max_match = len(target_codes)
            matching_stats = OrderedDict()

            for k in range(1, max_match):
                matching_stats[f"Dùng đúng {k} mã"] = (df_final['matching_count'] == k).sum()

            # Record dùng tất cả mã
            matching_stats[f"Dùng tất cả {max_match} mã"] = (df_final['matching_count'] == max_match).sum()

            # chart
            df_chart = pd.DataFrame({
                "Số mã khớp": list(matching_stats.keys()),
                "Hóa đơn": list(matching_stats.values())
            })

            fig = px.bar(df_chart, x="Số mã khớp", y="Hóa đơn", title="Thống kê hóa đơn theo số code trùng khớp")
            st.plotly_chart(fig, use_container_width=True)

            # Show filter data
            st.subheader("📊 Thống kê theo số lượng mã khớp")

            for label, count in matching_stats.items():
                st.write(f"🔸 {label}: {count} hóa đơn")


