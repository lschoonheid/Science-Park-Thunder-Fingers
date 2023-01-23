from tqdm import tqdm
from ..classes import Schedule
from ..classes.data import pickle_cache
from ..classes.result import Result


@pickle_cache
def make_prototype(students_input, courses_input, rooms_input):
    return Schedule(students_input, courses_input, rooms_input)


def generate_solutions(solver, n: int = 1000, compress=True, **kwargs):
    """Generate `n` schedules"""
    solver_name = type(solver).__name__

    results: list[Result] = []
    for n in tqdm(range(n), f"{solver_name}"):
        result: Result = solver.solve()
        if compress:
            result.compress()
        results.append(result)
    return results
