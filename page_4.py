import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="LỌC CODE THEO HÀNH TRÌNH", layout="centered")

st.title("🏷️ LỌC CODE THEO HÀNH TRÌNH")

# ✅ Cache hàm đọc file để tránh reload nhiều lần
@st.cache_data
def load_excel_hoa_don(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl", skiprows=4)

@st.cache_data
def load_excel_sms(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl")

# 📁 Tải file
uploaded_file_hoa_don = st.file_uploader("📁 Tải lên file hóa đơn", type=["xlsx"])
uploaded_file_sms = st.file_uploader("📁 Tải lên file sms", type=["xlsx"])

if uploaded_file_hoa_don:
    with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
        df_hoa_don = load_excel_hoa_don(uploaded_file_hoa_don)

    if uploaded_file_sms:
        with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
            df_sms = load_excel_sms(uploaded_file_sms)
            df_sms["Phone"] = df_sms["Phone"].astype(str).str.zfill(10)

        code_input = st.text_input(
            "🔢 Nhập các mã cần lọc (cách nhau bằng dấu phẩy)",
            value=""
        )
        target_codes = {code.strip() for code in code_input.split(",") if code.strip().isdigit()}

        # 👇 Nhấn nút để bắt đầu lọc dữ liệu
        if st.button("📥 Lọc dữ liệu"):

            # Lọc theo mã thẻ GG
            def contains_code(ma_gg):
                if pd.isna(ma_gg):
                    return False
                items = [x.strip().split("-")[0] for x in str(ma_gg).split(",")]
                return any(code in target_codes for code in items)
            if len(target_codes) > 0:
                df_hoa_don = df_hoa_don[df_hoa_don['Mã thẻ GG'].apply(contains_code)]

            # Hiển thị dữ liệu gốc
            st.subheader("📋 Danh sách hóa đơn")
            st.dataframe(df_hoa_don, use_container_width=True)

            st.subheader("📋 Danh sách SMS")
            st.dataframe(df_sms, use_container_width=True)

            # Đảm bảo cột Phone là kiểu chuỗi
            df_sms["Phone"] = df_sms["Phone"].astype(str)

            # Điều kiện: không đúng định dạng bắt đầu bằng 0 và có 10 chữ số
            invalid_phones = df_sms[~df_sms["Phone"].str.match(r"^0\d{9}$")]

            if len(invalid_phones) > 0:
                # Hiển thị kết quảSĐT
                st.subheader("📋 Danh sách SMS không hợp lệ")
                st.dataframe(invalid_phones)

            df_trung_lap = df_hoa_don.merge(df_sms, left_on="SĐT", right_on="Phone", how="inner")
            tong_doanh_thu = df_trung_lap['Doanh thu tính lương'].sum()
            st.subheader("📋 Danh sách Khớp")
            st.dataframe(df_trung_lap, use_container_width=True)

            df_duplicate_phones = df_trung_lap[df_trung_lap.duplicated(subset=["Phone"], keep=False)]
            st.subheader("📋 Danh sách KH mua nhiều lần")
            st.dataframe(df_duplicate_phones, use_container_width=True)


            # Xóa các dòng trùng số điện thoại, giữ lại dòng đầu tiên
            df_trung_lap_unique = df_trung_lap.drop_duplicates(subset=["Phone"], keep="first")

            st.subheader("📋 Danh sách KH nhận mã và đi mua hàng")
            st.dataframe(df_trung_lap_unique, use_container_width=True)

            # Metric
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🧮 Số khách nhận mã và đi mua", len(df_trung_lap_unique))
            with col2:
                st.metric("💰 Tổng doanh thu", f"{tong_doanh_thu:,.0f} VND")

            # Lọc theo mã giảm giá
            df_filtered = df_trung_lap[df_trung_lap['Mã thẻ GG'].notna() & (df_trung_lap['Mã thẻ GG'].str.strip() != '')]

            tong_doanh_thu_gg = df_filtered['Doanh thu tính lương'].sum()

            st.subheader("📋 Danh sách KH có sử dụng mã giảm giá")
            st.dataframe(df_filtered, use_container_width=True)

            # df_duplicate_phones_mgg = df_matched[df_matched.duplicated(subset=["Phone"], keep=False)]
            # if len(df_duplicate_phones_mgg) > 0:
            #     st.subheader("📋 Danh sách KH sử dụng mã giảm giá nhiều lần")
            #     st.dataframe(df_duplicate_phones_mgg, use_container_width=True)
            #
            # df_matched_unique = df_matched.drop_duplicates(subset=["Phone"], keep="first")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🧮 Số khách nhận mã và sử dụng", len(df_filtered))
            with col2:
                st.metric("💰 Tổng doanh thu", f"{tong_doanh_thu_gg:,.0f} VND")
