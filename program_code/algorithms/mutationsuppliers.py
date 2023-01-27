# from numba import jit
from math import exp
import random
import numpy as np
from .mutator import Mutator
from ..classes import Timeslot
from ..classes.result import Result


class MutationSupplier(Mutator):
    def __init__(
        self,
        score_scope: int = 10,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
    ):
        # Score scope is how many timeslots to look at when scoring a swap
        self.score_scope = score_scope
        self.tried_timeslot_swaps = tried_timeslot_swaps
        self.swap_scores_memory = swap_scores_memory

    def suggest_mutation(self, result: Result, ceiling=0):
        """Generate possible swap."""
        raise NotImplementedError

    def reset_mutations(self):
        self.tried_timeslot_swaps.clear()


class HillClimber(MutationSupplier):
    def suggest_mutation(self, result: Result, ceiling=0):
        # See which swaps are best
        swap_scores = self.get_swap_scores_timeslot(
            result, self.score_scope, self.tried_timeslot_swaps, ceiling=ceiling
        )
        # TODO: make this a priority queue
        swap: tuple[Timeslot, Timeslot] = min(swap_scores, key=swap_scores.get)  # type: ignore

        # if len(swap_scores_memory) > 4000:
        #     swap_scores_memory.clear()
        # self.tried_timeslot_swaps.union(swap_scores.keys())

        # TODO: implement student moving

        # Update memory
        self.swap_scores_memory.update(swap_scores)
        del self.swap_scores_memory[swap]
        return self.swap_neighbors, [result.schedule, *swap, "Room"]


class SimulatedAnnealing(MutationSupplier):
    def __init__(
        self,
        score_scope: int = 10,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
        T_0: float = 1 / 600,
        kB=1,
    ):
        self.T_0 = T_0
        self.kB = kB
        super().__init__(score_scope, tried_timeslot_swaps, swap_scores_memory)

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

        # Subtract 0.69315 so a diff of 0 results in 50 percent chance of change
        return exp(-beta * diff - 0.69315)

    def suggest_mutation(self, result: Result, ceiling=15, _recursion_depth=1000):
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        move_mutation, swap_mutation = None, None

        timeslots = list(result.schedule.timeslots.values())

        # For annealing important to NOT select the best swap, but a random one
        draw_move = self.draw_valid_student_move(
            result, timeslots, tried_swaps=self.tried_timeslot_swaps, ceiling=ceiling
        )
        draw_swap = self.draw_valid_timeslot_swap(result, timeslots, self.tried_timeslot_swaps, ceiling=ceiling)

        if draw_move:
            move, move_score = draw_move
            probability_move = self.p(move_score, self.temperature(result))
            move_mutation = self.move_node, [result.schedule, *move]
        else:
            probability_move = 0

        if draw_swap:
            swap, swap_score = draw_swap
            probability_swap = self.p(swap_score, self.temperature(result))
            swap_mutation = self.swap_neighbors, [result.schedule, *swap, "Room"]
        else:
            probability_swap = 0

        # Simulated annealing: accept a random mutation with probability p
        do_move = self.biased_boolean(probability_move)
        do_swap = self.biased_boolean(probability_swap)

        if do_move and do_swap:
            if probability_move > probability_swap:
                return move_mutation
            return swap_mutation
        elif do_move:
            return move_mutation
        elif do_swap:
            return swap_mutation

        return self.suggest_mutation(result, ceiling, _recursion_depth - 1)
