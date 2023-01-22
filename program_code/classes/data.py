import pickle
import hashlib
from typing import Callable
from functools import wraps
from csv import DictReader


def dump_pickle(data, output: str):
    """Dump pickle file."""
    with open(output, "wb") as handle:
        pickle.dump(data, handle)
    return data


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
        return [row for row in DictReader(file)]


class Data:
    """Wrapper object for data."""

    def __init__(self, stud_prefs_path: str, courses_path: str, rooms_path: str):
        self.students, self.courses, self.rooms = self.load(stud_prefs_path, courses_path, rooms_path)

    def load(self, stud_prefs_path: str, courses_path: str, rooms_path: str, replace_blank=True):
        students = csv_to_dicts(stud_prefs_path)
        courses = csv_to_dicts(courses_path)

        # Replace blank datavalues with valid values
        for course in courses:
            if replace_blank:
                for tag in list(course.keys())[1:]:
                    if course[tag] is "":
                        course[tag] = None
                    else:
                        course[tag] = int(course[tag])

        rooms = csv_to_dicts(rooms_path)
        return students, courses, rooms
