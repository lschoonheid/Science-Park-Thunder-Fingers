from .course import Course
from .timeslot import Timeslot
from .student import Student


class Activity:
    def __init__(self, uid: int, type: str, capacity: int | None) -> None:
        self.id = uid
        self.node_type = "Activity"
        self.type = type
        self.capacity = capacity
        self.course: Course
        self.timeslots: dict[int, Timeslot] = {}
        self.students: dict[int, Student] = {}

    def add_neighbor(self, node):
        # if type(node) is Timeslot:
        if node.node_type == "Course":
            self.course = node
        elif node.node_type == "Timeslot":
            self.timeslots[node.id] = node
        elif node.node_type == "Student":
            self.students[node.id] = node
        else:
            print("Error in adding neighbor!")

    def __repr__(self) -> str:
        return f"{self.type} of {self.course}"

    # assert type(node) is Timeslot, "Can only add timeslot to activity as neighbor"
