# First test program to make schedules with object oriented programming.

from .course import Course
from .room import Room
from .student import Student
from ..modules.helpers import csv_to_dicts

# Load csv files
# TODO: #8 build representation of graph
class Schedule:
    def __init__(self, stud_prefs_path: str, courses_path: str, rooms_path: str) -> None:
        # self.nodes: dict[int, (Student, Course, Room)] = {}
        # Students is a dictionary that hold all students by student number with corresponding info
        self.students: dict[int, Student] = {}
        # Courses is a dictionary that holds course name with corresponding info
        self.courses: dict[int, Course] = {}
        # Rooms is a dictionary that hold all rooms with corresponding capacity
        # TODO: #18 replace by timeslot? (the relevant node)
        self.rooms: dict[int, Room] = {}

        self.load_nodes(stud_prefs_path, courses_path, rooms_path)

    def load_nodes(self, stud_prefs_path, courses_path, rooms_path):
        node_id = 0

        for student in csv_to_dicts(stud_prefs_path):
            self.add_student(node_id, student)
            node_id += 1

        for course in csv_to_dicts(courses_path):
            self.add_course(node_id, course)
            node_id += 1

        for room in csv_to_dicts(rooms_path):
            self.add_room(node_id, room)
            node_id += 1

    def add_student(self, uid: int, student: dict) -> None:
        s = student
        self.students[uid] = Student(uid, s["Achternaam"], s["Voornaam"], int(s["Stud.Nr."]))

    def add_course(self, uid: int, course: dict, replace_blank=True) -> None:
        c = course

        # Replace blank datavalues with valid values
        non_strict_tags = ["Max. stud. Werkcollege", "Max. stud. Practicum"]
        if replace_blank:
            for tag in non_strict_tags:
                if c[tag] == "":
                    c[tag] = 0

        self.courses[uid] = Course(
            uid,
            c["Vak"],
            int(c["#Hoorcolleges"]),
            int(c["#Werkcolleges"]),
            int(c["Max. stud. Werkcollege"]),
            int(c["#Practica"]),
            int(c["Max. stud. Practicum"]),
            int(c["Verwacht"]),
        )

    def add_room(self, uid: int, room: dict) -> None:
        r = room
        self.rooms[uid] = Room(uid, r["\ufeffZaalnummber"], r["Max. capaciteit"])
