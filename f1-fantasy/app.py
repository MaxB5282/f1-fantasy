import streamlit as st

st.set_page_config(
    page_title="Max's F1 League",
    page_icon="🏎️",
    layout="wide",
)

st.title("🏎️ Max's F1 League")
st.caption("5 players · 4 drivers each · one champion")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏁 Regular Race")
    st.markdown("**Qualifying**")
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11+"],
            "Points":   [10,    9,    8,    7,    6,    5,    4,    3,    2,    1,     0],
        },
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**Race Finish**")
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11+"],
            "Points":   [25,   18,   15,   12,   10,   8,    6,    4,    2,    1,     0],
        },
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**Other**")
    st.dataframe(
        {
            "Event":  ["Position gained", "Position lost", "DNF"],
            "Points": ["+2 each", "-1 each", "-5"],
        },
        hide_index=True,
        use_container_width=True,
    )

with col2:
    st.subheader("⚡ Sprint Race")
    st.markdown("**Sprint Finish**")
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9+", "DNF"],
            "Points":   [8,    7,    6,    5,    4,    3,    2,    1,   0,     -10],
        },
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**Other**")
    st.dataframe(
        {
            "Event":  ["Position gained", "Position lost", "Fastest lap", "DNF"],
            "Points": ["+1 each", "-1 each", "+5", "-10"],
        },
        hide_index=True,
        use_container_width=True,
    )

with col3:
    st.subheader("📋 League Rules")
    st.dataframe(
        {
            "Rule":   [
                "Drivers per team",
                "4th round draft pick",
                "Waiver pickup penalty",
            ],
            "Detail": [
                "4",
                "3× multiplier on all points",
                "-20 pts",
            ],
        },
        hide_index=True,
        use_container_width=True,
    )
