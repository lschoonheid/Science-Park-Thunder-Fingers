# from numba import jit
from math import exp
import numpy as np
from .mutator import Mutator
from ..classes.result import Result


class MutationSupplier(Mutator):
    def __init__(
        self,
        score_scope: int = 10,
        tried_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[int, int], int | float] = {},
    ):
        # Score scope is how many timeslots to look at when scoring a swap
        self.score_scope = score_scope
        self.tried_swaps = tried_swaps
        self.swap_scores_memory = swap_scores_memory

    def suggest_swap(self, result: Result, ceiling=0):
        raise NotImplementedError

    def reset_swaps(self):
        self.tried_swaps.clear()


class HillClimber(MutationSupplier):
    def suggest_swap(self, result: Result, ceiling=0):
        # See which swaps are best
        swap_scores = self.get_swap_scores_timeslot(result, self.score_scope, self.tried_swaps, ceiling=ceiling)
        # TODO: make this a priority queue
        suggested_swap: tuple[int, int] = min(swap_scores, key=swap_scores.get)  # type: ignore

        # if len(swap_scores_memory) > 4000:
        #     swap_scores_memory.clear()
        # self.tried_swaps.union(swap_scores.keys())

        # Update memory
        self.swap_scores_memory.update(swap_scores)
        del self.swap_scores_memory[suggested_swap]
        return suggested_swap


class SimulatedAnnealing(MutationSupplier):
    def __init__(
        self,
        score_scope: int = 10,
        tried_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[int, int], int | float] = {},
        T_0: float = 4 / 600,
        kB=1,
    ):
        self.T_0 = T_0
        self.kB = kB
        super().__init__(score_scope, tried_swaps, swap_scores_memory)

    # @jit()
    def biased_boolean(self, probability: float = 0.5) -> bool:
        """Returns `True` with probability `probability`. Otherwise returns False."""
        assert probability >= 0, "Probability cannot be less than zero"
        if np.random.rand() < probability:
            return True
        return False

    # def temperature(self, T_0: float, i: int = 0, i_max: int = 0) -> float:
    # @property
    def temperature(self, result: Result) -> float:
        # return T_0 * (i_max - i) / i_max
        return self.T_0 * result.score

    # @jit()
    def p(self, diff, temperature) -> float:
        k_boltzman = self.kB
        beta = 1 / (k_boltzman * temperature)

        return exp(-beta * diff)

    def suggest_swap(self, result: Result, ceiling=15, _recursion_depth=1000):
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        # For annealing important to NOT select the best swap, but a random one
        draw = self.draw_valid_timeslot_swap(
            result,
            list(result.schedule.timeslots.values()),
            self.tried_swaps,
            ceiling=ceiling,
        )
        if not draw:
            return None
        (id1, id2), score = draw

        # Simulated annealing: accept a random swap with probability p
        probability = self.p(score, self.temperature(result))
        if self.biased_boolean(probability):
            return id1, id2

        return self.suggest_swap(result, ceiling, _recursion_depth - 1)
