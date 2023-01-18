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

    def __init__(self, uid: int, act_type: str, capacity: int | None) -> None:
        self.id = uid

        # Metadata
        self.act_type = act_type
        self.capacity = capacity

        # Neighbors
        self.courses: dict[int, Course] = {}
        self.timeslots: dict[int, Timeslot] = {}
        self.students: dict[int, Student] = {}

    def __str__(self) -> str:
        return f"{self.act_type} of {str(*(self.courses.values()))}"
