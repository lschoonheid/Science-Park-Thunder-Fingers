"""Functions to handle caching, saving and retrieving data."""


import os
import pickle
import hashlib
from typing import Callable
from functools import wraps
import csv
import time


def prepare_path(path: str):
    """If a directory for `path` doesn't exist, make it."""

    # Filter directory from path
    directory = "/".join(path.split("/")[:-1])
    if directory == "":
        return

    isExist = os.path.exists(directory)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(directory)


def dump_pickle(data, output: str):
    """Dump pickle file."""
    prepare_path(output)
    with open(output, "wb") as handle:
        pickle.dump(data, handle)
    return data


def dump_result(data, directory: str):
    time_string = time.strftime("%Y%m%d-%H%M%S")
    path = directory + time_string + ".pyc"
    dump_pickle(data, path)
    return path


def load_pickle(location: str):
    """Load pickle file."""
    with open(location, "rb") as handle:
        data = pickle.load(handle)
    return data


def hashargs(*args, **kwds):
    """Takes `args` and `kwds` as arguments and hashes its information to a string."""
    args_identifier = hashlib.md5(str((args, kwds)).encode()).hexdigest()
    return args_identifier


def pickle_cache(func: Callable, verbose: bool = False):
    """Decorator function for caching function output to PYC files."""

    @wraps(func)
    def wrapper(*args, **kwds):
        args_identifier = hashargs(*args, **kwds)
        output = ".cache/" + args_identifier + ".pyc"

        try:
            data = load_pickle(output)
            if verbose:
                print("Found cached data. Loading from cache instead.")
        except FileNotFoundError:
            data = dump_pickle(func(*args, **kwds), output)
        return data

    return wrapper


def csv_to_dicts(input_file: str):
    with open(input_file, "r") as file:
        return [row for row in csv.DictReader(file)]


def schedule_to_csv(schedule, output_path: str = "output/Schedule_output.csv", verbose=False):
    """Program to convert a schedule object into a csv file."""
    # columns
    field_names = ["student", "vak", "activiteit", "zaal", "dag", "tijdslot"]

    prepare_path(output_path)

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for student in schedule.students.values():
            for timeslot in student.timeslots.values():
                for activity in timeslot.activities.values():
                    data = [
                        student.name,
                        activity.course.name,
                        activity.act_type,
                        timeslot.room.name,
                        timeslot.day_names[timeslot.day],
                        timeslot.period_names[timeslot.period],
                    ]
                    writer.writerow(data)

        if verbose:
            print(f"output saved to {output_path}")


class InputData:
    """Wrapper object for input data."""

    def __init__(self, stud_prefs_path: str, courses_path: str, rooms_path: str):
        self.students_input, self.courses_input, self.rooms_input = self.load(stud_prefs_path, courses_path, rooms_path)

    def load(self, stud_prefs_path: str, courses_path: str, rooms_path: str, replace_blank=True):
        students = csv_to_dicts(stud_prefs_path)
        courses = csv_to_dicts(courses_path)

        # Replace blank datavalues with valid values
        for course in courses:
            if replace_blank:
                for tag in list(course.keys())[1:]:
                    if course[tag] == "":
                        course[tag] = None
                    else:
                        course[tag] = int(course[tag])

        rooms = csv_to_dicts(rooms_path)
        return students, courses, rooms
