import warnings
from ..classes import Schedule, dump_result
from .generate import generate_solutions
from .randomize import Randomize
from .mutate import Mutations
from ..classes.result import Result
import copy
from tqdm import tqdm


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Mutations):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        max_generations=30000,
        # max_generations=35000,
        numberOfChromosomes=100,
        # numberOfChromosomes=100,
        replaceByGeneration=8,
        trackBest=5,
        numberOfCrossoverPoints=2,
        mutationSize=2,
        crossoverProbability=80,
        mutationProbability=3,
        method="min_gaps_overlap",
        verbose=False,
    ) -> None:
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.max_generations = max_generations

        self.method = method
        self.verbose = verbose

        self.population_size = numberOfChromosomes
        self.mutationSize = mutationSize
        self.replaceByGeneration = replaceByGeneration
        self.trackBest = trackBest
        self.numberOfCrossoverPoints = numberOfCrossoverPoints
        self.crossoverProbability = crossoverProbability
        self.mutationProbability = mutationProbability

    def get_fitness(self, result: Result):
        result.update_score()
        return 10000 / (1 + result.score)

    def solve(
        self,
        schedule_seed: Schedule | None = None,
        i_max: int | None = None,
    ):
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

        # Worst score
        best_fitness = 0
        current_best: Result = None  # type: ignore
        generations = 0
        # TODO: in a loop: crossover, mutate, select best fit and repeat
        pbar = tqdm(range(self.max_generations))
        for i in pbar:
            # TODO mark lower half of population for replacement

            population_sorted: list[Result] = self.sort_objects(self.population, "score")  # type: ignore
            current_best: Result = population_sorted[0].decompress(
                self.students_input, self.courses_input, self.rooms_input
            )

            current_best_fitness = self.get_fitness(current_best)
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness

            solved = current_best.check_solved()

            # TODO: define crossover
            # TODO: define mutations
            # TODO do different mutations, depending on highest conflict factor
            # TODO: hillclimber

            # TODO: recursive swapping function
            # TODO: index on swaps already tried
            # TODO: simulated annealing
            # Try swapping timeslots to get a better fitness (or score)
            _old_score = current_best.score

            backup_edges = copy.deepcopy(current_best.schedule.edges)

            swapped = self.swap_random_timeslots(current_best.schedule)
            undid_swap = not swapped
            if not swapped:
                warnings.warn("Had to break here")
                break
            if self.get_fitness(current_best) < current_best_fitness or not current_best.check_solved():
                # Undo swap
                self.swap_neighbors(current_best.schedule, *swapped, skip=["Room"])  # type: ignore
                current_best.update_score()
                undid_swap = True

            if not current_best.check_solved():
                current_best = Result(Schedule(self.students_input, self.courses_input, self.rooms_input, backup_edges))
            generations = i
            pbar.set_description(f"{type(self).__name__} ({self.method}) (score: {current_best.score})")
            # print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")
            if current_best.score == 0:
                break

        output_path = dump_result(current_best, f"output/genetic_{self.max_generations}_")
        print(
            f"Best fitness {self.get_fitness(current_best):5f} \t score: {current_best.score} \nIterations: {generations} \t solved: {current_best.check_solved()} \
            \nScore vector: {current_best.score_vector} \
            \nsaved at {output_path}"
        )

        print("\n")
        if self.verbose:
            print(f"Best found score: {current_best.score}")
        return current_best
