import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.express as px
from collections import OrderedDict

st.set_page_config(page_title="SỐ NGƯỜI DÙNG CODE", layout="centered")

st.title("🧑‍🤝‍🧑 SỐ NGƯỜI DÙNG CODE")

# ✅ Cache hàm đọc file để tránh reload nhiều lần
@st.cache_data
def load_excel(uploaded_file):
    return pd.read_excel(uploaded_file, engine="openpyxl", skiprows=4)

# 📁 Tải file
uploaded_file = st.file_uploader("📁 Tải lên file Excel", type=["xlsx"])
uploaded_file_data_kv = st.file_uploader("📁 Tải lên file danh sách cửa hàng", type=["xlsx"])

if uploaded_file:
    with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
        df = load_excel(uploaded_file)

    if uploaded_file_data_kv:
        with st.spinner("⏳ Đang đọc dữ liệu... Chờ xíu nha vk 😄"):
            kv_df = pd.read_excel(uploaded_file_data_kv, engine="openpyxl")
            kv_df = kv_df.drop_duplicates()

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
                    start_date_input = st.date_input("🗓️ Từ ngày", value=datetime(2025, 5, 1).date())
                with col2:
                    end_date_input = st.date_input("🗓️ Đến ngày", value=datetime(2025, 5, 10).date())

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

                def contains_code(ma_gg):
                    if pd.isna(ma_gg):
                        return False
                    items = [x.strip().split("-")[0] for x in str(ma_gg).split(",")]
                    return any(code in target_codes for code in items)

                df_final = df_filtered_date[df_filtered_date['Mã thẻ GG'].apply(contains_code)]

                # ❌ Loại bỏ dòng có Mã thẻ GG trống hoặc rỗng
                df_final = df_final[df_final['Mã thẻ GG'].notna()]
                df_final = df_final[df_final['Mã thẻ GG'].str.strip() != '']

                # 👉 Gộp Mã thẻ GG theo SĐT
                def merge_and_dedup(values):
                    codes = []
                    for val in values.dropna():
                        codes.extend([code.strip() for code in val.split(",")])
                    return ', '.join(sorted(set(codes)))


                df_merged = (
                    df_final
                    .groupby('SĐT')['Mã thẻ GG']
                    .apply(merge_and_dedup)
                    .reset_index()
                )

                def count_matching_codes(ma_gg):
                    if pd.isna(ma_gg):
                        return 0
                    codes = {x.strip().split("-")[0] for x in str(ma_gg).split(",")}
                    return len(codes.intersection(target_codes))

                df_merged['matching_count'] = df_merged['Mã thẻ GG'].apply(count_matching_codes)

                max_match = len(target_codes)
                matching_stats = OrderedDict()

                for k in range(1, max_match):
                    matching_stats[f"Dùng đúng {k} mã"] = (df_merged['matching_count'] == k).sum()

                # Record dùng tất cả mã
                matching_stats[f"Dùng tất cả {max_match} mã"] = (df_merged['matching_count'] == max_match).sum()

                st.subheader("📋 Dữ liệu sau khi lọc")
                st.dataframe(df_final, use_container_width=True)

                st.subheader("📋 Dữ liệu sau khi gộp mã")
                st.dataframe(df_merged, use_container_width=True)

                # chart
                df_chart = pd.DataFrame({
                    "Số mã khớp": list(matching_stats.keys()),
                    "Số người sử dụng": list(matching_stats.values())
                })

                fig = px.bar(df_chart, x="Số mã khớp", y="Số người sử dụng",
                             title="Thống kê số người sử dụng theo số mã trùng khớp")
                st.plotly_chart(fig, use_container_width=True)

                # Show filter data
                st.subheader("📊 Thống kê theo số lượng mã khớp")

                for label, count in matching_stats.items():
                    st.write(f"🔸 {label}: {count} người")


                # Show sum
                st.subheader("📊 Tổng số người sử dụng mã")
                st.write(f"🔸 {len(df_merged)}")

                # Tổng hợp theo khu vực
                df_merged_kv = df_final.merge(
                    kv_df,
                    left_on="Chi nhánh",
                    right_on="Chuyển data cho CH",
                    how="left"
                )
                df_unique_customers = df_merged_kv.drop_duplicates(subset=["SĐT", "KV sau chuyển data"])
                st.subheader("📍 Dữ liệu sau khi gán KV")
                st.dataframe(df_unique_customers, use_container_width=True)

                # Kiểm tra xem có dữ liệu bất thng hay không
                # test_duplicate = df_unique_customers["SĐT"].value_counts().loc[lambda x: x > 1]
                # st.subheader("📋 Danh sách KH bị lặp")
                # st.dataframe(test_duplicate, use_container_width=True)

                summary_df = df_unique_customers.groupby("KV sau chuyển data").agg(
                    So_khach_hang=("SĐT", "count")
                ).reset_index().rename(columns={"KV sau chuyển data": "Khu vực"})
                st.subheader("📊 Thống kê theo Khu vực")
                st.dataframe(summary_df, use_container_width=True)
