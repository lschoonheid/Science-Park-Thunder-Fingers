from functools import cached_property
import numpy as np
from ..algorithms.statistics import Statistics
from .schedule import Schedule
import copy


class Result(Statistics):
    """Encapsulating class for schedule and applying operations on it such as calculating score, verifying validity and compression."""

    def __init__(
        self,
        schedule: Schedule,
        solved: bool | None = None,
        iterations: int | None = None,
        score_matrix=np.array(
            [
                5,
                1,
                1,
                2,
                10,  # TODO
            ]
        ),
        score_vector=None,
    ):
        self.schedule = schedule

        # Possible to initialize with validity checked by other method
        self.solved_input = solved
        # Iterations taken for solution
        self.iterations = iterations

        # Define weights to statistics for score calculation
        self.score_matrix = score_matrix
        self.score_vector_input = score_vector

        # Remember data state
        self._compressed = False

    # Hard constraints

    def check_solved(self):
        """Check whether schedule solution is valid."""
        assert self._compressed == False, "Can only verify schedule uncompressed."
        # Verify each hard constraint
        for course in self.schedule.courses.values():
            # Check whether lectures never coincide with same course activities
            if self.moment_conflicts(course.bound_activities.values(), course.activities.values()):
                return False

            for activity in course.activities.values():
                # Check lectures have max. one timeslot
                if self.activity_overbooked(activity):
                    return False
                for student in activity.students.values():
                    # Check students have exactly 1 timeslot for all their activities
                    if self.student_timeslots_for_activity(student, activity) != 1:
                        return False

        # Check timeslots have one activity
        # Check timeslots are not over capacity (room capacity)
        # Check timeslots are not over capacity (activity capacity)
        for timeslot in self.schedule.timeslots.values():
            if len(timeslot.activities) > 1 or self.timeslot_student_overbooked(timeslot):
                return False

        # If all hard constraints were satisfied, solution is valid
        return True

    @cached_property
    def is_solved(self):
        """Return validity of schedule solution."""
        if self.solved_input is None:
            return self.check_solved()
        return self.solved_input

    # Soft constraints for calculating score

    def evening_timeslots(self):
        """Count usage of evening timeslots."""
        return self.aggregate(self.evening_bookings, self.schedule.rooms)

    def student_overbookings(self):
        """Instances of students with two timeslots at the same time."""
        return self.aggregate(self.student_overbooked, self.schedule.students)

    def gap_periods(self) -> tuple[int, int, int, int]:
        """Count free periods in between the first and last active period of students."""
        gaps = sum([self.gap_periods_student(student) for student in self.schedule.students.values()])

        return gaps  # type: ignore

    @cached_property
    def score_vector(self):
        """Return soft constraint scores in a numpy array."""
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

    def sub_score_vector(self, node):
        """Return soft constraint scores for a single node. Consider only nodes related to `node`."""
        match node.__class__.__name__:
            case "Timeslot":
                # For timeslot: check scores of students enrolled in timeslot
                # Evening period is 4
                sub_evening_timeslots = int(node.period == 4 and node.enrolled_students > 0)
                sub_students_overbooked = self.aggregate(self.student_overbooked, node.students)

                sub_gap_periods_list: list[tuple[int, int, int, int]] = [self.gap_periods_student(student) for student in node.students.values()]  # type: ignore
                # Take into account timeslots with only one student
                if len(sub_gap_periods_list) > 1:
                    sub_gap_periods = sum(sub_gap_periods_list)  # type: ignore
                elif len(sub_gap_periods_list) == 1:
                    sub_gap_periods = sub_gap_periods_list[0]
                else:
                    sub_gap_periods = (0, 0, 0, 0)
            case "Student":
                # For student: only check own score
                sub_evening_timeslots = 0
                sub_students_overbooked = self.student_overbooked(node)
                sub_gap_periods = self.gap_periods_student(node)
            case _:
                raise TypeError("Node must be Timeslot or Student.")

        # Return subscore
        return np.array(
            [
                sub_evening_timeslots,
                sub_students_overbooked,
                sub_gap_periods[1],
                sub_gap_periods[2],
                sub_gap_periods[3],
            ]
        )

    def sub_score(self, node):
        """Calculate subscore for `node`."""
        return self.score_matrix.dot(self.sub_score_vector(node))

    @cached_property
    def score(self) -> float:
        """Calculate score of `self.schedule`."""
        return self.score_matrix.dot(self.score_vector)

    def update_score(self):
        """Forget score. Forces recalculation upon next retrieval of `self.score`."""
        assert not self._compressed, "Cannot recalculate values in compressed state."
        if "is_solved" in self.__dict__.keys():
            del self.__dict__["is_solved"]
        if "score_vector" in self.__dict__.keys():
            del self.__dict__["score_vector"]
        if "score" in self.__dict__.keys():
            del self.__dict__["score"]

    def compress(self):
        """Compress `self.schedule`. Keep only solver generated information, throw away data that can be build from prototype."""
        if self._compressed:
            return self

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
        return self

    def decompress(
        self,
        students_input: list[dict],
        courses_input: list[dict],
        rooms_input: list[dict],
        edges_input: set[tuple[int, int]] | None = None,
    ):
        """Decompress `self.schedule`. Rebuilds schedule using input data and edges generated by solver."""
        if not self._compressed:
            return self

        # If given, build schedule from input edge data
        if edges_input is None:
            edges_input = self.schedule.edges

        # Initialize schedule with required data
        self.schedule.__init__(students_input, courses_input, rooms_input, edges_input)
        self._compressed = False
        return self

    def __str__(self):
        return str(self.__dict__)

    def deepcopy(
        self,
        students_input: list[dict],
        courses_input: list[dict],
        rooms_input: list[dict],
    ):
        """Faster deepcopying method than `copy.deepcopy()`."""
        return Result(
            Schedule(students_input, courses_input, rooms_input, copy.deepcopy(self.schedule.edges)),
            self.solved_input,
            self.iterations,
            self.score_matrix,
            self.score_vector_input,
        )
