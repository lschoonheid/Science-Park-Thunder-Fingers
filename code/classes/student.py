from .node import Node


class Student(Node):
    """Node that represents a student..

    Is linked with:
    - courses
    - activities
    - timeslots
    """

    def __init__(
        self,
        uid: int,
        surname: str,
        name: str,
        std_id: int,
    ) -> None:
        self.id = uid

        # Metadata
        self.name = name
        self.surname = surname
        self.std_id = std_id

        # Neighbors
        self.courses = {}
        self.activities = {}
        self.timeslots = {}

    def __repr__(self) -> str:
        """Output representation of information."""
        # return f"{self.surname}, {self.name} ({self.std_id}): {self.courses}"
        return f"{self.name}"

    def __str__(self) -> str:
        """Output name to string."""
        return f"{self.name} {self.surname}"
