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
        self.activities = {}
        self.timeslots = {}

    def add_neighbor(self, node):
        if node.node_type == "Course":
            self.courses[node.id] = node
        elif node.node_type == "Activity":
            self.activities[node.id] = node
        elif node.node_type == "Timeslot":
            self.timeslots[node.id] = node
        else:
            print("Error in adding neighbor!")

    def __repr__(self) -> str:
        """Output representation of information."""
        # return f"{self.surname}, {self.name} ({self.std_id}): {self.courses}"
        return f"{self.surname}, {self.name}"

    def __str__(self) -> str:
        """Output information to string."""
        return f"{self.surname}, {self.name} ({self.std_id}): {self.courses}"
