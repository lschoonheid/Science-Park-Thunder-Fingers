from .statistics import Statistics
from ..classes.schedule import Schedule


class Solver:
    def __init__(self, verbose=False):
        self.verifier = Statistics()
        self.verbose = verbose

    # Mockup function only for type hinting
    def solve(self, schedule: Schedule, i_max: int | None = None, method: str = "", strict=True):
        return self.verifier.Result(schedule)
