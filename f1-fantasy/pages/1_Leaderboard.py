import streamlit as st
import pandas as pd
from utils.database import get_supabase, get_leaderboard

st.set_page_config(
    page_title="Leaderboard | Max's F1 League",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Leaderboard")

supabase = get_supabase()
player_totals, player_breakdown = get_leaderboard(supabase)

if not player_totals:
    st.info("No data yet. Set up teams in Admin, then enter some race results.")
    st.stop()

# Overall standings
sorted_players = sorted(player_totals.items(), key=lambda x: -x[1]["total"])

standings = pd.DataFrame(
    [
        {"Pos": i + 1, "Player": p["name"], "Total Points": p["total"]}
        for i, (_, p) in enumerate(sorted_players)
    ]
)

st.dataframe(standings, hide_index=True, use_container_width=True)

st.divider()
st.subheader("Driver Breakdown")

for pid, p in sorted_players:
    with st.expander(f"{p['name']}  —  {p['total']} pts"):
        df = pd.DataFrame(player_breakdown[pid]).sort_values("Total Pts", ascending=False)
        st.dataframe(df, hide_index=True, use_container_width=True)
