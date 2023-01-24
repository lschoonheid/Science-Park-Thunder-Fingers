from .node import Node
from .course import Course
from .timeslot import Timeslot
from .student import Student


class Activity(Node):
    """Node that represents an activity. Eg: `wc1 of analyise`'.

    Is linked with:
    - timeslots
    - students
    """

    def __init__(self, uid: int, act_type: str, capacity_input: int | None, max_timeslots: int | None = None) -> None:
        self.id = uid

        # Metadata
        self.act_type = act_type
        self.capacity_input = capacity_input
        self.max_timeslots = max_timeslots

        # Neighbors
        # self.courses: dict[int, Course] = {}
        self.timeslots: dict[int, Timeslot] = {}
        self.students: dict[int, Student] = {}

    def add_neighbor(self, node):
        if type(node).__name__ == "Course":
            self.course = node
            return
        return super().add_neighbor(node)

    @property
    def capacity(self):
        if self.capacity_input:
            return self.capacity_input
        return self.enrolled_students

    def __repr__(self) -> str:
        return f"{self.act_type} of {self.course}"

    def __str__(self) -> str:
        return f"{self.act_type} of {self.course}"
