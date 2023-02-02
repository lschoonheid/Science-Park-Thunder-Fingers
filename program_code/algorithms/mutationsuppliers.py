"""
Individual part
Class for mutation strategies as base for population based algorithms.

Execute from main.py: choose strategy (HillClimber, Simulated Annealing, Directed Simulated Annealing).

Student: Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import random
import numpy as np
from .randomizer import Randomizer
from .statistics import Statistics
from .mutations import MoveStudent, Mutation, SwapStudents, SwapTimeslots
from ..classes import Timeslot
from ..classes.result import Result


class MutationSupplier(Statistics):
    """Mutation supplier parent class. Suggests mutations.

    Increasing `score_scope` increases the amount of mutations to try out.
    `ceiling` defines the maximum score difference a mutation is allowed to bring."""

    def __init__(
        self,
        score_scope: int = 1,
        ceiling=0,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
    ):
        # Score scope is how many timeslots to look at when scoring a swap
        self.score_scope = score_scope
        self.ceiling = ceiling
        self.tried_timeslot_swaps = tried_timeslot_swaps
        self.swap_scores_memory = swap_scores_memory

    def find_mutations(self, result: Result, timeslots: list[Timeslot]) -> list[Mutation]:
        """Find available mutations for each type of mutation"""
        return [
            # Move single student
            MoveStudent(result, timeslots, self.ceiling, self.tried_timeslot_swaps),
            # Swap two students within 2 timeslots
            SwapStudents(result, timeslots, self.ceiling, self.tried_timeslot_swaps),
            # Swap two timeslots
            SwapTimeslots(result, timeslots, self.ceiling, self.tried_timeslot_swaps),
        ]

    def suggest_mutation(self, result: Result, ceiling=0, iterations=0, i_max=1) -> Mutation:
        """Return best possible mutation according to chosen strategy."""
        raise NotImplementedError

    def reset_mutations(self):
        """Clear memory of tried swaps."""
        self.tried_timeslot_swaps.clear()


class HillClimber(MutationSupplier):
    """Supplies mutations with hillclimber strategy. Increasing `score_scope` > 1 results in steepest descent hillclimber."""

    def __init__(
        self,
        score_scope: int = 1,
        ceiling=0,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
    ):
        super().__init__(score_scope, ceiling, tried_timeslot_swaps, swap_scores_memory)

    def suggest_mutation(
        self, result: Result, timeslots=None, _recursion_depth=1000, iterations=0, i_max=1
    ) -> Mutation:
        """Return best possible mutation according to hillclimber strategy."""
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        # Find targets
        if timeslots is None:
            timeslots = list(result.schedule.timeslots.values())

        # Generate possible mutations
        possible_mutations = []
        for i in range(self.score_scope):
            possible_mutations.extend(self.find_mutations(result, timeslots))

        # See which swaps are best
        random.shuffle(possible_mutations)
        best_mutation = min(possible_mutations, key=lambda m: m.score)

        # If best mutation isn't an improvement, try again.
        if best_mutation.score > 0:
            return self.suggest_mutation(result, timeslots, _recursion_depth - 1)

        # Return best found mutation
        return best_mutation


class SimulatedAnnealing(MutationSupplier):
    """Supplies mutations with simulated annealing algorithm."""

    def __init__(
        self,
        score_scope: int = 1,
        tried_timeslot_swaps: set[tuple[int, int]] = set(),
        swap_scores_memory: dict[tuple[Timeslot, Timeslot], int | float] = {},
        T_0: float = 1 / 5,
        ceiling=10,
    ):
        self.T_0 = T_0
        super().__init__(score_scope, ceiling, tried_timeslot_swaps, swap_scores_memory)

    def temperature(self, score: int | float, iterations, i_max) -> float:
        T = self.T_0 * (i_max - iterations) / ((iterations + 1) * i_max)
        return T

    def temperature_lin(self, score: int | float, iterations, i_max) -> float:
        """Linear temperature schedule."""
        floor = 2
        score_0 = 600 + floor
        T = self.T_0 * (score + floor) / score_0
        return T

    def temperature_swq(self, score: int | float, iterations, i_max) -> float:

        """Quadratic temperature schedule."""
        floor = 5
        score_0 = 600 + floor
        return self.T_0 * ((score + floor) / score_0) ** 2

    def temperature_exp(self, score: int | float, iterations, i_max) -> float:

        """Exponential temperature schedule."""
        floor = 5
        score_0 = 600 + floor
        ex = np.exp(-3 * score_0 / (score + floor) + 1)
        return self.T_0 * ex

    def probability(self, diff: int | float, temperature: int | float) -> float:
        """Simulated annealing mutation acceptance probability."""
        # Prevent overflow errors for large differences. If diff is negative, accept mutation.
        if diff < 0:
            return 1

        P = np.exp(-diff / temperature)
        return P

    def suggest_mutation(
        self, result: Result, timeslots: list[Timeslot] | None = None, _recursion_depth=1000, iterations=0, i_max=1
    ) -> Mutation:
        """Return best mutation with simulated annealing."""
        ceiling = self.ceiling
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        # Find targets
        if timeslots is None:
            timeslots = list(result.schedule.timeslots.values())

        # Generate possible mutations
        possible_mutations = []
        for i in range(self.score_scope):
            possible_mutations.extend(self.find_mutations(result, timeslots))

        # Shuffle mutations so that we don't always pick first listed mutation if scores are equal
        random.shuffle(possible_mutations)

        # Go through mutations and return mutation if acceptance critaria are fulfilled
        for mutation in Statistics.sort_objects(possible_mutations, "score"):
            P = self.probability(mutation.score, self.temperature(mutation.score, iterations, i_max))
            do_mutation = Randomizer.biased_boolean(P)

            if do_mutation:
                return mutation

        # Return accepted mutation
        return self.suggest_mutation(result, _recursion_depth=_recursion_depth - 1)


class DirectedSA(SimulatedAnnealing):
    """Supplied mutations with bias towards mutating highest conflict areas."""

    def biased_subjects(self, result: Result, timeslots: list[Timeslot], fraction: float = 1 / 10):
        """Returns a list of subjects that are biased towards the worst subjects."""
        scores = np.array([result.sub_score(t) for t in timeslots])
        total_score = sum(scores)

        selection_size = int(len(timeslots) // (1 / fraction))
        probabilities = selection_size * scores / total_score
        select = [Randomizer.biased_boolean(p) for p in probabilities]

        selection = [subject for subject, select in zip(timeslots, select) if select]

        return selection

    def suggest_mutation(self, result: Result, ceiling=10, _recursion_depth=1000) -> Mutation:
        """Return best mutation."""
        if _recursion_depth == 0:
            raise RecursionError("Recursion depth exceeded")

        all_timeslots = list(result.schedule.timeslots.values())
        timeslots = self.biased_subjects(result, all_timeslots, 1 / 2)

        return super().suggest_mutation(result, timeslots, _recursion_depth)
