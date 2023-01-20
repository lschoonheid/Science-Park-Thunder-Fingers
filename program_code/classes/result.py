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
        score_matrix=np.array([100, -1, -30, -1, -5]),
        score_vector_input=None,
    ):
        self.schedule = schedule
        self.solved_input = solved
        self.iterations = iterations

        self.score_matrix = score_matrix
        self.score_vector_input = score_vector_input

        self.verifier = Statistics()

    @cached_property
    def is_solved(self):
        # Convert True/False to int for matrix multiplication
        if self.solved_input is None:
            # TODO check if it is solved (meets all hard constraints)
            return False
        return self.solved_input

    @cached_property
    def student_overbookings(self):
        """1 malus point"""
        # if self.student_overbookings_input is None:
        return self.verifier.aggregate(self.verifier.student_overbooked, self.schedule.students)
        # return self.student_overbookings_input

    @cached_property
    def students_unbooked(self):
        """Hard constraint.
        Amount of students missing timeslots for activities."""
        if self.is_solved:
            return 0
        return self.verifier.aggregate(self.verifier.students_unbooked, self.schedule.activities)

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

    @cached_property
    def score_vector(self):
        if self.score_vector_input is None:
            return np.array(
                [
                    int(self.is_solved),
                    self.student_overbookings,
                    self.timeslot_activity_overbookings,
                    self.timeslot_student_overbookings,
                    self.students_unbooked,
                ]
            )
        return self.score_vector_input

    @cached_property
    def score(self) -> float:
        return self.score_matrix.dot(self.score_vector)

    def decompress(self, target: Schedule):
        v = vars(self)
        target = self.schedule
        return self

    def __str__(self):
        return str(self.__dict__)


class CompressedResult(Result):
    """Similar to `Result` class, but removes pointers to original schedule to save memory."""

    def __init__(self, result: Result, score_matrix=np.array([100, -1, -30, -1, -5])):
        """Does not use reference to original schedule object so it is a candidate for garbage collection."""
        self.schedule: Schedule = Schedule([], [], [])
        self.schedule.edges = copy.copy(result.schedule.edges)
        self.score_matrix = score_matrix

        self.score_vector_input = result.score_vector

        self.verifier = Statistics()

    def decompress(self, target: Schedule):
        """Decompress data onto `target`. Alters target."""
        for edge in self.schedule.edges:
            id1, id2 = edge
            node1 = target.nodes[id1]
            node2 = target.nodes[id2]
            target.connect_nodes(node1, node2)
        return Result(target, score_vector_input=self.score_vector)
