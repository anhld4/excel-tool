import streamlit as st

# Define the pages with new icons
page_1 = st.Page("page_1.py", title="SỐ BILL - DOANH THU THEO ĐẦU CODE", icon="📦")     # Gợi ý: Hóa đơn, sản phẩm
page_2 = st.Page("page_2.py", title="CHI TIẾT SỐ CODE SỬ DỤNG", icon="📋")              # Gợi ý: Danh sách chi tiết
page_3 = st.Page("page_3.py", title="SỐ NGƯỜI DÙNG CODE", icon="🧑‍🤝‍🧑")               # Gợi ý: Người dùng

# Set up navigation
pg = st.navigation([page_1, page_2, page_3])

# Run the selected page
pg.run()
