import streamlit as st

st.set_page_config(
    page_title="Max's F1 League",
    page_icon="🏎️",
    layout="wide",
)

st.title("🏎️ Max's F1 League")
st.markdown("---")

st.markdown(
    """
Welcome to the official home of **Max's Fantasy F1 League** — 5 players, 4 drivers each, one champion.

### Navigate
- **Leaderboard** — Overall standings and driver breakdowns
- **Race Results** — Lap-by-lap points per race
- **Admin** — Enter race results *(password required)*

### Points System
| Category | Points |
|---|---|
| Qualifying P1–P10 | 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 |
| Race P1–P10 | 25, 18, 15, 12, 10, 8, 6, 4, 2, 1 |
| Each position gained (overtakes) | +2 pts |
| 4th round draft pick | **3× multiplier** on all points |
"""
)
