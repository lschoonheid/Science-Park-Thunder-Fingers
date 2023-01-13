"""
Interface for executing scheduler program.

Execute: `python3 main.py -h` for usage.

Student: Anna Neefjes, Julia TODO, #17 Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


import argparse

# from code.modules.helpers import csv_to_dicts
from code.classes.schedule import Schedule


# TODO: write interface code to execute complete program from command line
def main(
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv",
    courses_path: str = "data/vakken_subset.csv",
    rooms_path: str = "data/zalen.csv",
):
    """Interface for executing scheduling program."""

    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)


if __name__ == "__main__":
    # Create a command line argument parser
    parser = argparse.ArgumentParser(description="Make a schedule.")

    # Read arguments from command line
    args = parser.parse_args()
    kwargs = vars(args)

    # Run program through interface with provided arguments
    main(**kwargs)
