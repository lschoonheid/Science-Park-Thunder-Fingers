from ..classes.schedule import Schedule
import copy


# TODO: #14 implement genetic algorithm to combine schedules into children schedules


class GeneticAlgorithm:
    def __init__(self, prototype, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5) -> None:
        pass


# import multiprocessing


# # Necessary to work around
# def solver_wrapper(arguments):
#     solver, schedule, kwargs = arguments
#     """Execute `solver.solve(schedule, **kwargs)` with `kwargs`."""
#     return solver.solve(schedule, **kwargs)


# num_workers = multiprocessing.cpu_count()
# pool = multiprocessing.Pool(num_workers)
# with pool as p:
#     solver_arguments = [(solver, schedule, kwargs) for schedule in schedules]

#     chunksize, extra = divmod(n, num_workers * 4)
#     if extra:
#         chunksize += 1

#     results = list(
#         tqdm(
#             p.imap(solver_wrapper, solver_arguments, chunksize),
#             total=n,
#             desc="Solving schedules",
#             position=0,
#             leave=" ",
#         )
#     )
# results = list(tqdm(p.starmap(solver_swrapper, solver_arguments), total=n, desc="Instances", position=0, leave=" "))
