import multiprocessing
import warnings
from tqdm import tqdm
from ..classes import Schedule

# from ....helpers.data import pickle_cache
from ..helpers.data import pickle_cache
from ..classes.result import Result


@pickle_cache
def make_prototype(students_input, courses_input, rooms_input):
    return Schedule(students_input, courses_input, rooms_input)


# Necessary to work around
def solver_wrapper(arguments):
    solver, kwargs = arguments
    """Execute `solver.solve(schedule, **kwargs)` with `kwargs`."""
    return solver.solve(**kwargs)


def generate_solutions(solver, n: int = 1, compress=True, show_progress=True, multithreading=True, **kwargs):
    """Generate `n` solutions for schedule.

    `compress`: compresses results during calculation. Saves memory, but not implemented for multithreading.
    `multithreading`: enables mapping processes to individual machine cores to utilise more performance.
    `kwargs`: possible arguments for `solver`.
    """

    # If multithreading is not enabled, simply run a loop
    if not multithreading:
        results: list[Result] = []
        for n in tqdm(range(n), "Solving schedules", disable=not show_progress or n == 1):
            result: Result = solver.solve(**kwargs)
            if compress:
                result.compress()
            results.append(result)
        return results

    if multithreading and compress:
        warnings.warn("Compression currently disabled for multithreading operations.")

    # Generate arguments for `solver` for all instances
    solver_arguments = [(solver, kwargs) for i in range(n)]

    num_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_workers, initargs=(multiprocessing.RLock(),), initializer=tqdm.set_lock)

    # Map jobs to cores and retrieve results
    with pool as p:
        results = list(
            tqdm(
                p.imap(solver_wrapper, solver_arguments),
                total=n,
                desc="Solving schedules",
                position=0,
                leave=True,
                disable=not show_progress or n == 1,
            )
        )
    return results
