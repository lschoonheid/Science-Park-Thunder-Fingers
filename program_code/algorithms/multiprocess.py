import multiprocessing
from tqdm import tqdm
from .solver import Solver
from ..classes import Schedule

# Necessary to work around
def solver_wrapper(arguments):
    solver, schedule, kwargs = arguments
    """Execute `solver.solve(schedule, **kwargs)` with `kwargs`."""
    return solver.solve(schedule, **kwargs)


def multi_solve(solver: Solver, students_input, courses_input, rooms_input, n: int = 1000, compress=True, **kwargs):
    schedules = [Schedule(students_input, courses_input, rooms_input) for i in range(n)]

    num_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_workers)
    with pool as p:
        solver_arguments = [(solver, schedule, kwargs) for schedule in schedules]

        chunksize, extra = divmod(n, num_workers * 4)
        if extra:
            chunksize += 1

        results = list(
            tqdm(
                p.imap(solver_wrapper, solver_arguments, chunksize),  # type: ignore
                total=n,
                desc="Solving schedules",
                position=0,
                leave=" ",  # type: ignore
            )
        )
    results = list(tqdm(p.starmap(solver_swrapper, solver_arguments), total=n, desc="Instances", position=0, leave=" "))  # type: ignore
