import streamlit as st
import pandas as pd
from pathlib import Path
from utils.database import get_supabase, get_leaderboard

st.set_page_config(
    page_title="Leaderboard | Max's F1 League",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Leaderboard")


def get_image(folder, name):
    """Return image path if it exists, else None."""
    slug = name.lower().replace(" ", "_")
    for ext in ["jpg", "jpeg", "png", "webp"]:
        path = Path(f"images/{folder}/{slug}.{ext}")
        if path.exists():
            return str(path)
    return None


supabase = get_supabase()
player_totals, player_breakdown = get_leaderboard(supabase)

if not player_totals:
    st.info("No data yet. Set up teams in Admin, then enter some race results.")
    st.stop()

sorted_players = sorted(player_totals.items(), key=lambda x: -x[1]["total"])

# ── Player cards ──────────────────────────────────────────────────────────────
cols = st.columns(len(sorted_players))
medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

for i, (pid, p) in enumerate(sorted_players):
    with cols[i]:
        img = get_image("players", p["name"])
        if img:
            st.image(img, use_container_width=True)
        st.markdown(f"### {medals[i]} {p['name']}")
        st.metric("Points", p["total"])

st.divider()

# ── Driver breakdown ──────────────────────────────────────────────────────────
st.subheader("Driver Breakdown")

for pid, p in sorted_players:
    with st.expander(f"{p['name']}  —  {p['total']} pts"):
        for d in sorted(player_breakdown[pid], key=lambda x: -x["Total Pts"]):
            dcols = st.columns([1, 4, 3])
            img = get_image("drivers", d["Driver"])
            if img:
                dcols[0].image(img, width=60)
            else:
                dcols[0].write("")
            label = f"**{d['Driver']}**"
            if d["Round"] == 4:
                label += "  ✦ 3×"
            dcols[1].markdown(label)
            dcols[1].caption(f"Round {d['Round']} pick · {d['Base Pts']} base pts")
            dcols[2].metric("Points", d["Total Pts"])
