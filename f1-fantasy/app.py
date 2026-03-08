import streamlit as st

pages = st.navigation([
    st.Page("pages/1_Leaderboard.py",  title="Leaderboard",  icon="🏆", default=True),
    st.Page("pages/2_Race_Results.py", title="Race Results",  icon="🏁"),
    st.Page("pages/3_Admin.py",        title="Admin",         icon="⚙️"),
    st.Page("pages/4_Waiver_Wire.py",  title="Waiver Wire",   icon="🔄"),
    st.Page("pages/5_Rules.py",        title="Rules",         icon="📋"),
])

pages.run()
