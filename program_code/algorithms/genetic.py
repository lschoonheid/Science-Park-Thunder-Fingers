import warnings
from ..classes import Schedule, Timeslot, dump_result
from .generate import generate_solutions
from .randomize import Randomize
from .mutate import Mutations
from ..classes.result import Result
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import time


# from numba import jit
from math import exp
import numpy as np


class MutationSupplier(Mutations):
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

    def suggest_swap(self):
        raise NotImplementedError

    def reset_swaps(self):
        self.tried_swaps.clear()


class SteepestDescent(MutationSupplier):
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

        e = exp(-beta * diff)
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


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Mutations):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        population_size=50,
        max_generations=10000,
        method="min_gaps_overlap",
        mutation_supplier=SimulatedAnnealing(),
        verbose=False,
    ) -> None:
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.population_size = population_size
        self.max_generations = max_generations

        self.method = method
        self.mutation_supplier = mutation_supplier

        self.verbose = verbose

    def fitness(self, score: float | int):
        """Get fitness of a result."""
        return 10000 / (1 + score)

    def solve(
        self,
        schedule_seed: Schedule | None = None,
        i_max: int | None = None,
    ):
        """
        TODO mark lower half of population for replacement
        TODO: define crossover
        TODO: define mutations
        TODO do different mutations, depending on highest conflict factor
        TODO: statistics of different methods
        TODO: hillclimber
        TODO: recursive swapping function
        TODO: index on swaps already tried
        TODO: simulated annealing PRIORITY
        TODO: fix swapping function resulting in bad solution PRIORITY
        TODO:  define mutation on swapping students
        TODO: Track score over time
        - TODO: Sub score function per timeslot, only consider students involved with timeslot for much faster score difference calculation
        - TODO: Build population of mutations and take best score differences , steepest decent: number of mutations = decent scope
        TODO: Simulated annealing

        TODO: hillclimber for first part, then simulated annealing for second part? PRIORITY

        Notable: simulated annealing is much faster than hillclimber, but hillclimber is much more effective
        """
        # Initialize population from prototype
        if schedule_seed is None:
            self.population = generate_solutions(
                Randomize(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=True,
                show_progress=True,
            )
        else:
            self.population = [Result(copy.deepcopy(schedule_seed)).compress() for i in range(self.population_size)]

        population_sorted: list[Result] = self.sort_objects(self.population, "score")  # type: ignore
        current_best: Result = population_sorted[0].decompress(
            self.students_input, self.courses_input, self.rooms_input
        )
        backup_edges = copy.deepcopy(current_best.schedule.edges)

        start_time = time.time()
        best_fitness = 0
        best_score = None
        track_scores: list[float] = []
        timestamps = []
        generations = 0
        # TODO: in a loop: crossover, mutate, select best fit and repeat
        pbar = tqdm(range(self.max_generations), position=0, leave=True)
        for i in pbar:
            # Try swapping timeslots to get a better fitness (or score)
            # Describe progress
            pbar.set_description(
                f"{type(self).__name__} ({type(self.mutation_supplier).__name__}) (score: {current_best.score}) (best swap memory {len(self.mutation_supplier.swap_scores_memory) } tried swaps memory {len(self.mutation_supplier.tried_swaps) })"
            )
            # print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")

            # Check if solution is found
            if current_best.score == 0:
                break

            current_best.update_score()
            if self.fitness(current_best.score) > best_fitness and current_best.check_solved():
                backup_edges = copy.deepcopy(current_best.schedule.edges)
                best_score = current_best.score
                best_fitness = self.fitness(best_score)

            # TODO Possible to do relaxation here
            # Get suggestion for possible mutation
            suggested_swap = self.mutation_supplier.suggest_swap(current_best)
            if not suggested_swap:
                break
            id1, id2 = suggested_swap
            swapped_nodes = current_best.schedule.nodes[id1], current_best.schedule.nodes[id2]

            # Apply mutation
            self.swap_neighbors(current_best.schedule, *swapped_nodes, skip=["Room"])  # type: ignore
            swapped_ids = suggested_swap

            # Check if mutation is better
            if not current_best.check_solved():
                # If better, keep mutation, else revert
                current_best = Result(Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges))
                self.mutation_supplier.tried_swaps.add(swapped_ids)
                continue
            #  Clear memory of swaps because of new schedule
            self.mutation_supplier.reset_swaps()

            # Track progress
            generations = i
            track_scores.append(current_best.score)  # type: ignore
            timestamps.append(time.time() - start_time)

        # Dump results
        strategy_name = self.mutation_supplier.__class__.__name__
        dump_result([current_best, timestamps], f"output/genetic_{strategy_name}_scorestime_{self.max_generations}_")
        output_path = dump_result(current_best, f"output/genetic_{strategy_name}_{self.max_generations}_")

        # Output results to console
        print(
            f"Best score: {current_best.score} \
            \nIterations: {generations} \t solved: {current_best.check_solved()} \
            \nScore vector: {current_best.score_vector} \
            \nsaved at {output_path}"
        )

        # Show score over time
        plt.plot(timestamps, track_scores)
        plt.xlabel("Time (s)")
        plt.ylabel("Score")
        plt.show()

        return current_best
