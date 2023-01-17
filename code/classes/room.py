class Room:
    """Node that represents a room.

    Is linked with:
    - timeslots
    """

    def __init__(self, uid: int, name: str, capacity: int) -> None:
        self.id = uid
        self.node_type = "Room"
        self.name = name
        self.capacity = capacity
        self.timeslots = {}

    def add_neighbor(self, node):
        if node.node_type == "Timeslot":
            self.timeslots[node.id] = node
        else:
            print("Error in adding neighbor!")

    def __repr__(self) -> str:
        return f"{self.name}"
