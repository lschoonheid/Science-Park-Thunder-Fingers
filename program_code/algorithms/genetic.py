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
        max_generations=100,
        # max_generations=35000,
        numberOfChromosomes=10,
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
        return 1 / (1 + result.score)

    def solve(
        self,
        seed: Schedule | None = None,
        i_max: int | None = None,
    ):
        # Initialize population from prototype
        if seed is None:
            self.population = generate_solutions(
                Randomize(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=True,
                show_progress=True,
            )
        else:
            self.population = [Result(copy.deepcopy(seed)).compress() for i in range(self.population_size)]

        # Worst score
        best_fitness = 0
        current_best: Result = None  # type: ignore
        # TODO: in a loop: crossover, mutate, select best fit and repeat
        for i in tqdm(range(self.max_generations), disable=True):
            # TODO mark lower half of population for replacement

            population_sorted: list[Result] = self.sort_objects(self.population, "score")  # type: ignore
            current_best: Result = population_sorted[0].decompress(
                self.students_input, self.courses_input, self.rooms_input
            )

            current_best_fitness = self.get_fitness(current_best)
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness

            # TODO: define crossover
            # TODO: define mutations
            # TODO do different mutations, depending on highest conflict factor
            # TODO: hillclimber

            # TODO: recursive swapping function
            # TODO: index on swaps already tried
            # TODO: simulated annealing
            # Try swapping timeslots to get a better fitness (or score)
            swapped = self.swap_random_timeslots(current_best.schedule)
            if not swapped:
                warnings.warn("Had to break here")
                break
            if self.get_fitness(current_best) < current_best_fitness:
                # Undo swap
                self.swap_neighbors(current_best.schedule, *swapped, skip=["Room"])  # type: ignore
                current_best.update_score()

            print(f"Score: {current_best.score} \t Generation: {i + 1 }/{ self.max_generations}", end="\r")

        print(
            f"Best fitness {self.get_fitness(current_best):5f} \t score: {current_best.score} \nIterations: {self.max_generations} \t soved: {current_best.check_solved()}"
        )
        dump_result(current_best, f"output/genetic_{self.max_generations}_")

        print("\n")
        if self.verbose:
            print(f"Best found score: {current_best.score}")
        return current_best
