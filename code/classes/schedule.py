# First test program to make schedules with object oriented programming.

from .course import Course
from .room import Room
from .student import Student
from .activity import Activity
from .timeslot import Timeslot
from ..modules.helpers import csv_to_dicts


class Schedule:
    """Class representation of schedule graph. Contains all nodes and edges."""

    def __init__(self, stud_prefs_path: str, courses_path: str, rooms_path: str) -> None:
        # self.nodes: dict[int, (Student, Course, Room)] = {}
        # Students is a dictionary that hold all students by student number with corresponding info
        self.students: dict[int, Student] = {}
        # Courses is a dictionary that holds course name with corresponding info
        self.courses: dict[int, Course] = {}
        self.activities: dict[int, Activity] = {}
        self.timeslots: dict[int, Timeslot] = {}
        # Rooms is a dictionary that hold all rooms with corresponding capacity
        self.rooms: dict[int, Room] = {}

        # Contains all nodes
        # TODO: #22 make parenmt 'Node' class
        self.nodes: dict[int, Student | Course | Activity | Room | Timeslot] = {}
        # Contains all edges as [uid1, uid2]
        self.edges: set[tuple[int, int]] = set()

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
        self.nodes[uid] = self.students[uid]
        self._student_catalog[stud_no] = uid

    def _add_course(self, uid: int, course: dict, replace_blank=True) -> None:
        c = course
        # TODO: #25 There is one course that is referenced as "Zoeken, sturen en bewegen" in `vakken.csv` but as "Zoeken sturen en bewegen" in `studenten_en_vakken.csv`.
        name = c["Vak"].replace(",", "")

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
        self.nodes[uid] = self.courses[uid]
        self._course_catalog[name] = uid

    def _add_activity(self, uid: int, activity: dict) -> None:
        self.activities[uid] = Activity(uid, **activity)
        self.nodes[uid] = self.activities[uid]

    def _add_room(self, uid: int, room: dict) -> None:
        r = room
        self.rooms[uid] = Room(uid, r["\ufeffZaalnummber"], r["Max. capaciteit"])
        self.nodes[uid] = self.rooms[uid]

    def _add_timeslot(self, uid: int, timeslot: dict) -> None:
        self.timeslots[uid] = Timeslot(uid, **timeslot)
        self.nodes[uid] = self.timeslots[uid]

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

        # Add children activities to courses and vice versa
        for course in self.courses.values():
            for i in range(course.num_lec):
                activity = {
                    "type": f"hc{i+1}",
                    "capacity": None,
                }
                self._add_activity(node_id, activity)
                self.connect_nodes(course, self.activities[node_id])
                node_id += 1
            for i in range(course.num_tut):
                activity = {
                    "type": f"wc{i+1}",
                    "capacity": course.max_stud_tut,
                }
                self._add_activity(node_id, activity)
                self.connect_nodes(course, self.activities[node_id])
                node_id += 1
            for i in range(course.num_prac):
                activity = {
                    "type": f"p{i+1}",
                    "capacity": course.max_stud_prac,
                }
                self._add_activity(node_id, activity)
                self.connect_nodes(course, self.activities[node_id])
                node_id += 1

        #  Add rooms
        for room in csv_to_dicts(rooms_path):
            self._add_room(node_id, room)
            node_id += 1

        # Add timeslots
        for room in self.rooms.values():
            period_range: int = 4
            # De grootste zaal heeft ook een avondslot van 17:00-19:00
            if room.name == "C0.110":
                period_range = 5

            for day in range(5):
                for period in range(period_range):
                    timeslot_dict = {"day": day, "period": period}
                    self._add_timeslot(node_id, timeslot_dict)
                    timeslot = self.timeslots[node_id]
                    self.connect_nodes(room, timeslot)
                    print(timeslot)
                    node_id += 1

    def connect_nodes(self, node1, node2):
        """Connect two nodes. Symmetrically adds neighbor to nodes and fails if conn"""
        node1.add_neighbor(node2)
        node2.add_neighbor(node1)

        # Sort so the tuple of pairing (id1, id2) is unique
        edge = (min(node1.id, node2.id), max((node1.id, node2.id)))

        # Return true if connection can be made, return false if connection already exists
        if edge in self.edges:
            return False
        self.edges.add(edge)
        return True

    def load_neighbours(self, stud_prefs_path):
        """
        Load all the neighbours into the loaded nodes.
        """

        # Load neighbors from CSV
        for student_dict in csv_to_dicts(stud_prefs_path):
            stud_id = self._student_catalog[int(student_dict["Stud.Nr."])]

            # Get course choices from student
            choice_keys = list(student_dict.keys())[-5:]
            # Clean empty strings
            choices_dirty = [student_dict[choice] for choice in choice_keys]
            choices = list(filter(lambda c: c != "", choices_dirty))

            # Add courses to student
            for course_name in choices:
                course_id = self._course_catalog[course_name]
                course = self.courses[course_id]
                student = self.students[stud_id]
                self.connect_nodes(course, student)

        # Infer neighbors from graph
        for student in self.students.values():
            for course in student.courses.values():
                for activity in course.activities.values():
                    self.connect_nodes(student, activity)
