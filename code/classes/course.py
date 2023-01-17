# from .student import Student


class Course:
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
        # Course node id
        self.id = uid
        self.node_type = "Course"

        # name name
        self.name = name

        # Lectures
        self.num_lec = num_lec

        # Tutorials & Max students per tutorial
        self.num_tut = num_tut
        self.max_stud_tut = max_stud_tut

        # Practicals & Max students per practical
        self.num_prac = num_prac
        self.max_stud_prac = max_stud_prac

        # Expected students per subject
        self.expected_stud = expected_stud

        self.activities = {}

        # self.students: dict[int, Student] = {}
        self.students = {}

    # def add_neighbor(self, node: Student):
    def add_neighbor(self, node):
        if node.node_type == "Student":
            self.students[node.id] = node
        elif node.node_type == "Activity":
            self.activities[node.id] = node
        else:
            print("Error in adding neighbor!")

    def __repr__(self) -> str:
        """Output name to string"""
        return self.name
