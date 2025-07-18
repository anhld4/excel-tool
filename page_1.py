import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="SỐ BILL - DOANH THU THEO ĐẦU CODE", layout="centered")

st.title("📦 SỐ BILL - DOANH THU THEO ĐẦU CODE")

# ✅ Cache hàm đọc file để tránh reload nhiều lần
@st.cache_data
def load_excel_data(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl", skiprows=4)

# 📁 Tải file
uploaded_file_data = st.file_uploader("📁 Tải lên file hóa đơn", type=["xlsx"])
uploaded_file_data_kv = st.file_uploader("📁 Tải lên file danh sách cửa hàng", type=["xlsx"])

if uploaded_file_data:
    with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
        df = load_excel_data(uploaded_file_data)
    if uploaded_file_data_kv:
        with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
            kv_df = pd.read_excel(uploaded_file_data_kv, engine="openpyxl")
            kv_df = kv_df.drop_duplicates()

        st.subheader("📋 Dữ liệu gốc")
        st.dataframe(df, use_container_width=True)

        st.subheader("📋 Danh sách cửa hàng")
        st.dataframe(kv_df, use_container_width=True)

        # Kiểm tra xem có dữ liệu bất thng hay không
        # test_duplicate = kv_df["Chuyển data cho CH"].value_counts().loc[lambda x: x > 1]
        # st.subheader("📋 Danh sách cửa hàng bị lặp")
        # st.dataframe(test_duplicate, use_container_width=True)

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

                # Lọc theo mã thẻ GG
                def contains_code(ma_gg):
                    if pd.isna(ma_gg):
                        return False
                    items = [x.strip().split("-")[0] for x in str(ma_gg).split(",")]
                    return any(code in target_codes for code in items)

                df_final = df_filtered_date[df_filtered_date['Mã thẻ GG'].apply(contains_code)]
                tong_doanh_thu = df_final['Doanh thu tính lương'].sum()

                # ✅ Kết quả
                st.subheader("📌 Dữ liệu sau khi lọc")
                st.dataframe(df_final, use_container_width=True)

                # Metric
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🧮 SỐ HÓA ĐƠN DÙNG CODE", len(df_final))
                with col2:
                    st.metric("💰 DOANH THU CODE", f"{tong_doanh_thu:,.0f} VND")

                # Tổng hợp theo khu vực
                df_merged = df_final.copy()
                df_merged["Chi nhánh_lower"] = df_merged["Chi nhánh"].str.lower()
                kv_df["CH_lower"] = kv_df["Chuyển data cho CH"].str.lower()

                df_merged = df_merged.merge(
                    kv_df,
                    left_on="Chi nhánh_lower",
                    right_on="CH_lower",
                    how="left"
                )

                st.subheader("📍 Dữ liệu sau khi gán KV")

                st.dataframe(df_merged, use_container_width=True)

                summary_df = df_merged.groupby("KV sau chuyển data").agg(
                    So_hoa_don=("Doanh thu tính lương", "count"),
                    Doanh_thu=("Doanh thu tính lương", "sum")
                ).reset_index().rename(columns={"KV sau chuyển data": "Khu vực"})
                st.subheader("📊 Thống kê theo Khu vực")
                st.dataframe(summary_df, use_container_width=True)





