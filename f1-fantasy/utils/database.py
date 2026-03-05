import streamlit as st
from supabase import create_client, Client
from utils.points import calculate_driver_points, apply_multiplier


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


def get_leaderboard(supabase):
    """Return (player_totals dict, driver_breakdown dict) for the leaderboard."""
    player_drivers = (
        supabase.table("player_drivers")
        .select("player_id, driver_id, draft_round, players(id, name), drivers(id, name)")
        .execute()
        .data
    )

    all_results = (
        supabase.table("race_results")
        .select("driver_id, base_points")
        .execute()
        .data
    )

    # Sum base points per driver
    driver_base = {}
    for r in all_results:
        did = r["driver_id"]
        driver_base[did] = driver_base.get(did, 0) + (r["base_points"] or 0)

    player_totals = {}
    player_breakdown = {}

    for pd in player_drivers:
        pid = pd["player_id"]
        did = pd["driver_id"]
        draft_round = pd["draft_round"]
        player_name = pd["players"]["name"]
        driver_name = pd["drivers"]["name"]

        base = driver_base.get(did, 0)
        total = apply_multiplier(base, draft_round)

        if pid not in player_totals:
            player_totals[pid] = {"name": player_name, "total": 0}
            player_breakdown[pid] = []

        player_totals[pid]["total"] += total
        player_breakdown[pid].append(
            {
                "Driver": driver_name,
                "Round": draft_round,
                "Base Pts": round(base, 1),
                "Multiplier": f"{apply_multiplier(1, draft_round)}x",
                "Total Pts": round(total, 1),
            }
        )

    return player_totals, player_breakdown


def save_race_results(supabase, race_id, rows):
    """Upsert race result rows. Each row must include all required fields."""
    supabase.table("race_results").upsert(
        rows, on_conflict="race_id,driver_id"
    ).execute()
