from .room import Room


class Timeslot:
    """Node that represents a timeslot. Eg: `Room A1, period 9-11 on friday`'.

    Is linked with:
    - one room
    - students
    - activities
    """

    def __init__(self, uid: int, day: int, period: int) -> None:
        self.id = uid
        self.node_type = "Timeslot"
        self.day = day
        self.period = period

        self.room: Room
        self.students = {}
        self.activities = {}

        self.period_names = [i for i in range(9, 19, 2)]
        self.day_names = ["ma", "di", "wo", "do", "vr"]

    def add_neighbor(self, node):
        if node.node_type == "Room":
            self.room = node
        elif node.node_type == "Student":
            self.students[node.id] = node
        elif node.node_type == "Activity":
            self.activities[node.id] = node
        else:
            print("Error in adding neighbor!")

    def __repr__(self) -> str:
        return f"Room {self.room} hour {self.period_names[self.period]} on {self.day_names[self.day]}"
