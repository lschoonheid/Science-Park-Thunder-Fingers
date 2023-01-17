"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia Geisler, Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse

# from code.modules.helpers import csv_to_dicts
from code.classes.schedule import Schedule
from code.visualisation.visualize import GraphVisualization
from code.algorithms.genetic import GeneticAlgorithm
from code.algorithms.randomize import connect_random
from code.algorithms.objective import Objective
from sched_csv_output import schedule_to_csv


def random(schedule):
    # make random schedule
    connect_random(schedule, i_max=20)
    objective = Objective(schedule)
    objective.get_score()

    G = GraphVisualization(schedule)
    G.visualize()

    schedule_to_csv(schedule)


# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv",
    courses_path: str = "data/vakken_subset.csv",
    rooms_path: str = "data/zalen.csv",
):
    """Interface for executing scheduling program."""

    protoype = Schedule(stud_prefs_path, courses_path, rooms_path)
    ga = GeneticAlgorithm(protoype)
    ga.run(2)


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(description="Make a schedule.")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
