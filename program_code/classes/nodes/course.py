from .node import Node

class Course(Node):
    """Node that represents a course.

    Is linked with:
    - activities
    - students
    """

    def __init__(
        self,
        uid: int,
        name: str,
        num_lec: int,
        num_tut: int,
        max_stud_tut: int | None,
        num_prac: int,
        max_stud_prac: int | None,
        expected_stud: int,
    ) -> None:
        self.id = uid

        # Metadata
        self.name = name
        self.num_lec = num_lec  # lectures
        self.num_tut = num_tut  # tutorials
        self.max_stud_tut = max_stud_tut
        self.num_prac = num_prac  # practicals
        self.max_stud_prac = max_stud_prac
        self.expected_stud = expected_stud

        # Neighbors
        self.activities = {}
        self.students = {}
        self.timeslots = {}

    def __repr__(self) -> str:
        """Output name to string"""
        return self.name

    def __str__(self) -> str:
        """Output name to string"""
        return self.name
