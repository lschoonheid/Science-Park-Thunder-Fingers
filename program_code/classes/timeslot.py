from .node import Node
from .room import Room


class Timeslot(Node):
    """Node that represents a timeslot. Eg: `Room A1, period 9-11 on friday`'.

    Is linked with:
    - one room
    - students
    - activities
    """

    def __init__(self, uid: int, day: int, period: int) -> None:
        self.id = uid

        # Metadata
        self.day = day
        self.period = period

        # Neighbors
        self.room: Room
        self.students = {}
        self.activities = {}

        self.period_names = [i for i in range(9, 19, 2)]
        self.day_names = ["ma", "di", "wo", "do", "vr"]

    def __repr__(self) -> str:
        return f"Room {self.room} hour {self.period_names[self.period]} on {self.day_names[self.day]}"

    def __str__(self) -> str:
        return f"Room {self.room} hour {self.period_names[self.period]} on {self.day_names[self.day]}"
