"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia Geisler, Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse

from program_code.classes import *
from program_code.visualisation.visualize import GraphVisualization, plot_statistics
from program_code.algorithms.genetic import GeneticAlgorithm
from program_code.algorithms.randomize import *
from program_code.algorithms.statistics import Statistics
from sched_csv_output import schedule_to_csv


def generate(solver: Solver, n: int, stud_prefs_path, courses_path, rooms_path, **kwargs):
    """Generate `n` schedules"""
    results: list[Statistics.Result] = []
    for i in tqdm(range(n)):
        schedule = Schedule(stud_prefs_path, courses_path, rooms_path)
        results.append(solver.solve(schedule, **kwargs))
    return results


# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str,
    courses_path: str,
    rooms_path: str,
):
    """Interface for executing scheduling program."""

    results = generate(Randomize(), 1000, stud_prefs_path, courses_path, rooms_path)

    sampled_schedule = random.choice(results).schedule
    G = GraphVisualization(sampled_schedule)
    G.visualize()
    schedule_to_csv(sampled_schedule)

    plot_statistics(results)


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(description="Make a schedule.")

    parser.add_argument(
        "--prefs",
        dest="stud_prefs_path",
        default="data/studenten_en_vakken_subset.csv",
        help="Path to student enrolments csv.",
    )
    parser.add_argument("--courses", dest="courses_path", default="data/vakken_subset.csv", help="Path to courses csv.")
    parser.add_argument("--rooms", dest="rooms_path", default="data/zalen_subset.csv", help="Path to rooms csv.")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
