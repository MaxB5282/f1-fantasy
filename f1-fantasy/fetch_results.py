#!/usr/bin/env python3
"""
fetch_results.py — Fetch F1 weekend results via FastF1 and push to Supabase.

Usage:
    python fetch_results.py --round 3
    python fetch_results.py --round 3 --dry-run    # preview without uploading
    python fetch_results.py --round 3 --year 2024  # specific year (default: 2025)

First-time setup:
    pip install fastf1 supabase tomli   # tomli only needed on Python <3.11
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


# ── Credential loading ─────────────────────────────────────────────────────────

def load_secrets():
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        print("ERROR: .streamlit/secrets.toml not found.")
        print("Copy .streamlit/secrets.toml.example and fill in your values.")
        sys.exit(1)
    try:
        import tomllib          # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("ERROR: Run  pip install tomli  (needed on Python < 3.11)")
            sys.exit(1)
    with open(secrets_path, "rb") as f:
        return tomllib.load(f)


# ── Driver name normalization ──────────────────────────────────────────────────
# If FastF1 returns a name that doesn't match Supabase exactly, add it here.

NAME_MAP = {
    "Nico Hulkenberg":  "Nico Hülkenberg",
}


def normalize(name: str) -> str:
    return NAME_MAP.get(name.strip(), name.strip())


# ── DNF detection ──────────────────────────────────────────────────────────────

def is_dnf(status) -> bool:
    if not status or (isinstance(status, float) and pd.isna(status)):
        return False
    s = str(status).strip()
    if s == "Finished":
        return False
    if s.startswith("+") and "Lap" in s:   # "+1 Lap", "+2 Laps", etc.
        return False
    return True   # Accident, Engine, Retired, Collision, Disqualified, etc.


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch F1 results and upload to Supabase")
    parser.add_argument("--round",   type=int, required=True, help="F1 round number")
    parser.add_argument("--year",    type=int, default=2025,  help="Season year (default: 2025)")
    parser.add_argument("--dry-run", action="store_true",     help="Print results without uploading")
    args = parser.parse_args()

    import fastf1
    fastf1.Cache.enable_cache(str(Path(__file__).parent / "fastf1_cache"))

    # ── Supabase ───────────────────────────────────────────────────────────────
    supabase   = None
    race_db_id = None
    driver_map = {}   # name → DB id

    if not args.dry_run:
        from supabase import create_client
        secrets  = load_secrets()
        supabase = create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])

        races = supabase.table("races").select("*").eq("round_number", args.round).execute().data
        if not races:
            print(f"ERROR: Round {args.round} not found in the races table.")
            print("Add the race in the Admin page first, then re-run this script.")
            sys.exit(1)

        race_db_id = races[0]["id"]
        print(f"DB race: {races[0]['name']}  (id={race_db_id})")

        drivers    = supabase.table("drivers").select("id, name").execute().data
        driver_map = {d["name"]: d["id"] for d in drivers}

    # ── FastF1 event ───────────────────────────────────────────────────────────
    print(f"\nFetching {args.year} round {args.round} from FastF1...")
    event = fastf1.get_event(args.year, args.round)
    fmt   = str(event.get("EventFormat", "")).lower()
    print(f"Event : {event['EventName']}")
    print(f"Format: {event['EventFormat']}")

    is_sprint = "sprint" in fmt
    print(f"Sprint weekend: {is_sprint}")

    # Import scoring functions (works when run from the f1-fantasy directory)
    from utils.points import calculate_driver_points, calculate_sprint_points

    # ── Qualifying ─────────────────────────────────────────────────────────────
    print("\nLoading Qualifying...")
    qual = event.get_session("Q")
    qual.load(laps=False, telemetry=False, weather=False, messages=False)

    qual_pos = {}
    for _, row in qual.results.iterrows():
        qual_pos[normalize(str(row["FullName"]))] = int(row["Position"])

    # ── Race ───────────────────────────────────────────────────────────────────
    print("Loading Race...")
    race_sess = event.get_session("R")
    race_sess.load(laps=True, telemetry=False, weather=False, messages=False)

    # Detect fastest lap in race
    fastest_lap_driver = None
    try:
        fl_lap  = race_sess.laps.pick_fastest()
        fl_info = race_sess.get_driver(fl_lap["DriverNumber"])
        fastest_lap_driver = normalize(str(fl_info["FullName"]))
        print(f"Race fastest lap: {fastest_lap_driver}")
    except Exception as e:
        print(f"Could not determine race fastest lap: {e}")

    race_rows = []
    print()
    print(f"{'── Race Results ':-<60}")
    print(f"  {'Driver':<24}  {'Q':>3}  {'Grid':>4}  {'Fin':>4}  {'FL':>3}  {'DNF':>5}  {'Pts':>6}")
    print(f"  {'-'*58}")

    for _, row in race_sess.results.iterrows():
        name      = normalize(str(row["FullName"]))
        driver_id = driver_map.get(name)

        if not args.dry_run and driver_id is None:
            print(f"  WARNING: '{name}' not in DB — skipping")
            continue

        q    = qual_pos.get(name)
        grid = int(row["GridPosition"]) if pd.notna(row.get("GridPosition")) else q
        fin  = int(row["Position"])     if pd.notna(row.get("Position"))     else None
        dnf  = is_dnf(row.get("Status"))
        fl   = (name == fastest_lap_driver)

        pts = calculate_driver_points(q, grid, fin, dnf, fl)

        print(f"  {name:<24}  {str(q):>3}  {str(grid):>4}  {'DNF' if dnf else str(fin):>4}  {'✓' if fl else '':>3}  {str(dnf):>5}  {pts:>6.1f}")

        race_rows.append({
            "race_id":        race_db_id,
            "driver_id":      driver_id,
            "qualifying_pos": q,
            "grid_pos":       grid,
            "race_pos":       None if dnf else fin,
            "fastest_lap":    fl,
            "dnf":            dnf,
            "base_points":    pts,
        })

    # ── Sprint ─────────────────────────────────────────────────────────────────
    sprint_rows = []

    if is_sprint:
        print("\nLoading Sprint...")
        sprint_sess = event.get_session("S")
        sprint_sess.load(laps=True, telemetry=False, weather=False, messages=False)

        # Fastest lap in sprint
        fastest_lap_driver = None
        try:
            fl_lap  = sprint_sess.laps.pick_fastest()
            fl_info = sprint_sess.get_driver(fl_lap["DriverNumber"])
            fastest_lap_driver = normalize(str(fl_info["FullName"]))
            print(f"Sprint fastest lap: {fastest_lap_driver}")
        except Exception as e:
            print(f"Could not determine sprint fastest lap: {e}")

        print()
        print(f"{'── Sprint Results ':-<60}")
        print(f"  {'Driver':<24}  {'Grid':>4}  {'Fin':>4}  {'FL':>3}  {'DNF':>5}  {'Pts':>6}")
        print(f"  {'-'*56}")

        for _, row in sprint_sess.results.iterrows():
            name      = normalize(str(row["FullName"]))
            driver_id = driver_map.get(name)

            if not args.dry_run and driver_id is None:
                print(f"  WARNING: '{name}' not in DB — skipping")
                continue

            grid = int(row["GridPosition"]) if pd.notna(row.get("GridPosition")) else None
            fin  = int(row["Position"])     if pd.notna(row.get("Position"))     else None
            dnf  = is_dnf(row.get("Status"))
            fl   = (name == fastest_lap_driver)

            pts = calculate_sprint_points(grid, fin, fl, dnf)

            print(f"  {name:<24}  {str(grid):>4}  {'DNF' if dnf else str(fin):>4}  {'✓' if fl else '':>3}  {str(dnf):>5}  {pts:>6.1f}")

            sprint_rows.append({
                "race_id":     race_db_id,
                "driver_id":   driver_id,
                "grid_pos":    grid,
                "finish_pos":  None if dnf else fin,
                "fastest_lap": fl,
                "dnf":         dnf,
                "base_points": pts,
            })

    # ── Upload ─────────────────────────────────────────────────────────────────
    if args.dry_run:
        print("\n[DRY RUN] Nothing was uploaded to Supabase.")
        return

    print(f"\nUploading {len(race_rows)} race result rows...")
    supabase.table("race_results").upsert(race_rows, on_conflict="race_id,driver_id").execute()

    if sprint_rows:
        print(f"Uploading {len(sprint_rows)} sprint result rows...")
        supabase.table("sprint_results").upsert(sprint_rows, on_conflict="race_id,driver_id").execute()

    print("\nDone ✓  Check the leaderboard to verify.")


if __name__ == "__main__":
    main()
