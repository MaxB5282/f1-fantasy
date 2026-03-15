# ── Regular Race ──────────────────────────────────────────────────────────────
QUALIFYING_POINTS = {
    1: 15, 2: 14, 3: 13, 4: 12, 5: 11,
    6: 10, 7: 9, 8: 8, 9: 7, 10: 6,
}
QUALIFYING_POINTS_DEFAULT = 0  # P11+ get 0 pts

RACE_POINTS = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1,
}

POSITIONS_GAINED_PTS = 2   # per position gained in race
POSITIONS_LOST_PTS = -1    # per position lost in race
FASTEST_LAP_PTS = 3        # bonus for fastest lap in regular race
DNF_PENALTY = -5

# ── Sprint Race ───────────────────────────────────────────────────────────────
SPRINT_RACE_POINTS = {
    1: 8, 2: 7, 3: 6, 4: 5, 5: 4,
    6: 3, 7: 2, 8: 1,
}

SPRINT_POSITIONS_GAINED_PTS = 1   # per position gained in sprint
SPRINT_POSITIONS_LOST_PTS = -1    # per position lost in sprint
SPRINT_FASTEST_LAP_PTS = 5
SPRINT_DNF_PENALTY = -10

# ── Misc ──────────────────────────────────────────────────────────────────────
FOURTH_ROUND_MULTIPLIER = 2
WAIVER_PICKUP_PENALTY = -20


def calculate_driver_points(qualifying_pos, grid_pos, race_pos, dnf=False, fastest_lap=False):
    """Calculate base points for a driver in a regular race."""
    qual_pts = QUALIFYING_POINTS.get(qualifying_pos, QUALIFYING_POINTS_DEFAULT if qualifying_pos else 0)

    if dnf:
        return qual_pts + DNF_PENALTY

    race_pts = RACE_POINTS.get(race_pos, 0)
    if grid_pos is not None and race_pos is not None:
        net = grid_pos - race_pos  # positive = gained positions
        if net > 0:
            pos_pts = min(net * POSITIONS_GAINED_PTS, 10)  # cap gains at 10 pts
        else:
            pos_pts = net * abs(POSITIONS_LOST_PTS)
    else:
        pos_pts = 0
    fl_pts = FASTEST_LAP_PTS if fastest_lap else 0

    return qual_pts + race_pts + pos_pts + fl_pts


def calculate_sprint_points(grid_pos, finish_pos, fastest_lap=False, dnf=False):
    """Calculate base points for a driver in a sprint race."""
    if dnf:
        return SPRINT_DNF_PENALTY

    sprint_pts = SPRINT_RACE_POINTS.get(finish_pos, 0)
    net = grid_pos - finish_pos  # positive = gained positions
    pos_pts = net * SPRINT_POSITIONS_GAINED_PTS if net > 0 else net * abs(SPRINT_POSITIONS_LOST_PTS)
    fastest_pts = SPRINT_FASTEST_LAP_PTS if fastest_lap else 0

    return sprint_pts + pos_pts + fastest_pts


def apply_multiplier(base_points, draft_round):
    """Apply draft round multiplier to base points (only on positive totals)."""
    if draft_round == 4 and base_points > 0:
        return base_points * FOURTH_ROUND_MULTIPLIER
    return base_points


def get_driver_points_breakdown(qualifying_pos, grid_pos, race_pos, dnf=False, fastest_lap=False):
    """Return a dict of individual scoring components for a regular race."""
    qual_pts = QUALIFYING_POINTS.get(qualifying_pos, QUALIFYING_POINTS_DEFAULT if qualifying_pos else 0)

    if dnf:
        return {"Qual Pts": qual_pts, "Finish Pts": 0, "Pos Pts": DNF_PENALTY, "FL Pts": 0}

    race_pts = RACE_POINTS.get(race_pos, 0) if race_pos else 0
    if grid_pos is not None and race_pos is not None:
        net = grid_pos - race_pos
        if net > 0:
            pos_pts = min(net * POSITIONS_GAINED_PTS, 10)
        else:
            pos_pts = net * abs(POSITIONS_LOST_PTS)
    else:
        pos_pts = 0
    fl_pts = FASTEST_LAP_PTS if fastest_lap else 0

    return {"Qual Pts": qual_pts, "Finish Pts": race_pts, "Pos Pts": pos_pts, "FL Pts": fl_pts}


def get_sprint_points_breakdown(grid_pos, finish_pos, fastest_lap=False, dnf=False):
    """Return a dict of individual scoring components for a sprint race."""
    if dnf:
        return {"Finish Pts": SPRINT_DNF_PENALTY, "Pos Pts": 0, "FL Pts": 0}

    sprint_pts = SPRINT_RACE_POINTS.get(finish_pos, 0) if finish_pos else 0
    net = (grid_pos - finish_pos) if grid_pos is not None and finish_pos is not None else 0
    pos_pts = net * SPRINT_POSITIONS_GAINED_PTS if net > 0 else net * abs(SPRINT_POSITIONS_LOST_PTS)
    fl_pts = SPRINT_FASTEST_LAP_PTS if fastest_lap else 0

    return {"Finish Pts": sprint_pts, "Pos Pts": pos_pts, "FL Pts": fl_pts}
