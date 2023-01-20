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
from program_code.classes.data import Data
from program_code.classes.schedule import Schedule
from program_code.algorithms.solver import Solver
from program_code.algorithms.randomize import Randomize
from program_code.algorithms.statistics import Statistics
from program_code.visualisation.visualize import GraphVisualization, plot_statistics
from sched_csv_output import schedule_to_csv


def generate(solver: Solver, students_input, courses_input, rooms_input, n: int = 1000, **kwargs):
    """Generate `n` schedules"""
    results: list[Statistics.Result] = []
    for i in tqdm(range(n)):
        schedule = Schedule(students_input, courses_input, rooms_input)
        results.append(solver.solve(schedule, **kwargs))
    return results


# TODO: write interface code to execute complete program from command line
def main(stud_prefs_path: str, courses_path: str, rooms_path: str, n_subset: int, verbose: bool = False, **kwargs):
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

    results = generate(Randomize(verbose=verbose), students_input, courses_input, rooms_input, **kwargs)

    sampled_result = random.choice(results)
    if verbose:
        sampled_result.score_vector
        print(sampled_result)
    G = GraphVisualization(sampled_result.schedule)
    G.visualize()
    schedule_to_csv(sampled_result.schedule)

    if do_plot:
        plot_statistics(results)


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
