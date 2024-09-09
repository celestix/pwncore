from typing import Dict, Tuple
# PID: Points
PROBLEMS_CACHE: Dict[int, int] = {}
# TID: [PID, PENALTY, POINTS]
TEAMS_SOLVED_PROBS: Dict[int, Tuple[Dict[int, float], str, int]] = {}

async def update_team_solved(tid, pid=None, penalty=None, name=None, points=None):
    if not tid in TEAMS_SOLVED_PROBS:
        penalty = 0
        points = 0
        TEAMS_SOLVED_PROBS[tid] = ({pid:penalty} if pid else {}, name, points)
        return
    data = TEAMS_SOLVED_PROBS[tid]
    if not pid in data[0]:
        data[0][pid] = 0
    if not points:
        TEAMS_SOLVED_PROBS[tid] = ({pid:penalty if penalty is not None else data[0][pid]}, data[1], points if points is not None else data[2])
    