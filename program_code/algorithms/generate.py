from tqdm import tqdm
from .solver import Solver
from ..classes import Schedule
from ..classes.data import pickle_cache
from ..classes.result import Result


@pickle_cache
def make_prototype(students_input, courses_input, rooms_input):
    return Schedule(students_input, courses_input, rooms_input)


def generate_solutions(
    solver: Solver, students_input, courses_input, rooms_input, n: int = 1000, compress=True, **kwargs
):
    """Generate `n` schedules"""
    results: list[Result] = []
    for n in tqdm(range(n)):
        schedule = make_prototype(students_input, courses_input, rooms_input)
        result = solver.solve(schedule)
        if compress:
            result.compress()
        results.append(result)
    return results
