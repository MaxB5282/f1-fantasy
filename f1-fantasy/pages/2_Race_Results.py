import streamlit as st
import pandas as pd
from utils.database import get_supabase, get_races, get_race_results, get_sprint_results
from utils.points import get_driver_points_breakdown, get_sprint_points_breakdown

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
sprint_results = get_sprint_results(supabase, race_id)

if not results and not sprint_results:
    st.info("No results entered for this race yet.")
    st.stop()

if results:
    st.subheader("Race")
    rows = []
    for r in results:
        bd = get_driver_points_breakdown(
            r["qualifying_pos"], r["grid_pos"], r["race_pos"],
            dnf=r.get("dnf", False), fastest_lap=r.get("fastest_lap", False),
        )
        rows.append({
            "Driver": r["drivers"]["name"],
            "Constructor": r["drivers"]["constructor"],
            "Qual Pos": r["qualifying_pos"],
            "Grid Pos": r["grid_pos"],
            "Finish": "DNF" if r["dnf"] else r["race_pos"],
            "Qual Pts": bd["Qual Pts"],
            "Finish Pts": bd["Finish Pts"],
            "Pos Pts": bd["Pos Pts"],
            "FL Pts": bd["FL Pts"],
            "Total": r["base_points"],
        })
    df = pd.DataFrame(rows).sort_values("Total", ascending=False)
    st.dataframe(df, hide_index=True, use_container_width=True)

if sprint_results:
    st.subheader("Sprint")
    sprint_rows = []
    for r in sprint_results:
        bd = get_sprint_points_breakdown(
            r["grid_pos"], r["finish_pos"],
            fastest_lap=r.get("fastest_lap", False), dnf=r.get("dnf", False),
        )
        sprint_rows.append({
            "Driver": r["drivers"]["name"],
            "Constructor": r["drivers"]["constructor"],
            "Grid Pos": r["grid_pos"],
            "Finish": "DNF" if r["dnf"] else r["finish_pos"],
            "Finish Pts": bd["Finish Pts"],
            "Pos Pts": bd["Pos Pts"],
            "FL Pts": bd["FL Pts"],
            "Total": r["base_points"],
        })
    sprint_df = pd.DataFrame(sprint_rows).sort_values("Total", ascending=False)
    st.dataframe(sprint_df, hide_index=True, use_container_width=True)
