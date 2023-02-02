"""
Individueel onderdeel
Interface for executing timetable program.

Execute: `python3 timetable.py`.
In main you can choose what type of timetable for the function
plot_timetable() with options: student, course or room

Student: Julia Geisler
Course: Algoritmen en Heuristieken 2023
"""

import csv, argparse, random, warnings
import matplotlib.pyplot as plt
from ..helpers import InputData, prepare_path
from ..algorithms import generate_solutions, Randomizer, Schedule

WEEK_DAYS = ["MA", "DI", "WO", "DO", "VR"]
ROOMS = ["A1.04", "A1.06", "A1.08", "A1.10", "B0.201", "C0.110", "C1.112"]
COLORS = ["pink", "lightgreen", "lightblue", "wheat", "salmon"]


def csv_timetable(schedule: Schedule, spec: str | None = None):
    """Interface for executing timetable program based on specificity."""
    match spec:
        case "-s":
            stud_sched_csv(schedule)
        case "-c":
            course_sched_csv(schedule)
        case "-r":
            room_sched_csv(schedule)
        # run all if no specificity is given
        case None:
            stud_sched_csv(schedule)
            course_sched_csv(schedule)
            room_sched_csv(schedule)


def stud_sched_csv(schedule: Schedule):
    """ "Exports timetable for random student in csv format"""
    # generate student information from random student in schedule
    student = random.choice(schedule.students)
    timeslots = sorted(list(student.timeslots.values()), key=lambda x: x.moment)

    # output path + file name
    output_path = f"output/{student.name}_schedule_output.csv"

    # header
    field_names = ["dag", "tijdslot", "vak", "activiteit", "zaal"]
    prepare_path(output_path)
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
                    activity.course.name,
                    activity.act_type,
                    timeslot.room.name,
                ]
                writer.writerow(data)

        print(f"output saved to {output_path}")
        return student


def course_sched_csv(schedule: Schedule):
    """ "Exports timetable for random course in csv format"""
    # generate course information from random course in schedule
    course = random.choice(list(schedule.courses.values()))
    for activity in course.activities.values():
        for timeslot in activity.timeslots.values():
            schedule.connect_nodes(course, timeslot)
    timeslots = sorted(list(course.timeslots.values()), key=lambda x: x.moment)

    # output path + file name
    output_path = f"output/{course.name}_schedule_output.csv"

    # header
    field_names = ["dag", "tijdslot", "activiteit", "zaal", "studenten"]

    prepare_path(output_path)
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
    return course


def room_sched_csv(schedule: Schedule):
    """ "Exports timetable for random room in csv format"""
    # generate course information from random course in schedule
    room = random.choice(list(schedule.rooms.values()))
    timeslots = sorted(list(room.timeslots.values()), key=lambda x: x.moment)
    # output path + file name
    output_path = f"output/room_schedule_output.csv"

    # header
    field_names = ["zaal", "dag", "tijdslot", "vak", "activiteit", "studenten"]

    prepare_path(output_path)
    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for timeslot in timeslots:
            activity = list(timeslot.activities.values())[0]
            data = [
                room.name,
                timeslot.day_names[timeslot.day],
                timeslot.period_names[timeslot.period],
                activity.course,
                activity.act_type,
                list(timeslot.students.values()),
            ]
            writer.writerow(data)

        print(f"output saved to {output_path}")
    return room


def plot_timetable(schedule: Schedule, spec):
    """ "Exports timetable in png format"""
    timeslots = []
    # type of plot
    if spec == "student":
        student = stud_sched_csv(schedule)
        timeslots = sorted(list(student.timeslots.values()), key=lambda x: x.moment)
        spec = student
    elif spec == "course":
        course = course_sched_csv(schedule.courses)  # type: ignore
        for activity in course.activities.values():
            for timeslot in activity.timeslots.values():
                schedule.connect_nodes(course, timeslot)
        timeslots = sorted(list(course.timeslots.values()), key=lambda x: x.moment)
        spec = course
    elif spec == "room":
        room = room_sched_csv(schedule)
        timeslots = sorted(list(room.timeslots.values()), key=lambda x: x.moment)
        spec = room
    else:
        raise NotImplementedError

    output_path = f"output/{spec}_timetable.png"

    fig = plt.figure(figsize=(10, 5.89))
    for timeslot in timeslots:
        activity = list(timeslot.activities.values())[0]
        room = timeslot.room.name
        event = activity.course.name + "\n" + activity.act_type
        day = timeslot.day - 0.48
        period = timeslot.period_names[timeslot.period]
        end = period + 2
        plt.fill_between([day, day + 0.96], period, end, color=COLORS[int(round(day))], edgecolor="k", linewidth=0.5)
        plt.text(day + 0.02, period + 0.05, room, va="top", fontsize=7)
        plt.text(day + 0.48, (period + end) * 0.5, event, ha="center", va="center", fontsize=8)

    # Set Axis
    ax = plt.subplot()
    ax.yaxis.grid()
    ax.set_xlim(-0.5, len(WEEK_DAYS) - 0.5)
    ax.set_ylim(19.1, 8.9)
    ax.set_xticks(range(0, len(WEEK_DAYS)))
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.set_xticklabels(WEEK_DAYS)
    ax.set_yticks(range(9, 21, 2))
    ax.set_ylabel("Time")

    plt.title(str(spec), y=1.07)
    print(f"Timetable plot saved to {output_path}")
    plt.savefig(output_path, dpi=200)
