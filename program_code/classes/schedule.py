# First test program to make schedules with object oriented programming.

from .nodes import *


class Schedule:
    """Class representation of schedule graph. Contains all nodes and edges."""

    def __init__(
        self,
        students_input: list[dict],
        courses_input: list[dict],
        rooms_input: list[dict],
        edges_input: set[tuple[int, int]] | None = None,
    ) -> None:
        self._id_count = 0

        # keeps track of uids assigned to named nodes
        self._student_index: dict[int, int] = {}
        self._course_index: dict[str, int] = {}

        # Initialize edges if this is the first initialization
        if not hasattr(self, "edges"):
            # Contains all edges as tuple[id1, id2]
            self.edges: set[tuple[int, int]] = set()

        # Students is a dictionary that hold all students by student number with corresponding info
        self.students: dict[int, Student] = self.get_student_nodes(students_input)
        # Courses is a dictionary that holds course name with corresponding info
        self.courses: dict[int, Course] = self.get_course_nodes(courses_input)
        self.activities: dict[int, Activity] = self.get_activity_nodes()
        # Rooms is a dictionary that hold all rooms with corresponding capacity
        self.rooms: dict[int, Room] = self.get_room_nodes(rooms_input)
        self.timeslots: dict[int, Timeslot] = self.get_timeslot_nodes(self.rooms.values())

        # Contains all nodes
        self.nodes = self.students | self.courses | self.activities | self.rooms | self.timeslots
        # Add new edges
        self.edges = self.edges.union(self.get_edges(edges_input, students_input))

    # def track_self._id_count(self):
    #     """Keeps track of node id's ensuring each node is assigned a unique id."""
    #     return len(self.nodes)

    def get_student_nodes(self, students_input: list[dict]):
        """
        Get all student nodes into student dictionary in __init__
        """
        students = {}

        for student in students_input:
            self._id_count = self._id_count
            s = student
            stud_no = int(s["Stud.Nr."])

            students[self._id_count] = Student(self._id_count, s["Achternaam"], s["Voornaam"], stud_no)
            # self.nodes[self._id_count] = students[self._id_count]
            self._student_index[stud_no] = self._id_count
            self._id_count += 1

        return students

    def get_course_nodes(self, courses_input: list[dict]):
        """
        Get all course nodes into course dictionary in __init__
        """
        courses = {}

        for course in courses_input:
            c = course
            # TODO: #25 There is one course that is referenced as "Zoeken, sturen en bewegen" in `vakken.csv` but as "Zoeken sturen en bewegen" in `studenten_en_vakken.csv`.
            name = c["Vak"].replace(",", "")

            courses[self._id_count] = Course(
                self._id_count,
                name,
                int(c["#Hoorcolleges"]),
                int(c["#Werkcolleges"]),
                c["Max. stud. Werkcollege"],  # type: ignore
                int(c["#Practica"]),
                c["Max. stud. Practicum"],  # type: ignore
                int(c["Verwacht"]),
            )
            # self.nodes[self._id_count] = courses[self._id_count]
            self._course_index[name] = self._id_count
            self._id_count += 1

        return courses

    def get_activity_nodes(self):
        """
        Get all course nodes into course dictionary in __init__
        """
        activities = {}
        # Add children activities to courses and vice versa
        for course in self.courses.values():

            for i in range(course.num_lec):
                activity = {
                    "act_type": f"hc{i+1}",
                    "capacity_input": None,
                    "max_timeslots": 1,
                }
                activities[self._id_count] = Activity(self._id_count, **activity)
                # self.nodes[self._id_count] = activities[self._id_count]
                self.connect_nodes(course, activities[self._id_count])
                self._id_count += 1

            for i in range(course.num_tut):
                activity = {
                    "act_type": f"wc{i+1}",
                    "capacity_input": course.max_stud_tut,
                }
                activities[self._id_count] = Activity(self._id_count, **activity)
                # self.nodes[self._id_count] = activities[self._id_count]
                self.connect_nodes(course, activities[self._id_count])
                self._id_count += 1

            for i in range(course.num_prac):
                activity = {
                    "act_type": f"p{i+1}",
                    "capacity_input": course.max_stud_prac,
                }
                activities[self._id_count] = Activity(self._id_count, **activity)
                # self.nodes[self._id_count] = activities[self._id_count]
                self.connect_nodes(course, activities[self._id_count])
                self._id_count += 1

        return activities

    def get_room_nodes(self, rooms_input: list[dict]):
        """
        Get all room nodes into room dictionary in __init__
        """
        rooms = {}

        for room in rooms_input:
            r = room
            rooms[self._id_count] = Room(self._id_count, r["\ufeffZaalnummber"], int(r["Max. capaciteit"]))  # type: ignore
            # self.nodes[self._id_count] = rooms[self._id_count]
            self._id_count += 1

        return rooms

    def get_timeslot_nodes(self, rooms):
        timeslots = {}

        # Add timeslots
        for room in rooms:
            period_range: int = 4

            # De grootste zaal heeft ook een avondslot van 17:00-19:00
            if room.name == "C0.110":
                period_range = 5

            for day in range(5):
                for period in range(period_range):
                    timeslot = {"day": day, "period": period}
                    timeslots[self._id_count] = Timeslot(self._id_count, **timeslot)
                    # self.nodes[self._id_count] = timeslots[self._id_count]
                    self.connect_nodes(room, timeslots[self._id_count])
                    self._id_count += 1

        return timeslots

    # TODO: general add_node function

    def connect_nodes(self, node1: NodeSC, node2: NodeSC, add_edge=True, check=False):
        """Connect two nodes by adding neighbor to both nodes symmetrically.
        - returns `True` if connection was made
        - returns `False` if connection already exists."""

        # Sort so the tuple of pairing (id1, id2) is unique
        edge = (min(node1.id, node2.id), max((node1.id, node2.id)))

        # Return true if connection can be made, return false if connection already exists
        if check and edge in self.edges:
            return False

        node1.add_neighbor(node2)
        node2.add_neighbor(node1)
        if add_edge:
            self.edges.add(edge)
        return edge

    def get_edges(self, edges: set[tuple[int, int]] | None = None, students_input: list[dict] | None = None):
        """
        Get all the neighbours into the geted nodes.
        """
        new_edges: set[tuple[int, int]] = set()

        # Add neighbors from input
        if edges is not None:
            for edge in edges:
                id1, id2 = edge
                node1 = self.nodes[id1]
                node2 = self.nodes[id2]
                new_edge = self.connect_nodes(node1, node2, add_edge=False)
                if new_edge:
                    new_edges.add(new_edge)

        if students_input is None:
            return new_edges

        # Get neighbors from dict
        for student_dict in students_input:
            stud_id = self._student_index[int(student_dict["Stud.Nr."])]

            # Get course choices from student
            choice_keys = list(student_dict.keys())[-5:]
            # Clean empty strings
            choices_dirty = [student_dict[choice] for choice in choice_keys]
            choices = list(filter(lambda c: c != "", choices_dirty))

            # Add courses to student
            for course_name in choices:
                course_id = self._course_index[course_name]
                course = self.courses[course_id]
                student = self.students[stud_id]
                new_edge = self.connect_nodes(student, course, add_edge=False)
                if new_edge:
                    new_edges.add(new_edge)

        # Infer neighbors from graph
        for student in self.students.values():
            for course in student.courses.values():
                for activity in course.activities.values():
                    new_edge = self.connect_nodes(student, activity, add_edge=False)
                    if new_edge:
                        new_edges.add(new_edge)

        return new_edges
