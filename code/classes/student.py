from .course import Course


class Student(object):
    """Object to store student information and course enrolment.


    #TODO #5
    Args:
        object (_type_): _description_
    """

    def __init__(
        self,
        uid: int,
        surname: str,
        name: str,
        std_id: int,
    ) -> None:
        self.id = uid
        self.node_type = "Student"
        self.name = name
        self.surname = surname
        self.std_id = std_id
        self.courses = {}

    def add_neighbor(self, node: Course):
        assert type(node) is Course, "Can only add courses to student neighbors"
        self.courses[node.id] = node

    def __repr__(self) -> str:
        """Output representation of information."""
        # return f"{self.surname}, {self.name} ({self.std_id}): {self.courses}"
        return f"{self.surname}, {self.name}"

    def __str__(self) -> str:
        """Output information to string."""
        return f"{self.surname}, {self.name} ({self.std_id}): {self.courses}"
