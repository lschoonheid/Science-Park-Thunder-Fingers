# from numba import jit
from math import exp
import random
import numpy as np
from typing import Callable
from functools import total_ordering
from .mutator import Mutator
from ..classes import Timeslot
from ..classes.result import Result


class Mutation(Mutator):
    def __init__(
        self,
        action: Callable,
        drawer: Callable[[Result, list, set | None, int | None], tuple | None],
        result: Result,
        targets: list,
        ceiling: int | None = None,
        tried_mutations: set | None = None,
        arguments: dict | None = None,
        inverse: Callable | None = None,
    ):
        self.type = action.__name__
        self.action = action
        self.inverse = inverse
        self.result = result
        self.arguments = arguments

        draw = drawer(result, targets, tried_mutations, ceiling)
        if draw:
            self.subjects, self.score = draw

    def apply(self):
        if self.arguments:
            return self.action(self.result.schedule, *self.subjects, **self.arguments)
        return self.action(self.result.schedule, *self.subjects)

    def revert(self):
        if self.inverse:
            if self.arguments:
                return self.inverse(self.result.schedule, *self.subjects, **self.arguments)
            return self.inverse(self.result.schedule, *self.subjects)

        raise NotImplementedError


class MutationSupplier(Mutator):
    def __init__(
        self,
        score_scope: int = 2,
        ceiling=0,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
    ):
        # Score scope is how many timeslots to look at when scoring a swap
        self.score_scope = score_scope
        self.ceiling = ceiling
        self.tried_timeslot_swaps = tried_timeslot_swaps
        self.swap_scores_memory = swap_scores_memory

    def suggest_mutation(self, result: Result, ceiling=0):
        """Generate possible swap."""
        raise NotImplementedError

    def reset_mutations(self):
        self.tried_timeslot_swaps.clear()


class HillClimber(MutationSupplier):
    def __init__(
        self,
        score_scope: int = 2,
        ceiling=0,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
    ):
        super().__init__(score_scope, ceiling, tried_timeslot_swaps, swap_scores_memory)

    def suggest_mutation(
        self,
        result: Result,
        timeslots=None,
        _recursion_depth=1000,
    ):
        ceiling = self.ceiling
        # See which swaps are best

        if timeslots is None:
            timeslots = list(result.schedule.timeslots.values())

        timeslots = list(result.schedule.timeslots.values())
        # For annealing important to NOT select the best swap, but a random one
        possible_mutations = []

        for i in range(self.score_scope):
            possible_mutations.extend(
                [
                    # Move single student
                    Mutation(
                        self.move_node,
                        self.draw_valid_student_move,
                        result,
                        timeslots,
                        ceiling,
                    ),
                    # Swap two timeslots
                    Mutation(
                        self.swap_neighbors,
                        self.draw_valid_timeslot_swap,
                        result,
                        timeslots,
                        ceiling,
                        self.tried_timeslot_swaps,
                        {"skip": "Room"},
                    ),
                    # Swap two students within 2 timeslots
                    Mutation(
                        self.swap_students_timeslots,
                        self.draw_valid_student_swap,
                        result,
                        timeslots,
                        ceiling,
                        self.tried_timeslot_swaps,
                    ),
                ]
            )

        random.shuffle(possible_mutations)
        best_mutation = min(possible_mutations, key=lambda m: m.score)

        if best_mutation.score > 0:
            return self.suggest_mutation(result, timeslots, _recursion_depth - 1)

        return best_mutation


class SimulatedAnnealing(MutationSupplier):
    def __init__(
        self,
        score_scope: int = 10,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
        # T_0: float = 1 / 1000000,
        T_0: float = 1,
        ceiling=10,
        # T_0: float = 1 / 10,
    ):
        self.T_0 = T_0
        super().__init__(score_scope, ceiling, tried_timeslot_swaps, swap_scores_memory)

    def temperature(self, score: int | float) -> float:
        floor = 2
        score_0 = 600 + floor
        return self.T_0 * (score + floor) / score_0

    def temperature_sqr(self, score: int | float) -> float:
        floor = 5
        score_0 = 600 + floor
        return self.T_0 * ((score + floor) / score_0) ** 2

    def temperature_exp(self, score: int | float) -> float:
        floor = 5
        score_0 = 600 - floor
        ex = np.exp(-score_0 / (score + floor) + 1)
        return self.T_0 * ex

    # @jit()
    def probability(self, diff, temperature) -> float:

        # Subtract 0.69315 so a diff of 0 results in 50 percent chance of change
        return np.exp(-diff / temperature)
        return np.exp(-diff / temperature - 0.69315)

    def suggest_mutation(
        self,
        result: Result,
        timeslots: list[Timeslot] | None = None,
        _recursion_depth=1000,
    ):
        ceiling = self.ceiling
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        if timeslots is None:
            timeslots = list(result.schedule.timeslots.values())

        # For annealing important to NOT select the best swap, but a random one
        # TODO implement score scope, try more mutations
        possible_mutations = [
            Mutation(
                self.move_node,
                self.draw_valid_student_move,
                result,
                timeslots,
                ceiling,
            ),
            Mutation(
                self.swap_neighbors,
                self.draw_valid_timeslot_swap,
                result,
                timeslots,
                ceiling,
                self.tried_timeslot_swaps,
                {"skip": "Room"},
            ),
            Mutation(
                self.swap_students_timeslots,
                self.draw_valid_student_swap,
                result,
                timeslots,
                ceiling,
                self.tried_timeslot_swaps,
            ),
        ]

        # Shuffle mutations so that we don't always pick move_node if scores are equal
        random.shuffle(possible_mutations)

        for mutation in self.sort_objects(possible_mutations, "score"):
            P = self.probability(mutation.score, self.temperature(result.score))
            do_mutation = self.biased_boolean(P)

            if do_mutation:
                if mutation.type == "swap_students_timeslots":
                    pass
                return mutation

        return self.suggest_mutation(result, _recursion_depth=_recursion_depth - 1)


class DirectedSA(SimulatedAnnealing):
    def biased_subjects(self, result: Result, timeslots: list[Timeslot], fraction: float = 1 / 10):
        """Returns a list of subjects that are biased towards the worst subjects."""
        scores = np.array([result.sub_score(t) for t in timeslots])
        total_score = sum(scores)

        selection_size = int(len(timeslots) // (1 / fraction))
        probabilities = selection_size * scores / total_score
        select = [self.biased_boolean(p) for p in probabilities]

        selection = [subject for subject, select in zip(timeslots, select) if select]

        return selection

    def suggest_mutation(self, result: Result, ceiling=10, _recursion_depth=1000):
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        all_timeslots = list(result.schedule.timeslots.values())
        timeslots = self.biased_subjects(result, all_timeslots, 1 / 2)

        return super().suggest_mutation(result, timeslots, _recursion_depth)
