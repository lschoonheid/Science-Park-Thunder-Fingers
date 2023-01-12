class Student(object):
    """Object to store student information and course enrolment.


    # TODO #5
    Args:
        object (_type_): _description_
    """

    def __init__(self, surname: str, first_name: str, std_id: int, courses: list[str]) -> None:
        self.surname = surname
        self.first_name = first_name
        self.std_id = std_id
        self.courses = courses

    def __repr__(self) -> str:
        """Output representation of information."""
        return f"{self.surname}, {self.first_name} ({self.std_id}): {self.courses}"

    def __str__(self) -> str:
        """Output information to string."""
        return f"{self.surname}, {self.first_name} ({self.std_id}): {self.courses}"
