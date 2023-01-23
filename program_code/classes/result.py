from functools import cached_property
import numpy as np
from ..algorithms.statistics import Statistics
from .schedule import Schedule


class Result:
    def __init__(
        self,
        schedule: Schedule,
        solved: bool | None = None,
        iterations: int | None = None,
        score_matrix=np.array(
            [
                -5,
                -1,
                -1,
                -2,
                -10,  # TODO
            ]
        ),
        score_vector=None,
    ):
        self.schedule = schedule
        self.solved_input = solved
        self.iterations = iterations

        self.score_matrix = score_matrix
        self.score_vector_input = score_vector

        self.verifier = Statistics()

        self._compressed = False

    # Hard constraints

    def check_solved(self):
        assert self._compressed == False, "Can only verify schedule uncompressed."
        # TODO check if it is solved (meets all hard constraints). Use the above hard constraint checkers.
        # Check lectures have one timeslot
        # Check students have exactly 1 timeslot for all their activities
        for activity in self.schedule.activities.values():
            if self.verifier.activity_overbooked(activity):
                return False
            for student in activity.students.values():
                if self.verifier.student_timeslots_for_activity(student, activity) != 1:
                    return False

        # Check timeslots have one activity
        # Check timeslots are not over capacity (room capacity)
        # Check timeslots are not over capacity (activity capacity)
        for timeslot in self.schedule.timeslots.values():
            if self.verifier.timeslot_activity_overbooked(timeslot) or self.verifier.timeslot_student_overbooked(
                timeslot
            ):
                return False

        return True

    @cached_property
    def is_solved(self):
        # Convert True/False to int for matrix multiplication
        if self.solved_input is None:
            return self.check_solved()
        return self.solved_input

    # Soft constraints

    # @cached_property
    def evening_timeslots(self):
        return self.verifier.aggregate(self.verifier.evening_bookings, self.schedule.rooms)

    # @cached_property
    def student_overbookings(self):
        """Instances of students with two timeslots at the same time."""
        # if self.student_overbookings_input is None:
        return self.verifier.aggregate(self.verifier.student_overbooked, self.schedule.students)
        # return self.student_overbookings_input

    # TODO: #39 don't allow 3 gaps
    # @cached_property
    def gap_periods(self) -> tuple[int, int, int, int]:
        """Count free periods in between the first and last active period of students."""
        gaps = sum([self.verifier.gap_periods(student) for student in self.schedule.students.values()])

        return gaps  # type: ignore

    # @cached_property
    def score_vector(self):
        """Return soft constraint scores."""
        if self.score_vector_input is None:
            gap_periods = self.gap_periods()
            return np.array(
                [
                    self.evening_timeslots(),
                    self.student_overbookings(),
                    gap_periods[1],
                    gap_periods[2],
                    gap_periods[3],
                ]
            )
        return self.score_vector_input

    @cached_property
    def score(self) -> float:
        return self.score_matrix.dot(self.score_vector())

    def compress(self):
        # Initialize scorevector
        self.score_vector

        # Delete all protype data except genereted edges, since entire graph can be rebuild from prototype and edges
        del self.schedule.nodes
        del self.schedule._student_index
        del self.schedule._course_index
        del self.schedule.students
        del self.schedule.courses
        del self.schedule.activities
        del self.schedule.rooms
        del self.schedule.timeslots

        self._compressed = True

    def decompress(
        self,
        students_input: list[dict],
        courses_input: list[dict],
        rooms_input: list[dict],
        edges_input: set[tuple[int, int]] | None = None,
    ):
        """Decompress data onto `target`. Binds target to self.schedule"""
        if edges_input is None:
            edges_input = self.schedule.edges
        self.schedule.__init__(students_input, courses_input, rooms_input, edges_input)
        self._compressed = False

    def __str__(self):
        return str(self.__dict__)
