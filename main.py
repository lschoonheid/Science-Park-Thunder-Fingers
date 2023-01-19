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
from code.algorithms.statistics import Statistics
from sched_csv_output import schedule_to_csv


def make_random(stud_prefs_path: str, courses_path: str, rooms_path: str, i_max=None, _recursions=100):
    """Make random schedule."""
    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)
    solver = Randomize()
    verifier = Statistics()

    if not i_max:
        guess_required_edges = 0
        for activity in schedule.activities.values():
            enrolled_students = len(activity.students)
            guess_required_edges += enrolled_students
        i_max = 2 * guess_required_edges

    result = solver.solve(schedule, i_max=i_max)
    if not (result.is_solved()) and _recursions > 0:
        print("Restarting...\n\n")
        return make_random(stud_prefs_path, courses_path, rooms_path, i_max, _recursions=_recursions - 1)

    print(f"Score: {result.score()}")
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
