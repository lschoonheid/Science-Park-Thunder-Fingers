class Node:
    """Base class of node."""

    def __init__(self, uid: int):
        self.id = uid

        # Neighbors
        self.students = {}
        self.courses = {}
        self.activities = {}
        self.timeslots = {}

    def add_neighbor(self, node):
        match type(node).__name__:
            case "Course":
                self.courses[node.id] = node
            case "Activity":
                self.activities[node.id] = node
            case "Student":
                self.students[node.id] = node
            case "Timeslot":
                self.timeslots[node.id] = node
            case "Room":
                self.room = node
            case _:
                print(f"Error: in adding node of type {type(node).__name__}: {node} to {self}")

    def __str__(self) -> str:
        return f"Node {self.id} at {hex(id(self))}"
