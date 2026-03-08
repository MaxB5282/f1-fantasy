import streamlit as st
import pandas as pd
from utils.database import get_supabase, get_races, get_race_results

st.set_page_config(
    page_title="Race Results | Max's F1 League",
    page_icon="🏁",
    layout="wide",
)

st.title("🏁 Race Results")

supabase = get_supabase()
races = get_races(supabase)

if not races:
    st.info("No race results yet. Check back after the first race!")
    st.stop()

race_labels = [f"Round {r['round_number']}: {r['name']}" for r in races]
selected_idx = st.selectbox("Select Race", range(len(race_labels)), format_func=lambda i: race_labels[i])
race_id = races[selected_idx]["id"]

results = get_race_results(supabase, race_id)

if not results:
    st.info("No results entered for this race yet.")
    st.stop()

rows = []
for r in results:
    rows.append(
        {
            "Driver": r["drivers"]["name"],
            "Constructor": r["drivers"]["constructor"],
            "Qual Pos": r["qualifying_pos"],
            "Grid Pos": r["grid_pos"],
            "Finish": "DNF" if r["dnf"] else r["race_pos"],
            "FL": "⚡" if r.get("fastest_lap") else "",
            "Points": r["base_points"],
        }
    )

df = pd.DataFrame(rows).sort_values("Points", ascending=False)
st.dataframe(df, hide_index=True, use_container_width=True)
