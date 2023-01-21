from functools import cached_property
import numpy as np
import copy
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
                100,
                -5,
                -1,
                -0.5,
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

    @cached_property
    def timeslot_activity_overbookings(self):
        """Hard constraint"""
        if self.is_solved:
            return 0
        return self.verifier.aggregate(self.verifier.timeslot_activity_overbooked, self.schedule.timeslots)

    @cached_property
    def timeslot_student_overbookings(self):
        if self.is_solved:
            return 0
        """Hard constraint"""
        return self.verifier.aggregate(self.verifier.timeslot_student_overbooked, self.schedule.timeslots)

    def check_solved(self):
        # TODO check if it is solved (meets all hard constraints). Use the above hard constraint checkers.
        return False

    @cached_property
    def is_solved(self):
        # Convert True/False to int for matrix multiplication
        if self.solved_input is None:
            return self.check_solved()
        return self.solved_input

    # Soft constraints

    @cached_property
    def students_unbooked(self):
        """Hard constraint(?)
        Amount of students missing timeslots for activities."""
        if self.is_solved:
            return 0
        return self.verifier.aggregate(self.verifier.students_unbooked, self.schedule.activities)

    @cached_property
    def evening_timeslots(self):
        return self.verifier.aggregate(self.verifier.evening_bookings, self.schedule.rooms)

    @cached_property
    def student_overbookings(self):
        """Instances of students with two timeslots at the same time."""
        # if self.student_overbookings_input is None:
        return self.verifier.aggregate(self.verifier.student_overbooked, self.schedule.students)
        # return self.student_overbookings_input

    @cached_property
    def gap_periods(self):
        """Count free periods in between the first and last active period of students."""
        return self.verifier.aggregate(self.verifier.gap_periods, self.schedule.students)

    @cached_property
    def score_vector(self):
        """Return soft constraint scores."""
        if self.score_vector_input is None:
            return np.array(
                [
                    int(self.is_solved),
                    self.evening_timeslots,
                    self.student_overbookings,
                    self.gap_periods,
                ]
            )
        return self.score_vector_input

    @cached_property
    def score(self) -> float:
        return self.score_matrix.dot(self.score_vector)

    def compress(self):
        # Initialize scorevector
        self.score_vector

        # Delete all protype data except genereted edges, since entire graph can be rebuild from prototype and edges
        self.schedule.nodes = {}
        self.schedule._student_index = {}
        self.schedule._course_index = {}
        self.schedule.students = {}
        self.schedule.courses = {}
        self.schedule.activities = {}
        self.schedule.rooms = {}
        self.schedule.timeslots = {}

        self._compressed = True

    def decompress(self, target: Schedule):
        """Decompress data onto `target`. Binds target to self.schedule"""
        for edge in self.schedule.edges:
            id1, id2 = edge
            node1 = target.nodes[id1]
            node2 = target.nodes[id2]
            target.connect_nodes(node1, node2)
        self.schedule = target
        self._compressed = False

    def __str__(self):
        return str(self.__dict__)


# class CompressedResult(Result):
#     """Similar to `Result` class, but removes pointers to original schedule to save memory."""

#     def __init__(self, result: Result):
#         """Does not use reference to original schedule object so it is a candidate for garbage collection."""
#         self.schedule: Schedule = Schedule([], [], [])
#         self.schedule.edges = copy.copy(result.schedule.edges)

#         self.score_matrix = result.score_matrix
#         self.score_vector_input = result.score_vector

#         # self.verifier = Statistics()
