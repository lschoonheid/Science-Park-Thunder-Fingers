from csv import DictReader


def csv_to_dicts(input_file: str):
    with open(input_file, "r") as file:
        return [row for row in DictReader(file)]


class Data:
    """Wrapper object for data."""

    def __init__(self, stud_prefs_path: str, courses_path: str, rooms_path: str):
        self.students, self.courses, self.rooms = self.load(stud_prefs_path, courses_path, rooms_path)

    def load(self, stud_prefs_path: str, courses_path: str, rooms_path: str):
        students = csv_to_dicts(stud_prefs_path)
        courses = csv_to_dicts(courses_path)
        rooms = csv_to_dicts(rooms_path)
        return students, courses, rooms
