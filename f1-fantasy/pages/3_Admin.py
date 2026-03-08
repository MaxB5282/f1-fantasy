import streamlit as st
import pandas as pd
from utils.database import (
    get_supabase,
    get_players,
    get_drivers,
    get_races,
    get_player_drivers,
    get_race_results,
    get_sprint_results,
    save_race_results,
    save_sprint_results,
)
from utils.points import calculate_driver_points, calculate_sprint_points

st.set_page_config(
    page_title="Admin | Max's F1 League",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Admin")

# Password gate
admin_pw = st.secrets.get("ADMIN_PASSWORD", "f1admin")
pw = st.text_input("Admin password", type="password")
if pw != admin_pw:
    st.warning("Enter the admin password to continue.")
    st.stop()

supabase = get_supabase()

tab1, tab2, tab3, tab4 = st.tabs(["Enter Race Results", "Enter Sprint Results", "Add Race", "Set Teams"])

# ── Tab 1: Enter Race Results ─────────────────────────────────────────────────
with tab1:
    st.subheader("Enter Race Results")
    races = get_races(supabase)
    drivers = get_drivers(supabase)

    if not races:
        st.info("Add a race first in the 'Add Race' tab.")
    elif not drivers:
        st.warning("No drivers found. Run setup.sql in your Supabase dashboard.")
    else:
        race_labels = [f"Round {r['round_number']}: {r['name']}" for r in races]
        selected_idx = st.selectbox(
            "Select Race",
            range(len(race_labels)),
            format_func=lambda i: race_labels[i],
        )
        race_id = races[selected_idx]["id"]

        # Load existing results for pre-filling
        existing = {r["driver_id"]: r for r in get_race_results(supabase, race_id)}

        st.write(
            "Edit the table below. **Qual Pos** = qualifying result, "
            "**Grid Pos** = actual starting position (may differ due to penalties), "
            "**Race Pos** = finishing position. Check **DNF** if the driver didn't finish."
        )

        # Build editable dataframe
        rows = []
        for d in sorted(drivers, key=lambda x: x["name"]):
            ex = existing.get(d["id"], {})
            rows.append(
                {
                    "_driver_id": d["id"],
                    "Driver": d["name"],
                    "Constructor": d["constructor"],
                    "Qual Pos": ex.get("qualifying_pos") or 10,
                    "Grid Pos": ex.get("grid_pos") or 10,
                    "Race Pos": ex.get("race_pos") or 10,
                    "FL": ex.get("fastest_lap") or False,
                    "DNF": ex.get("dnf") or False,
                }
            )

        edited = st.data_editor(
            pd.DataFrame(rows),
            column_config={
                "_driver_id": None,  # hidden
                "Driver": st.column_config.TextColumn(disabled=True),
                "Constructor": st.column_config.TextColumn(disabled=True),
                "Qual Pos": st.column_config.NumberColumn(min_value=1, max_value=22, step=1),
                "Grid Pos": st.column_config.NumberColumn(min_value=1, max_value=22, step=1),
                "Race Pos": st.column_config.NumberColumn(min_value=1, max_value=22, step=1),
                "FL": st.column_config.CheckboxColumn(help="Fastest lap (+3 pts)"),
                "DNF": st.column_config.CheckboxColumn(),
            },
            hide_index=True,
            use_container_width=True,
        )

        if st.button("Save Results", type="primary"):
            to_save = []
            for _, row in edited.iterrows():
                qual = int(row["Qual Pos"])
                grid = int(row["Grid Pos"])
                fl = bool(row["FL"])
                dnf = bool(row["DNF"])
                race_pos = None if dnf else int(row["Race Pos"])
                pts = calculate_driver_points(qual, grid, race_pos, dnf, fl)
                to_save.append(
                    {
                        "race_id": race_id,
                        "driver_id": int(row["_driver_id"]),
                        "qualifying_pos": qual,
                        "grid_pos": grid,
                        "race_pos": race_pos,
                        "fastest_lap": fl,
                        "dnf": dnf,
                        "base_points": pts,
                    }
                )
            save_race_results(supabase, race_id, to_save)
            st.success("Results saved!")
            st.cache_data.clear()

# ── Tab 3: Add Race ───────────────────────────────────────────────────────────
with tab3:
    st.subheader("Add 2025 Race")

    F1_2025_CALENDAR = [
        (1, "Australian Grand Prix", "Albert Park"),
        (2, "Chinese Grand Prix", "Shanghai"),
        (3, "Japanese Grand Prix", "Suzuka"),
        (4, "Bahrain Grand Prix", "Bahrain International Circuit"),
        (5, "Saudi Arabian Grand Prix", "Jeddah"),
        (6, "Miami Grand Prix", "Miami"),
        (7, "Emilia Romagna Grand Prix", "Imola"),
        (8, "Monaco Grand Prix", "Monaco"),
        (9, "Spanish Grand Prix", "Barcelona"),
        (10, "Canadian Grand Prix", "Montreal"),
        (11, "Austrian Grand Prix", "Spielberg"),
        (12, "British Grand Prix", "Silverstone"),
        (13, "Belgian Grand Prix", "Spa"),
        (14, "Hungarian Grand Prix", "Budapest"),
        (15, "Dutch Grand Prix", "Zandvoort"),
        (16, "Italian Grand Prix", "Monza"),
        (17, "Azerbaijan Grand Prix", "Baku"),
        (18, "Singapore Grand Prix", "Marina Bay"),
        (19, "United States Grand Prix", "Austin"),
        (20, "Mexico City Grand Prix", "Mexico City"),
        (21, "São Paulo Grand Prix", "São Paulo"),
        (22, "Las Vegas Grand Prix", "Las Vegas"),
        (23, "Qatar Grand Prix", "Lusail"),
        (24, "Abu Dhabi Grand Prix", "Yas Marina"),
    ]

    existing_rounds = {r["round_number"] for r in get_races(supabase)}
    available = [(rnd, name, circuit) for rnd, name, circuit in F1_2025_CALENDAR if rnd not in existing_rounds]

    if not available:
        st.success("All 2025 races have been added.")
    else:
        labels = [f"Round {rnd}: {name}" for rnd, name, _ in available]
        idx = st.selectbox("Race", range(len(labels)), format_func=lambda i: labels[i])
        if st.button("Add Race"):
            rnd, name, circuit = available[idx]
            supabase.table("races").insert(
                {"round_number": rnd, "name": name, "circuit": circuit}
            ).execute()
            st.success(f"Added {name}!")
            st.rerun()

    current = get_races(supabase)
    if current:
        st.write("**Added races:**")
        st.dataframe(
            pd.DataFrame(current)[["round_number", "name", "circuit"]].rename(
                columns={"round_number": "Round", "name": "Race", "circuit": "Circuit"}
            ),
            hide_index=True,
            use_container_width=True,
        )

# ── Tab 4: Set Teams ────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Assign Draft Teams")
    st.write(
        "Assign 4 drivers to each player by draft round. "
        "**Round 4 picks get a 3× points multiplier.**"
    )

    players = get_players(supabase)
    drivers = get_drivers(supabase)

    if not players or not drivers:
        st.warning("Players/drivers missing. Run setup.sql in your Supabase dashboard.")
        st.stop()

    existing_picks = get_player_drivers(supabase)
    pick_map = {(p["player_id"], p["draft_round"]): p["driver_id"] for p in existing_picks}

    driver_by_id = {d["id"]: d["name"] for d in drivers}
    driver_name_to_id = {d["name"]: d["id"] for d in drivers}
    driver_options = ["— None —"] + sorted(driver_name_to_id.keys())

    for player in players:
        st.write(f"**{player['name']}**")
        cols = st.columns(4)
        picks = {}
        for rnd in range(1, 5):
            current_id = pick_map.get((player["id"], rnd))
            current_name = driver_by_id.get(current_id, "— None —")
            idx = driver_options.index(current_name) if current_name in driver_options else 0
            label = f"Round {rnd}" + (" ✦ 3×" if rnd == 4 else "")
            selected = cols[rnd - 1].selectbox(
                label,
                driver_options,
                index=idx,
                key=f"pick_{player['id']}_{rnd}",
            )
            picks[rnd] = selected

        if st.button(f"Save {player['name']}'s team", key=f"save_{player['id']}"):
            supabase.table("player_drivers").delete().eq("player_id", player["id"]).execute()
            new_picks = [
                {"player_id": player["id"], "driver_id": driver_name_to_id[name], "draft_round": rnd}
                for rnd, name in picks.items()
                if name != "— None —"
            ]
            if new_picks:
                supabase.table("player_drivers").insert(new_picks).execute()
            st.success(f"Saved {player['name']}'s team!")
            st.rerun()

        st.write("")

# ── Tab 2: Enter Sprint Results ───────────────────────────────────────────────
with tab2:
    st.subheader("Enter Sprint Results")
    races = get_races(supabase)
    drivers = get_drivers(supabase)

    if not races:
        st.info("Add a race first in the 'Add Race' tab.")
    elif not drivers:
        st.warning("No drivers found.")
    else:
        race_labels = [f"Round {r['round_number']}: {r['name']}" for r in races]
        selected_idx = st.selectbox(
            "Select Race",
            range(len(race_labels)),
            format_func=lambda i: race_labels[i],
            key="sprint_race_select",
        )
        race_id = races[selected_idx]["id"]

        existing = {r["driver_id"]: r for r in get_sprint_results(supabase, race_id)}

        st.write(
            "**Grid Pos** = sprint starting position, **Finish Pos** = sprint finishing position. "
            "Check **FL** for fastest lap, **DNF** if driver did not finish."
        )

        rows = []
        for d in sorted(drivers, key=lambda x: x["name"]):
            ex = existing.get(d["id"], {})
            rows.append({
                "_driver_id": d["id"],
                "Driver": d["name"],
                "Constructor": d["constructor"],
                "Grid Pos": ex.get("grid_pos") or 10,
                "Finish Pos": ex.get("finish_pos") or 10,
                "FL": ex.get("fastest_lap") or False,
                "DNF": ex.get("dnf") or False,
            })

        edited = st.data_editor(
            pd.DataFrame(rows),
            column_config={
                "_driver_id": None,
                "Driver": st.column_config.TextColumn(disabled=True),
                "Constructor": st.column_config.TextColumn(disabled=True),
                "Grid Pos": st.column_config.NumberColumn(min_value=1, max_value=22, step=1),
                "Finish Pos": st.column_config.NumberColumn(min_value=1, max_value=22, step=1),
                "FL": st.column_config.CheckboxColumn(help="Fastest lap (+5 pts)"),
                "DNF": st.column_config.CheckboxColumn(),
            },
            hide_index=True,
            use_container_width=True,
        )

        if st.button("Save Sprint Results", type="primary"):
            to_save = []
            for _, row in edited.iterrows():
                grid = int(row["Grid Pos"])
                finish = int(row["Finish Pos"])
                fl = bool(row["FL"])
                dnf = bool(row["DNF"])
                pts = calculate_sprint_points(grid, finish, fl, dnf)
                to_save.append({
                    "race_id": race_id,
                    "driver_id": int(row["_driver_id"]),
                    "grid_pos": grid,
                    "finish_pos": finish if not dnf else None,
                    "fastest_lap": fl,
                    "dnf": dnf,
                    "base_points": pts,
                })
            save_sprint_results(supabase, race_id, to_save)
            st.success("Sprint results saved!")
            st.cache_data.clear()
