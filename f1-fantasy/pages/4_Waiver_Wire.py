import streamlit as st
from utils.database import (
    get_supabase,
    get_players,
    get_drivers,
    get_player_drivers,
    get_point_adjustments,
    process_waiver_pickup,
)

st.set_page_config(
    page_title="Waiver Wire | Max's F1 League",
    page_icon="🔄",
    layout="wide",
)

st.title("🔄 Waiver Wire")
st.caption("Pick up any undrafted driver. You must drop one of your current drivers. Costs 20 points.")

supabase = get_supabase()
players = get_players(supabase)
drivers = get_drivers(supabase)
all_picks = get_player_drivers(supabase)

# Build lookup structures
drafted_driver_ids = {p["driver_id"] for p in all_picks}
free_agents = [d for d in drivers if d["id"] not in drafted_driver_ids]

player_rosters = {}
for pick in all_picks:
    pid = pick["player_id"]
    player_rosters.setdefault(pid, []).append(pick)

# ── Current Rosters ───────────────────────────────────────────────────────────
st.subheader("Current Rosters")
roster_cols = st.columns(len(players))
for i, player in enumerate(players):
    with roster_cols[i]:
        st.markdown(f"**{player['name']}**")
        for pick in sorted(player_rosters.get(player["id"], []), key=lambda x: x["draft_round"]):
            mult = " ✦ 3×" if pick["draft_round"] == 4 else ""
            st.write(f"R{pick['draft_round']}{mult} — {pick['drivers']['name']}")

st.divider()

# ── Free Agents ───────────────────────────────────────────────────────────────
st.subheader("Available Free Agents")
if not free_agents:
    st.info("No free agents available — all drivers are on a team.")
else:
    fa_df_data = [{"Driver": d["name"], "Constructor": d["constructor"]} for d in free_agents]
    st.dataframe(fa_df_data, hide_index=True, use_container_width=True)

st.divider()

# ── Process Pickup (Admin only) ───────────────────────────────────────────────
st.subheader("Process a Pickup")

admin_pw = st.secrets.get("ADMIN_PASSWORD", "f1admin")
pw = st.text_input("Admin password required to process pickups", type="password")

if pw != admin_pw:
    st.warning("Enter the admin password to process a pickup.")
    st.stop()

if not free_agents:
    st.info("No free agents to pick up.")
    st.stop()

col1, col2, col3 = st.columns(3)

player_options = {p["name"]: p["id"] for p in players}
selected_player_name = col1.selectbox("Which player is picking up?", list(player_options.keys()))
selected_player_id = player_options[selected_player_name]

fa_options = {f"{d['name']} ({d['constructor']})": d["id"] for d in free_agents}
selected_fa_label = col2.selectbox("Driver to pick up", list(fa_options.keys()))
selected_fa_id = fa_options[selected_fa_label]

player_current = player_rosters.get(selected_player_id, [])
if not player_current:
    col3.warning(f"{selected_player_name} has no drivers to drop.")
    st.stop()

drop_options = {
    f"R{p['draft_round']} — {p['drivers']['name']}": p["driver_id"]
    for p in sorted(player_current, key=lambda x: x["draft_round"])
}
selected_drop_label = col3.selectbox("Driver to drop", list(drop_options.keys()))
selected_drop_id = drop_options[selected_drop_label]

st.warning(
    f"**{selected_player_name}** will drop **{selected_drop_label.split('— ')[1]}** "
    f"and pick up **{selected_fa_label.split(' (')[0]}**. "
    f"This costs **-20 points**."
)

if st.button("Confirm Pickup", type="primary"):
    try:
        process_waiver_pickup(supabase, selected_player_id, selected_fa_id, selected_drop_id)
        st.success("Pickup processed!")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()

# ── Pickup History ────────────────────────────────────────────────────────────
st.subheader("Pickup History")
all_adj = get_point_adjustments(supabase)
waiver_adj = [a for a in all_adj if a.get("reason", "").startswith("Waiver")]
if waiver_adj:
    for adj in waiver_adj:
        st.write(f"**{adj['players']['name']}** — {adj['reason']} ({adj['amount']:+d} pts)")
else:
    st.caption("No pickups yet.")
