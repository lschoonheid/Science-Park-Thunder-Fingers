import warnings
from ..classes import Schedule, Timeslot, dump_result
from .generate import generate_solutions
from .randomizer import Randomizer
from .mutator import Mutator
from .mutationsuppliers import MutationSupplier, SimulatedAnnealing, HillClimber, Mutation
from ..classes.result import Result
import copy
from tqdm import tqdm
import matplotlib.pyplot as plt
import time


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolver(Mutator):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        population_size=5,
        max_generations=20000,
        method="min_gaps_overlap",
        mutation_supplier: MutationSupplier = SimulatedAnnealing(),
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
        self_repair=False,
    ):
        """
        TODO mark lower half of population for replacement
        TODO: define crossover
        TODO: define mutations
        TODO do different mutations, depending on highest conflict factor
        TODO: statistics of different methods
        - TODO: hillclimber
        - TODO: recursive swapping function
        TODO: index on swaps already tried
        - TODO: simulated annealing PRIORITY
        - TODO: fix swapping function resulting in bad solution PRIORITY
        TODO:  define mutation on swapping students
        TODO: Track score over time
        - TODO: Sub score function per timeslot, only consider students involved with timeslot for much faster score difference calculation
        - TODO: Build population of mutations and take best score differences , steepest decent: number of mutations = decent scope
        - TODO: Simulated annealing

        - TODO: hillclimber for first part, then simulated annealing for second part? PRIORITY

        """

        if i_max is None:
            i_max = self.max_generations

        # Initialize population from prototype
        if schedule_seed is None:
            self.population = generate_solutions(
                Randomizer(self.students_input, self.courses_input, self.rooms_input, method=self.method),
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
        pbar = tqdm(range(i_max), position=0, leave=True)
        for i in pbar:

            # Check if solution is found
            if current_best.score == 0:
                break

            if self_repair and self.fitness(current_best.score) > best_fitness and current_best.check_solved():
                backup_edges = copy.deepcopy(current_best.schedule.edges)
                best_score = current_best.score
                best_fitness = self.fitness(best_score)

            # TODO Possible to do relaxation here
            # Get suggestion for possible mutation
            mutation: Mutation = self.mutation_supplier.suggest_mutation(current_best)

            # Apply mutation
            mutation.apply()

            # Check if mutation is better
            if self_repair and not current_best.check_solved():
                # If better, keep mutation, else revert
                # TODO execute inverse of mutation for any mutation
                current_best = Result(Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges))
                # self.mutation_supplier.tried_timeslot_swaps.add(swapped_ids)
                continue
            #  Clear memory of swaps because of new schedule
            self.mutation_supplier.reset_mutations()

            if not self_repair and i % 20 == 0:
                current_best.update_score()
            # Try swapping timeslots to get a better fitness (or score)
            # Describe progress
            pbar.set_description(
                f"{type(self).__name__} ({type(self.mutation_supplier).__name__}) (score: {current_best.score}) (best swap memory {len(self.mutation_supplier.swap_scores_memory) } tried swaps memory {len(self.mutation_supplier.tried_timeslot_swaps) })"
            )
            # print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")

            if mutation.type == "swap_students_timeslots":
                pass
            # Track progress
            generations = i
            track_scores.append(current_best.score)  # type: ignore
            timestamps.append(time.time() - start_time)

        # Dump results
        strategy_name = self.mutation_supplier.__class__.__name__
        score = current_best.score
        dump_result(
            [current_best, timestamps],
            f"output/genetic_{strategy_name}_score{score}_scorestime_{self.max_generations}_",
        )
        output_path = dump_result(current_best, f"output/genetic_{strategy_name}_{score}_{self.max_generations}_")

        # Output results to console
        print(
            f"\nBest score: {current_best.score} \
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
