import streamlit as st
from supabase import create_client, Client
from utils.points import apply_multiplier


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_players(supabase):
    return supabase.table("players").select("*").order("name").execute().data


def get_drivers(supabase):
    return supabase.table("drivers").select("*").order("name").execute().data


def get_races(supabase):
    return supabase.table("races").select("*").order("round_number").execute().data


def get_player_drivers(supabase):
    return (
        supabase.table("player_drivers")
        .select("*, players(*), drivers(*)")
        .execute()
        .data
    )


def get_race_results(supabase, race_id=None):
    query = supabase.table("race_results").select("*, drivers(*), races(*)")
    if race_id:
        query = query.eq("race_id", race_id)
    return query.execute().data


def get_sprint_results(supabase, race_id=None):
    query = supabase.table("sprint_results").select("*, drivers(*), races(*)")
    if race_id:
        query = query.eq("race_id", race_id)
    return query.execute().data


def get_point_adjustments(supabase, player_id=None):
    query = supabase.table("point_adjustments").select("*, players(name)")
    if player_id:
        query = query.eq("player_id", player_id)
    return query.order("created_at", desc=True).execute().data


def save_race_results(supabase, race_id, rows):
    supabase.table("race_results").upsert(rows, on_conflict="race_id,driver_id").execute()


def save_sprint_results(supabase, race_id, rows):
    supabase.table("sprint_results").upsert(rows, on_conflict="race_id,driver_id").execute()


def process_waiver_pickup(supabase, player_id, picked_driver_id, dropped_driver_id):
    """Drop a driver, add the new one at the same draft round, and apply -20pt penalty."""
    # Get the dropped driver's draft round so new driver inherits it
    existing = (
        supabase.table("player_drivers")
        .select("draft_round")
        .eq("player_id", player_id)
        .eq("driver_id", dropped_driver_id)
        .execute()
        .data
    )
    if not existing:
        raise ValueError("Dropped driver not found on this player's team.")
    draft_round = existing[0]["draft_round"]

    # Swap the driver
    supabase.table("player_drivers").delete().eq("player_id", player_id).eq("driver_id", dropped_driver_id).execute()
    supabase.table("player_drivers").insert({
        "player_id": player_id,
        "driver_id": picked_driver_id,
        "draft_round": draft_round,
    }).execute()

    # Apply penalty
    dropped = supabase.table("drivers").select("name").eq("id", dropped_driver_id).execute().data[0]["name"]
    picked = supabase.table("drivers").select("name").eq("id", picked_driver_id).execute().data[0]["name"]
    supabase.table("point_adjustments").insert({
        "player_id": player_id,
        "amount": -20,
        "reason": f"Waiver pickup: {picked} for {dropped}",
    }).execute()


def get_leaderboard(supabase):
    """Return (player_totals, player_breakdown, adj_log, player_round_pts)."""
    player_drivers = (
        supabase.table("player_drivers")
        .select("player_id, driver_id, draft_round, players(id, name), drivers(id, name)")
        .execute()
        .data
    )

    # Build driver -> {pid, draft_round} mapping
    driver_to_player = {
        pd["driver_id"]: {"pid": pd["player_id"], "draft_round": pd["draft_round"]}
        for pd in player_drivers
    }

    # Fetch results with race info for per-round breakdown
    race_results = (
        supabase.table("race_results")
        .select("driver_id, base_points, race_id, races(id, round_number, name)")
        .execute()
        .data
    )
    sprint_results = (
        supabase.table("sprint_results")
        .select("driver_id, base_points, race_id, races(id, round_number, name)")
        .execute()
        .data
    )

    # Sum base points per driver (for overall totals)
    driver_race_pts = {}
    for r in race_results:
        did = r["driver_id"]
        driver_race_pts[did] = driver_race_pts.get(did, 0) + (r["base_points"] or 0)

    driver_sprint_pts = {}
    for r in sprint_results:
        did = r["driver_id"]
        driver_sprint_pts[did] = driver_sprint_pts.get(did, 0) + (r["base_points"] or 0)

    # Per-player per-race points (multiplier applied per race for weekly view)
    player_round_pts = {}  # {pid: {race_id: {"name": str, "round": int, "pts": float}}}
    for r in race_results + sprint_results:
        did = r["driver_id"]
        if did not in driver_to_player:
            continue
        info = driver_to_player[did]
        pid = info["pid"]
        draft_round = info["draft_round"]
        race_id = r["race_id"]
        race_info = r.get("races") or {}
        base = r["base_points"] or 0
        pts = apply_multiplier(base, draft_round)
        player_round_pts.setdefault(pid, {})
        if race_id not in player_round_pts[pid]:
            player_round_pts[pid][race_id] = {
                "name": race_info.get("name", ""),
                "round": race_info.get("round_number", 0),
                "pts": 0,
            }
        player_round_pts[pid][race_id]["pts"] = round(player_round_pts[pid][race_id]["pts"] + pts, 1)

    # Point adjustments per player (waiver penalties etc.)
    player_adj = {}
    adj_log = {}
    for adj in supabase.table("point_adjustments").select("player_id, amount, reason").execute().data:
        pid = adj["player_id"]
        player_adj[pid] = player_adj.get(pid, 0) + (adj["amount"] or 0)
        adj_log.setdefault(pid, []).append({"reason": adj["reason"], "amount": adj["amount"]})

    player_totals = {}
    player_breakdown = {}

    for pd in player_drivers:
        pid = pd["player_id"]
        did = pd["driver_id"]
        draft_round = pd["draft_round"]
        player_name = pd["players"]["name"]
        driver_name = pd["drivers"]["name"]

        base = driver_race_pts.get(did, 0) + driver_sprint_pts.get(did, 0)
        total = apply_multiplier(base, draft_round)

        if pid not in player_totals:
            player_totals[pid] = {"name": player_name, "total": 0}
            player_breakdown[pid] = []

        player_totals[pid]["total"] += total
        player_breakdown[pid].append({
            "Driver": driver_name,
            "Round": draft_round,
            "Base Pts": round(base, 1),
            "Multiplier": f"{apply_multiplier(1, draft_round)}x",
            "Total Pts": round(total, 1),
        })

    # Apply point adjustments to totals
    for pid, adj in player_adj.items():
        if pid in player_totals:
            player_totals[pid]["total"] += adj
            player_totals[pid]["adjustments"] = adj

    return player_totals, player_breakdown, adj_log, player_round_pts
