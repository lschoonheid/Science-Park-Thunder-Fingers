from ..classes.schedule import Schedule
from .solver import Solver
from .generate import generate_solutions
from .randomize import Randomize
from .mutate import Mutations
from .statistics import Statistics
from ..classes.result import Result
import copy


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Randomize, Mutations):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        numberOfChromosomes=100,
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
        # TODO: run update_score()
        return 1 / (1 + result.score)

    def solve(
        self,
        schedule: Schedule | None = None,
        i_max: int | None = None,
    ):
        # Generate population from prototype
        if schedule is None:
            self.initial_population = generate_solutions(
                Randomize(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=False,
                show_progress=False,
            )
        else:
            self.initial_population = [Result(copy.deepcopy(schedule)).compress() for i in range(self.population_size)]

        best_fitness = 0

        # TODO: in a loop: crossover, mutate, select best fit and repeat
        for i in range(100):
            current_generation = i
            self.population = generate_solutions(
                Randomize(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=True,
                show_progress=False,
            )

            # TODO: define crossover
            # TODO: define mutations

            population_sorted = self.sort_objects(self.population, "score")  # type: ignore
            current_best = self.get_fitness(population_sorted[0])
            if current_best > best_fitness:
                best_result = population_sorted[0]
                best_fitness = current_best
            print(f"Score: {best_result.score}\t Generation: {current_generation}", end="\r")
        print("\n")
        if self.verbose:
            print(f"Best found score: {best_result.score}")
        return best_result
