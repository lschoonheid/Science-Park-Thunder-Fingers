"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia Geisler, Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse

from code.classes import *
from code.visualisation.visualize import GraphVisualization
from code.algorithms.genetic import GeneticAlgorithm
from code.algorithms.randomize import *
from code.algorithms.objective import Objective
from sched_csv_output import schedule_to_csv


def make_random(stud_prefs_path: str, courses_path: str, rooms_path: str, i_max=50):
    """Make random schedule."""
    randomizer = Randomize()
    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)
    got_solution = randomizer.uniform_strict(schedule, i_max=i_max)

    objective = Objective(schedule)
    objective.get_score()

    if not (got_solution):
        print("Restarting...\n\n")
        make_random(stud_prefs_path, courses_path, rooms_path, i_max)
    return schedule


# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str,
    courses_path: str,
    rooms_path: str,
):
    """Interface for executing scheduling program."""

    # ga = GeneticAlgorithm(protoype)
    # ga.run(2)
    schedule = make_random(stud_prefs_path, courses_path, rooms_path)
    schedule_to_csv(schedule)

    G = GraphVisualization(schedule)
    G.visualize()


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
