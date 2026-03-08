import streamlit as st

st.set_page_config(
    page_title="Rules | Max's F1 League",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Scoring Rules")

with st.expander("🏁 Regular Race — Qualifying", expanded=False):
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11+"],
            "Points":   [10,    9,    8,    7,    6,    5,    4,    3,    2,    1,     0],
        },
        hide_index=True,
        use_container_width=True,
    )

with st.expander("🏁 Regular Race — Finish", expanded=False):
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11+"],
            "Points":   [25,   18,   15,   12,   10,   8,    6,    4,    2,    1,     0],
        },
        hide_index=True,
        use_container_width=True,
    )

with st.expander("🏁 Regular Race — Bonuses & Penalties", expanded=False):
    st.dataframe(
        {
            "Event":  ["Position gained", "Position lost", "Fastest lap", "DNF"],
            "Points": ["+2 each (max +10)", "-1 each", "+3", "-5"],
        },
        hide_index=True,
        use_container_width=True,
    )

with st.expander("⚡ Sprint Race — Finish", expanded=False):
    st.dataframe(
        {
            "Position": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9+"],
            "Points":   [8,    7,    6,    5,    4,    3,    2,    1,   0],
        },
        hide_index=True,
        use_container_width=True,
    )

with st.expander("⚡ Sprint Race — Bonuses & Penalties", expanded=False):
    st.dataframe(
        {
            "Event":  ["Position gained", "Position lost", "Fastest lap", "DNF"],
            "Points": ["+1 each", "-1 each", "+5", "-10"],
        },
        hide_index=True,
        use_container_width=True,
    )

with st.expander("📋 League Rules", expanded=False):
    st.dataframe(
        {
            "Rule": [
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
