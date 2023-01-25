"""
Individueel onderdeel
Interface for executing timetable program.

Execute: `python3 timetable.py`.

Student: Julia Geisler
Course: Algoritmen en Heuristieken 2023
"""

import csv
import matplotlib.pyplot as plt
# import pandas as pd
import numpy as np

import argparse
import random
import warnings
from program_code import (
    Data,
    generate_solutions,
    Randomize,
    Schedule)

PERIODS = ("9 - 11", "11 - 13", "13 - 15", "15 - 17", "17 - 19")
WEEK_DAYS = ("MA", "DI", "WO", "DO", "VR")
ROOMS = ["A1.04","A1.06","A1.08","A1.10","B0.201","C0.110","C1.112"]

""" 
main function is a selected copy from main.py 
to assure timetable.py can be run independently
"""
def main(stud_prefs_path: str, courses_path: str, rooms_path: str, n_subset: int, verbose: bool = False, **kwargs):
    """Interface for executing scheduling program."""
    # Load dataset
    input_data = Data(stud_prefs_path, courses_path, rooms_path)
    students_input = input_data.students
    courses_input = input_data.courses
    rooms_input = input_data.rooms

    # Optionally take subset of data
    if n_subset:
        if n_subset > len(students_input):
            warnings.warn("WARNING: Chosen subset size is larger than set size, continuing anyway.")
        else:
            students_input = random.sample(students_input, n_subset)

    # Generate (compressed) results: only return scorevector and edges
    results_compressed = generate_solutions(
        Randomize(
            students_input,
            courses_input,
            rooms_input,
            verbose=verbose,
        ),
        **kwargs,
    )

    # Take random sample and rebuild schedule from edges
    sampled_result = random.choice(results_compressed)
    sampled_result.decompress(
        students_input,
        courses_input,
        rooms_input,
    )

    plot_timetable(sampled_result.schedule)
 
def csv_timetable(schedule: Schedule, spec: str = None):
    """Interface for executing timetable program."""
    match spec:
        case "-s":
            stud_sched_csv(schedule)
        case "-c":
            course_sched_csv(schedule)
        case "-r":
            room_sched_csv(schedule)
        # run all three if no specificity is given
        case None:
            stud_sched_csv(schedule)
            course_sched_csv(schedule)
            room_sched_csv(schedule)

def stud_sched_csv(schedule: Schedule):
    # generate student information from random student in schedule
    student = random.choice(schedule.students)
    timeslots = sorted(list(student.timeslots.values()), key=lambda x: x.moment)

    # output path + file name
    output_path = f"output/{student.name}_schedule_output.csv"

    # header
    field_names = ["dag","tijdslot","vak","activiteit","zaal"]

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for timeslot in timeslots:
                for activity in timeslot.activities.values():
                    for course in activity.courses.values():
                        data = [
                            timeslot.day_names[timeslot.day],
                            timeslot.period_names[timeslot.period],
                            course.name,
                            activity.act_type,
                            timeslot.room.name,
                        ]
                        writer.writerow(data)

        print(f"output saved to {output_path}")
        return student

def course_sched_csv(schedule: Schedule):
    # generate course information from random course in schedule
    course = random.choice(list(schedule.courses.values()))
    for activity in course.activities.values():
        for timeslot in activity.timeslots.values():
            schedule.connect_nodes(course, timeslot)
    timeslots = sorted(list(course.timeslots.values()), key=lambda x: x.moment)

    # output path + file name
    output_path = f"output/{course.name}_schedule_output.csv"

    # header
    field_names = ["dag","tijdslot","activiteit","zaal", "studenten"]

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for timeslot in timeslots:
                for activity in timeslot.activities.values():
                    data = [
                        timeslot.day_names[timeslot.day],
                        timeslot.period_names[timeslot.period],
                        activity.act_type,
                        timeslot.room.name,
                        list(timeslot.students.values()),
                    ]
                    writer.writerow(data)

        print(f"output saved to {output_path}")

def room_sched_csv(schedule: Schedule):
    # generate course information from random course in schedule
    # room = random.choice(list(schedule.rooms.values()))
    print(schedule.rooms.values())
    # timeslots = sorted(list(room.timeslots.values()), key=lambda x: x.moment)
    # print(timeslots)
    # output path + file name
    output_path = f"output/room_schedule_output.csv"

    # header
    field_names = ["zaal","dag","tijdslot","vak","activiteit", "studenten"]

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for room in schedule.rooms.values():
            timeslots = sorted(list(room.timeslots.values()), key=lambda x: x.moment)
            for timeslot in timeslots:
                    for activity in timeslot.activities.values():
                        data = [
                            room.name,
                            timeslot.day_names[timeslot.day],
                            timeslot.period_names[timeslot.period],
                            random.choice(list(activity.courses.values())),
                            activity.act_type,
                            list(timeslot.students.values()),
                        ]
                        writer.writerow(data)

        print(f"output saved to {output_path}")

def plot_timetable(schedule: Schedule):
    
    timeslots = sorted(list(schedule.timeslots.values()), key=lambda x: x.moment)
    # for timeslot in timeslots:
    #         print(timeslot,timeslot.activities.values())

    for timeslot in timeslots:
        print(timeslot.day_names[timeslot.day])
        print(timeslot.period_names[timeslot.period])
        data = [
            timeslot.room.name,
            timeslot.day_names[timeslot.day],
            timeslot.period_names[timeslot.period],
            list(timeslot.activities.values())[0],
            # activity.act_type,
            list(timeslot.students.values()),
        ]
        # match timeslot.day
        print(data)
    xpoints = np.array([0,35])
    ypoints = np.array([0,4])
    plt.xticks(range(0,35,1))
    plt.plot(xpoints,ypoints)
    plt.grid('both')
    plt.show()


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
