from ..classes.schedule import Schedule
from .solver import Solver
from .generate import generate_solutions
from .randomize import Randomize
from .statistics import Statistics
import copy


# TODO: #14 implement genetic algorithm to combine schedules into children schedules
class GeneticSolve(Solver):
    def __init__(
        self, students_input, courses_input, rooms_input, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5
    ) -> None:
        self.verifier = Statistics()

        population_size = numberOfChromosomes
        self.population = generate_solutions(
            Randomize(),
            students_input,
            courses_input,
            rooms_input,
            n=population_size,
            compress=False,
        )
