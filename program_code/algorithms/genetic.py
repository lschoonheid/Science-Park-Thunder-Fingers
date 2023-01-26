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

# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Mutations):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        # max_generations=40,
        max_generations=5000,
        population_size=1,
        # population_size=50,
        decent_scope=10,
        # replaceByGeneration=8,
        # trackBest=5,
        # numberOfCrossoverPoints=2,
        # mutationSize=2,
        # crossoverProbability=80,
        # mutationProbability=3,
        method="min_gaps_overlap",
        verbose=False,
    ) -> None:
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.max_generations = max_generations

        self.method = method
        self.verbose = verbose

        self.population_size = population_size
        self.decent_scope = decent_scope
        # self.mutationSize = mutationSize
        # self.replaceByGeneration = replaceByGeneration
        # self.trackBest = trackBest
        # self.numberOfCrossoverPoints = numberOfCrossoverPoints
        # self.crossoverProbability = crossoverProbability
        # self.mutationProbability = mutationProbability

    def fitness(self, score: float | int):
        """Get fitness of a result."""
        return 10000 / (1 + score)

    def get_swap_scores_timeslot(
        self, result: Result, scope: int, tried_swaps: set[tuple[int, int]], ceiling: int | float | None = 0
    ):
        """Get scores differences for `scope` possible swaps."""
        swap_scores: dict[tuple[int, int], int | float] = {}
        timeslots = list(result.schedule.timeslots.values())
        for i in range(scope):
            draw = self.draw_uniform_recursive(
                timeslots,
                timeslots,
                lambda t1, t2: self.allow_swap_timeslot(result, t1, t2, score_ceiling=ceiling),
                return_value=True,
                # TODO: remember illegal swaps in between tries
                _combination_set=tried_swaps,
            )  # type: ignore
            if not draw:
                break
            tA, tB, score = draw  # type: ignore
            if ceiling is not None and score > ceiling:
                continue
            # Sort by id, make sure swap_scores has no duplicates
            id1, id2 = sorted([tA.id, tB.id])
            swap_scores[(id1, id2)] = score
        return swap_scores

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
        TODO: simulated annealing
        TODO: Track score over time
        TODO: Sub score function per timeslot, only consider students involved with timeslot for much faster score difference calculation
        TODO: Build population of mutations and take best score differences , steepest decent: number of mutations = decent scope
        TODO: Simulated annealing
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
        swap_scores_memory: dict[tuple[int, int], int | float] = {}
        backup_edges = copy.deepcopy(current_best.schedule.edges)

        best_fitness = 0
        best_score = None
        scores_over_time: list[float] = []
        timestamps = []
        # current_best: Result = None  # type: ignore
        generations = 0
        # TODO: order swap pairs
        tried_swaps: set[tuple[int, int]] = set()
        # TODO: in a loop: crossover, mutate, select best fit and repeat
        pbar = tqdm(range(self.max_generations), position=0, leave=True)
        for i in pbar:
            # Try swapping timeslots to get a better fitness (or score)

            current_best.update_score()
            if self.fitness(current_best.score) > best_fitness and current_best.check_solved():
                backup_edges = copy.deepcopy(current_best.schedule.edges)
                best_score = current_best.score
                best_fitness = self.fitness(best_score)

            # See which swaps are best
            swap_scores = self.get_swap_scores_timeslot(current_best, self.decent_scope, tried_swaps)
            # TODO: make this a priority queue
            # if len(swap_scores_memory) > 4000:
            #     swap_scores_memory.clear()
            # tried_swaps.union(swap_scores.keys())
            swap_scores_memory.update(swap_scores)
            best_swap_ids: tuple[int, int] = min(swap_scores, key=swap_scores.get)  # type: ignore
            best_swap_score = swap_scores[best_swap_ids]
            del swap_scores_memory[best_swap_ids]
            # swap_scores_sorted = sorted(swap_scores.items(), key=lambda item: item[1])
            # best_swap_score = swap_scores_sorted[0][1]
            # best_swap = swap_scores_sorted[0][0]

            # TODO Possible to do simulated annealing here
            if best_swap_score > 0:
                continue

            # TODO Possible to do relaxation here
            id1, id2 = best_swap_ids
            swapped_nodes = current_best.schedule.nodes[id1], current_best.schedule.nodes[id2]
            self.swap_neighbors(current_best.schedule, *swapped_nodes, skip=["Room"])  # type: ignore
            swapped_ids = best_swap_ids
            # swapped = best_swap

            # # swapped = self.swap_random_timeslots(current_best, tried_swaps=tried_swaps)
            # if not swapped:
            #     warnings.warn("Could no longer find available swaps before end of max_generations.")
            #     break

            if not current_best.check_solved():
                current_best = Result(Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges))
                tried_swaps.add(swapped_ids)
                continue

            # Score of REVERSING the swap
            score_diff = self.swap_score_timeslot(current_best, *swapped_nodes)  # type: ignore
            # swapped = self.swap_random_timeslots(current_best, tried_swaps=tried_swaps)

            # current_best.update_score()
            # if current_best.score > best_score:
            if score_diff < 0:
                # Swap was uneffective, undo swap
                self.swap_neighbors(current_best.schedule, *swapped, skip=["Room"])  # type: ignore
                current_best.update_score()
                tried_swaps.add(swapped_ids)
            else:
                # Succesful swap, clear memory of tried swaps
                # TODO: don't clear?
                tried_swaps.clear()

            generations = i
            pbar.set_description(
                f"{type(self).__name__} ({self.method}) (score: {current_best.score}) (best swap memory {len(swap_scores_memory) } tried swaps memory {len(tried_swaps) })"
            )
            # print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")

            scores_over_time.append(best_score)  # type: ignore
            timestamps.append(time.time())
            if current_best.score == 0:
                break

        dump_result([current_best, timestamps], f"output/genetic_steepest_scorestime_{self.max_generations}_")
        output_path = dump_result(current_best, f"output/genetic_{self.max_generations}_")
        print(
            f"Best score: {current_best.score} \
            \nIterations: {generations} \t solved: {current_best.check_solved()} \
            \nScore vector: {current_best.score_vector} \
            \nsaved at {output_path}"
        )

        plt.plot(timestamps, scores_over_time)
        plt.show()

        return current_best
