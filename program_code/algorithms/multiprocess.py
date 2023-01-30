import multiprocessing
from tqdm import tqdm
from .solver import Solver

# Necessary to work around
def solver_wrapper(arguments):
    solver, kwargs = arguments
    """Execute `solver.solve(schedule, **kwargs)` with `kwargs`."""
    return solver.solve(**kwargs)


def multi_solve(solver: Solver, n: int = 1000, compress=True, show_progress=True, **kwargs):
    solver_arguments = [(solver, kwargs) for i in range(n)]

    num_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_workers, initargs=(multiprocessing.RLock(),), initializer=tqdm.set_lock)

    # chunksize, extra = divmod(n, num_workers * 4)
    # if extra:
    #     chunksize += 1
    chunksize = 1

    with pool as p:
        results = list(
            tqdm(
                p.imap(solver_wrapper, solver_arguments, chunksize),  # type: ignore
                total=n,
                desc="Solving schedules",
                position=0,
                leave=True,  # type: ignore
            )
        )
    return results
