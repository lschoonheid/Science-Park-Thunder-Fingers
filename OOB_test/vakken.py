class Course(object):
    """Object to store course information.

    #TODO #2
    Args:
        object (_type_): _description_
    """

    def __init__(
        self,
        subject: str,
        num_lec: int,
        num_tut: int,
        max_stud_tut: int,
        num_prac: int,
        max_stud_prac: int,
        expected_stud: int,
    ) -> None:

        # Subject name
        self.subject = subject

        # Lectures
        self.num_lec = num_lec

        # Werkcolleges & Max studenten per werkcollege
        self.num_tut = num_tut
        self.max_stud_tut = max_stud_tut

        # Practica & Max studenten per practicum
        self.num_prac = num_prac
        self.max_stud_prac = max_stud_prac

        # Expected students per subject
        self.expected_stud = expected_stud
