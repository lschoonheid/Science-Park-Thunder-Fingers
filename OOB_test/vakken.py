# Object to store vakken, zalen en studenten apart.

class Lecture(object):

    def __init__(self, subject: str, num_hc: int, num_wc: int, max_stud_wc: int, num_prac: int, max_stud_prac: int, expected_stud: int) -> None:

        # Subject name
        self.subject = subject

        # Hoorcolleges
        self.num_hc = num_hc

        # Werkcolleges & Max studenten per werkcollege
        self.num_wc = num_wc
        self.max_stud_wc = max_stud_wc

        # Practica & Max studenten per practicum
        self.num_prac = num_prac
        self.max_stud_prac = max_stud_prac


        # Expected students per subject
        self.expected_stud = expected_stud

    

