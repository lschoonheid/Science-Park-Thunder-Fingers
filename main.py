"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia Geisler, Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse
import random
import warnings
from tqdm import tqdm

# import multiprocessing
from program_code.classes.data import Data, pickle_cache
from program_code.classes.schedule import Schedule
from program_code.algorithms.solver import Solver
from program_code.algorithms.randomize import Randomize
from program_code.algorithms.statistics import Statistics
from program_code.classes.result import Result
from program_code.visualisation.visualize import GraphVisualization, plot_statistics
from sched_csv_output import schedule_to_csv


# # Necessary to work around
# def solver_wrapper(arguments):
#     solver, schedule, kwargs = arguments
#     """Execute `solver.solve(schedule, **kwargs)` with `kwargs`."""
#     return solver.solve(schedule, **kwargs)


@pickle_cache
def make_prototype(students_input, courses_input, rooms_input):
    return Schedule(students_input, courses_input, rooms_input)


def generate(solver: Solver, students_input, courses_input, rooms_input, n: int = 1000, compress=False, **kwargs):
    """Generate `n` schedules"""
    statistics = Statistics()

    results: list[Result] = []
    # if 300 < n < 1000:
    # for schedule in tqdm(schedules, "Solving schedules"):
    # TODO: #37 compress data: save only edges and scorevector

    for n in tqdm(range(n)):
        schedule = make_prototype(students_input, courses_input, rooms_input)
        result = solver.solve(schedule)
        if compress:
            result.compress()
        results.append(result)
    # TODO pickle dump data?
    return results

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


# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str,
    courses_path: str,
    rooms_path: str,
    n_subset: int,
    verbose: bool = False,
    do_plot: bool = True,
    **kwargs,
):
    """Interface for executing scheduling program."""

    input_data = Data(stud_prefs_path, courses_path, rooms_path)
    students_input = input_data.students
    courses_input = input_data.courses
    rooms_input = input_data.rooms

    if n_subset:
        if n_subset > len(students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            students_input = random.sample(students_input, n_subset)

    results_compressed = generate(Randomize(verbose=verbose), students_input, courses_input, rooms_input, **kwargs)
    sampled_result = random.choice(results_compressed)

    prototype = Schedule(students_input, courses_input, rooms_input)
    sampled_result.decompress(prototype)
    if verbose:
        sampled_result.score_vector
        print(sampled_result)

    prototype = Schedule(students_input, courses_input, rooms_input)

    G = GraphVisualization(sampled_result.schedule)
    G.visualize()
    schedule_to_csv(sampled_result.schedule)

    if do_plot:
        plot_statistics(results_compressed)


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(prog="main.py", description="Make a schedule.")

    parser.add_argument(
        "--prefs",
        dest="stud_prefs_path",
        default="data/studenten_en_vakken.csv",
        help="Path to student enrolments csv.",
    )
    parser.add_argument("-i", type=int, dest="i_max", help="max iterations per solve cycle.")
    parser.add_argument("-n", type=int, dest="n", default=1, help="amount of results to generate.")
    parser.add_argument(
        "-sub", type=int, dest="n_subset", help="Subset: amount of students to take into account out of dataset."
    )
    parser.add_argument("-v", dest="verbose", action="store_true", help="Verbose: log error messages.")
    parser.add_argument("--courses", dest="courses_path", default="data/vakken.csv", help="Path to courses csv.")
    parser.add_argument("--rooms", dest="rooms_path", default="data/zalen.csv", help="Path to rooms csv.")
    parser.add_argument("--no_plot", dest="do_plot", action="store_false", help="Don't show matplotlib plot")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
