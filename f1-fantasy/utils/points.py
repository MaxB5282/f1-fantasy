QUALIFYING_POINTS = {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5, 7: 4, 8: 3, 9: 2, 10: 1,
}

RACE_POINTS = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1,
}

OVERTAKE_PTS_PER_POS = 2
FOURTH_ROUND_MULTIPLIER = 3


def calculate_driver_points(qualifying_pos, grid_pos, race_pos, dnf=False):
    """Calculate base points for a driver in a single race.

    Args:
        qualifying_pos: qualifying result (1-20)
        grid_pos: actual starting grid position (1-20), may differ due to penalties
        race_pos: finishing position (1-20), or None if DNF
        dnf: whether the driver did not finish
    """
    qual_pts = QUALIFYING_POINTS.get(qualifying_pos, 0)

    if dnf or race_pos is None:
        race_pts = 0
        overtake_pts = 0
    else:
        race_pts = RACE_POINTS.get(race_pos, 0)
        positions_gained = grid_pos - race_pos
        overtake_pts = max(0, positions_gained) * OVERTAKE_PTS_PER_POS

    return qual_pts + race_pts + overtake_pts


def apply_multiplier(base_points, draft_round):
    """Apply draft round multiplier to base points."""
    if draft_round == 4:
        return base_points * FOURTH_ROUND_MULTIPLIER
    return base_points
