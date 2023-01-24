from ..classes.schedule import Schedule
from .solver import Solver
from .generate import generate_solutions
from .randomize import Randomize
from .statistics import Statistics
from ..classes.result import Result
import copy


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Solver):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        numberOfChromosomes=100,
        replaceByGeneration=8,
        trackBest=5,
        verifier=Statistics(),
        method="uniform",
        verbose=False,
    ) -> None:
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.verifier = verifier
        self.method = method
        self.verbose = verbose

        self.population_size = numberOfChromosomes

    def get_fitness(self, result: Result):
        return 1 / (1 + result.get_score())

    def solve(
        self,
        schedule: Schedule | None = None,
        i_max: int | None = None,
    ):
        # Generate population from prototype
        if schedule is None:
            self.population = generate_solutions(
                Randomize(self.students_input, self.courses_input, self.rooms_input, method=self.method),
                n=self.population_size,
                compress=False,
            )
        else:
            self.population = [Result(copy.deepcopy(schedule)) for i in range(self.population_size)]

        # TODO: define crossover
        # TODO: define mutations
        # TODO: in a loop: crossover, mutate, select best fit and repeat

        return Result(Schedule([], [], []))
