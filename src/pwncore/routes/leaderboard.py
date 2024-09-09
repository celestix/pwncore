from __future__ import annotations

from time import monotonic

from fastapi import APIRouter, Request

from tortoise.expressions import RawSQL, Q

from pwncore.models import Team

# Metadata at the top for instant accessibility
metadata = {"name": "leaderboard", "description": "Operations on the leaderboard"}

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

from pwncore.utils import TEAMS_SOLVED_PROBS, PROBLEMS_CACHE

#  {
#         "name": "Team41",
#         "meta_team__name": null,
#         "tpoints": 300.0
#    },
 
from typing import Dict
class ExpiringLBCache:
    period: float
    last_update: float
    data: list[dict[str, float]]

    def __init__(self, period: float) -> None:
        self.period = period
        self.last_update = 0
        self.data = []
    # ({pid:penalty}, name, points)
    async def _do_update(self):
        # total = []
        # for i in TEAMS_SOLVED_PROBS:
        #     data = TEAMS_SOLVED_PROBS[i]
        #     tp = 0
        #     # pid: penalty
        #     probs: Dict[int, float] = data[0]
        #     for pid in probs:
        #         ppoints = PROBLEMS_CACHE[pid]
        #         penalty = probs[pid]
        #         if penalty == 0:
        #             penalty = 1
        #         tp += ppoints*penalty
        #     tp += data[2]
        #     total.append({"name":data[1], "tpoints": tp})
        # self.data = total
        self.data = (
            await Team.all()
            .filter(Q(solved_problem__problem__visible=True) | Q(points__gte=0))
            .annotate(
                tpoints=RawSQL(
                    'COALESCE((SUM("solvedproblem"."penalty" * '
                    '"solvedproblem__problem"."points")'
                    ' + "team"."points"), 0)'
                )
            )
            .group_by("id", "meta_team__name")
            .order_by("-tpoints")
            .values("name", "tpoints", "meta_team__name")
        )
        self.last_update = monotonic()

    async def get_lb(self, req: Request):
        if (
            getattr(req.app.state, "force_expire", False)
            or (monotonic() - self.last_update) > self.period  # noqa: W503
        ):
            await self._do_update()
            req.app.state.force_expire = False
        return self.data


gcache = ExpiringLBCache(30.0)


@router.get("")
async def fetch_leaderboard(req: Request):
    return await gcache.get_lb(req)
