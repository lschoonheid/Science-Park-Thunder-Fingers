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
        first_name: str,
        std_id: int,
    ) -> None:
        self.id = uid
        self.surname = surname
        self.first_name = first_name
        self.std_id = std_id
        self.courses = {}

    def add_course(self, course: Course):
        self.courses[course.id] = course

    def __repr__(self) -> str:
        """Output representation of information."""
        return f"{self.surname}, {self.first_name} ({self.std_id}): {self.courses}"

    def __str__(self) -> str:
        """Output information to string."""
        return f"{self.surname}, {self.first_name} ({self.std_id}): {self.courses}"
