from typing import Type


class Course(object):
    """Object to store course information.

    #TODO #2
    Args:
        object (_type_): _description_
    """

    def __init__(
        self,
        uid: int,
        subject: str,
        num_lec: int,
        num_tut: int,
        max_stud_tut: int | None,
        num_prac: int,
        max_stud_prac: int | None,
        expected_stud: int,
    ) -> None:
        # Course node id
        self.id = uid

        # Subject name
        self.subject = subject

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

    def __repr__(self) -> str:
        """Output name to string"""
        return self.subject
