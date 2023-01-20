# First test program to make schedules with object oriented programming.

from .node import NodeSC
from .course import Course
from .room import Room
from .student import Student
from .activity import Activity
from .timeslot import Timeslot


class Schedule:
    """Class representation of schedule graph. Contains all nodes and edges."""

    def __init__(self, students_input: list[dict], courses_input: list[dict], rooms_input: list[dict]) -> None:
        # Contains all nodes
        # TODO: #22 make parent 'Node' class
        self.nodes: dict[int, Student | Course | Activity | Room | Timeslot] = {}
        # Contains all edges as [uid1, uid2]
        self.edges: set[tuple[int, int]] = set()

        # keeps track of uids assigned to named nodes
        self._course_catalog: dict[str, int] = {}
        self._student_catalog: dict[int, int] = {}

        # Students is a dictionary that hold all students by student number with corresponding info
        self.students: dict[int, Student] = self.load_student_nodes(students_input)
        # Courses is a dictionary that holds course name with corresponding info
        self.courses: dict[int, Course] = self.load_course_nodes(courses_input)
        self.activities: dict[int, Activity] = self.load_activity_nodes()
        # Rooms is a dictionary that hold all rooms with corresponding capacity
        self.rooms: dict[int, Room] = self.load_room_nodes(rooms_input)
        self.timeslots: dict[int, Timeslot] = self.load_timeslot_nodes()

        self.load_neighbours(students_input)

    def track_node_id(self):
        return len(self.nodes)

    def load_student_nodes(self, students_input: list[dict]):
        """
        Load all student nodes into student dictionary in __init__
        """
        node_id = self.track_node_id()
        students = {}

        for student in students_input:
            s = student
            stud_no = int(s["Stud.Nr."])

            students[node_id] = Student(node_id, s["Achternaam"], s["Voornaam"], stud_no)
            self.nodes[node_id] = students[node_id]
            self._student_catalog[stud_no] = node_id
            node_id += 1

        return students

    def load_course_nodes(self, courses_input: list[dict]):
        """
        Load all course nodes into course dictionary in __init__
        """
        node_id = self.track_node_id()
        courses = {}

        for course in courses_input:
            replace_blank = True
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

            courses[node_id] = Course(
                node_id,
                name,
                int(c["#Hoorcolleges"]),
                int(c["#Werkcolleges"]),
                c["Max. stud. Werkcollege"],  # type: ignore
                int(c["#Practica"]),
                c["Max. stud. Practicum"],  # type: ignore
                int(c["Verwacht"]),
            )
            self.nodes[node_id] = courses[node_id]
            self._course_catalog[name] = node_id
            node_id += 1

        return courses

    def load_activity_nodes(self):
        """
        Load all course nodes into course dictionary in __init__
        """
        node_id = self.track_node_id()
        activities = {}
        # Add children activities to courses and vice versa
        for course in self.courses.values():

            for i in range(course.num_lec):
                activity = {
                    "act_type": f"hc{i+1}",
                    "capacity_input": None,
                    "max_timeslots": 1,
                }
                activities[node_id] = Activity(node_id, **activity)
                self.nodes[node_id] = activities[node_id]
                self.connect_nodes(course, activities[node_id])
                node_id += 1

            for i in range(course.num_tut):
                activity = {
                    "act_type": f"wc{i+1}",
                    "capacity_input": course.max_stud_tut,
                }
                activities[node_id] = Activity(node_id, **activity)
                self.nodes[node_id] = activities[node_id]
                self.connect_nodes(course, activities[node_id])
                node_id += 1

            for i in range(course.num_prac):
                activity = {
                    "act_type": f"p{i+1}",
                    "capacity_input": course.max_stud_prac,
                }
                activities[node_id] = Activity(node_id, **activity)
                self.nodes[node_id] = activities[node_id]
                self.connect_nodes(course, activities[node_id])
                node_id += 1

        return activities

    def load_room_nodes(self, rooms_input: list[dict]):
        """
        Load all room nodes into room dictionary in __init__
        """
        node_id = self.track_node_id()
        rooms = {}

        for room in rooms_input:
            r = room
            rooms[node_id] = Room(node_id, r["\ufeffZaalnummber"], int(r["Max. capaciteit"]))  # type: ignore
            self.nodes[node_id] = rooms[node_id]
            node_id += 1

        return rooms

    def load_timeslot_nodes(self):
        node_id = self.track_node_id()
        timeslots = {}

        # Add timeslots
        for room in self.rooms.values():
            period_range: int = 4

            # De grootste zaal heeft ook een avondslot van 17:00-19:00
            if room.name == "C0.110":
                period_range = 5

            for day in range(5):
                for period in range(period_range):
                    timeslot = {"day": day, "period": period}
                    timeslots[node_id] = Timeslot(node_id, **timeslot)
                    self.nodes[node_id] = timeslots[node_id]
                    self.connect_nodes(room, timeslots[node_id])
                    node_id += 1

        return timeslots

    def connect_nodes(self, node1: NodeSC, node2: NodeSC):
        """Connect two nodes by adding neighbor to both nodes symmetrically.
        - returns `True` if connection was made
        - returns `False` if connection already exists."""

        # Sort so the tuple of pairing (id1, id2) is unique
        edge = (min(node1.id, node2.id), max((node1.id, node2.id)))

        # Return true if connection can be made, return false if connection already exists
        if edge in self.edges:
            return False

        node1.add_neighbor(node2)
        node2.add_neighbor(node1)
        self.edges.add(edge)
        return True

    def load_neighbours(self, students_input: list[dict]):
        """
        Load all the neighbours into the loaded nodes.
        """

        # Load neighbors from CSV
        for student_dict in students_input:
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
