from .statistics import Statistics
from ..classes.schedule import Schedule


class Solver:
    def __init__(self, log=False):
        self.verifier = Statistics()
        self.do_log = log

    # Mockup function only for type hinting
    def solve(self, schedule: Schedule, i_max: int | None = None, method: str = "", strict=True):
        return self.verifier.Result(schedule)
