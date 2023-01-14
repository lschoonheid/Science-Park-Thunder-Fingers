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

        # keeps track of uids assigned to named nodes
        self._course_catalog: dict[str, int] = {}
        self._student_catalog: dict[int, int] = {}

        self.load_nodes(stud_prefs_path, courses_path, rooms_path)
        self.load_neighbours(stud_prefs_path)

    def _add_student(self, uid: int, student: dict) -> None:
        s = student
        stud_no = int(s["Stud.Nr."])

        # values = list(student.values())[0:3])
        self.students[uid] = Student(uid, s["Achternaam"], s["Voornaam"], stud_no)
        self._student_catalog[stud_no] = uid

    def _add_course(self, uid: int, course: dict, replace_blank=True) -> None:
        c = course
        name = c["Vak"]

        # Replace blank datavalues with valid values
        if replace_blank:
            for tag in list(c.keys())[1:]:
                if c[tag] == "":
                    c[tag] = None
                else:
                    c[tag] = int(c[tag])

        self.courses[uid] = Course(
            uid,
            name,
            int(c["#Hoorcolleges"]),
            int(c["#Werkcolleges"]),
            c["Max. stud. Werkcollege"],
            int(c["#Practica"]),
            c["Max. stud. Practicum"],
            int(c["Verwacht"]),
        )
        self._course_catalog[name] = uid

    def _add_room(self, uid: int, room: dict) -> None:
        r = room
        self.rooms[uid] = Room(uid, r["\ufeffZaalnummber"], r["Max. capaciteit"])

    def load_nodes(self, stud_prefs_path: str, courses_path: str, rooms_path: str):
        """
        Load all the nodes into the graph.
        """
        node_id = 0

        for student in csv_to_dicts(stud_prefs_path):
            self._add_student(node_id, student)
            node_id += 1

        for course in csv_to_dicts(courses_path):
            self._add_course(node_id, course)
            node_id += 1

        for room in csv_to_dicts(rooms_path):
            self._add_room(node_id, room)
            node_id += 1

    def connect_nodes(self, node1, node2):
        node1.add_neighbor(node2)
        node2.add_neighbor(node1)

    def load_neighbours(self, stud_prefs_path):
        """
        Load all the neighbours into the loaded nodes.
        """
        for student_dict in csv_to_dicts(stud_prefs_path):
            stud_uid = self._student_catalog[int(student_dict["Stud.Nr."])]

            # Get course choices from student
            choice_keys = list(student_dict.keys())[-5:]
            # Clean empty strings
            choices_dirty = [student_dict[choice] for choice in choice_keys]
            choices = list(filter(lambda c: c != "", choices_dirty))

            # Add courses to student
            for course_name in choices:
                course_id = self._course_catalog[course_name]
                course = self.courses[course_id]
                student = self.students[stud_uid]
                self.connect_nodes(course, student)
