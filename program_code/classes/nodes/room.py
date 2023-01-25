from .node import Node


class Room(Node):
    """Node that represents a room.

    Is linked with:
    - timeslots
    """

    def __init__(self, uid: int, name: str, capacity: int) -> None:
        self.id = uid

        # Metadata
        self.name = name
        self.capacity = capacity

        # Neighbors
        self.timeslots = {}

    def __repr__(self) -> str:
        return f"{self.name}"

    def __str__(self) -> str:
        return f"{self.name}"
