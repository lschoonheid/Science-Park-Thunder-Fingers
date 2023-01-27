from functools import cached_property
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
        self.moment = (day, period)

        # Neighbors
        self.neighbors = {}
        self.room: Room
        self.students = {}
        self.activities = {}
        self.courses = {}

        self.period_names = [i for i in range(9, 19, 2)]
        self.day_names = ["ma", "di", "wo", "do", "vr"]

    # Mutable, do not cache
    @property
    def enrolled_students(self):
        return len(self.students)

    def calculate_capacity(self):
        min_capacity = self.room.capacity
        if len(self.activities):
            for activity in self.activities.values():
                if activity.capacity and activity.capacity < min_capacity:
                    min_capacity = activity.capacity
        return min_capacity

    @cached_property
    def capacity(self) -> int:
        return self.calculate_capacity()

    def add_neighbor(self, node):
        if type(node).__name__ == "Activity" and "capacity" in self.__dict__.keys():
            del self.__dict__["capacity"]
        return super().add_neighbor(node)

    def remove_neighbor(self, node):
        if "capacity" in self.__dict__.keys() and node.__class__.__name__ == "Activity":
            del self.__dict__["capacity"]

        return super().remove_neighbor(node)

    def __repr__(self) -> str:
        return f"Room {self.room} hour {self.period_names[self.period]} on {self.day_names[self.day]}"

    def __str__(self) -> str:
        return f"Room {self.room} hour {self.period_names[self.period]} on {self.day_names[self.day]}"
