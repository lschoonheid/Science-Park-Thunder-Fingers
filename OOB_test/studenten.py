# Object to store studenten

class Student(object):

    def __init__(self, surname: str, firstname: str, std_id: int, courses: list[str]) -> None:
        self.surname = surname
        self.firstname = firstname
        self.std_id = std_id
        self.courses = courses
    
    def __repr__(self) -> str:
        return f'{self.surname}, {self.firstname} ({self.std_id}): {self.courses}'

    def __str__(self) -> str:
        return f'{self.surname}, {self.firstname} ({self.std_id}): {self.courses}'