from ..classes.schedule import Schedule
from ..classes.node import NodeSC
from ..classes.student import Student
from ..classes.timeslot import Timeslot
from ..classes.activity import Activity
from functools import cached_property
from typing import Callable
import numpy as np


# TODO
# temporar


# TODO: #15 Implement objective function which couples a score to a schedule
# TODO: #27 see if some functions can be cached
class Statistics:
    # TODO: #26 complete list below
    """
    Check for:
     - overbooked timeslots (over room capacity)
     - overbooked timeslots (over tutorial/practical capacity)
     - double booked timeslots
     - students missing timeslots for activities
     - students with double booked hours
     - lectures only happen once
     - free periods for student (max three is hard constraint)
     - malus points for using evening timeslot
     - student should only follow each class once (eg: one wc1 and one wc2 in student schedule)

     Optional:
     - least amount of unique classes (wc1 only given once etc.)
    """

    # def __init__(self) -> None:
    #     self.statistics: dict = {}
    #     self.score: float = 0

    def timeslot_has_activity(self, timeslot: Timeslot):
        if len(timeslot.activities) > 0:
            return True
        return False

    def student_has_period(self, student: Student, timeslot: Timeslot):
        new_moment = (timeslot.day, timeslot.period)
        for booked_timeslot in student.timeslots.values():
            booked_moment = (booked_timeslot.day, booked_timeslot.period)
            if booked_moment == new_moment:
                return False
        return True

    def student_has_activity_assigned(self, student: Student, activity: Activity):
        """See whether `student` already has a `timeslot` for `activity`."""
        for assigned_slot in student.timeslots.values():
            for activity_timeslot in activity.timeslots.values():
                if assigned_slot.id == activity_timeslot.id:
                    # Student already has assigned timeslot for activity
                    return True
        return False

    def students_unbooked(self, activity: Activity):
        """Count how many enrolled students of `activity` don't have a timeslot for it assigned."""
        unbooked_students = 0
        for student in activity.students.values():
            unbooked_students += int(not self.student_has_activity_assigned(student, activity))
        return unbooked_students

    def student_overbooked(self, student: Student, quiet=True):
        """Count overbooked periods for `student`."""
        bookings = set()
        double_bookings: int = 0
        for timeslot in student.timeslots.values():
            moment = (timeslot.day, timeslot.period)
            if moment in bookings:
                double_bookings += 1

                if not quiet:
                    print(f"MALUS: overbooked period for {student.name}: {moment} >1 times")
            else:
                bookings.add(moment)
        return double_bookings

    def timeslot_overbooked(self, timeslot: Timeslot, quiet=True):
        """Count overbooked `activity` for `timeslot`."""
        overbookings = len(timeslot.activities) - 1
        if overbookings > 0:
            bookings = [str(activity) for activity in timeslot.activities.values()]

            if not quiet:
                print(f"HARD CONSTRAINT: Overbooked timeslot: {timeslot.id} {timeslot} has {bookings}")
        return overbookings

    def aggregate(self, count_function: Callable[[NodeSC], int], nodes_dict: dict[int, NodeSC]):
        """Return sum of `count_function` for all `Node` in `nodes_dict`."""
        count = 0
        for node in nodes_dict.values():
            count += count_function(node)
        return count

    class Result:
        def __init__(
            self,
            schedule: Schedule,
            solved: bool | None = None,
            iterations: int | None = None,
            student_overbookings: int | None = None,
            timeslot_overbookings: int | None = None,
        ):
            self.schedule = schedule
            self.iterations = iterations

            # Convert True/False to int for matrix multiplication
            if type(solved) is None:
                self.solved = 0
            elif type(solved) is bool:
                self.solved = int(solved)
            else:
                raise ValueError("`solved` needs to be of type int | bool")

            self.student_overbookings_input = student_overbookings
            self.timeslot_overbookings_input = timeslot_overbookings

            self.verifier = Statistics()
            # Roostering wil bekijken of roosters rekening kunnen houden met individuele vakinschrijvingen. Ieder vakconflict van een student levert één maluspunt op.
            self.score_matrix = np.array([100, -1, -30, -5])

        @cached_property
        def is_solved(self):
            if type(self.solved) is bool:
                return self.solved
            return None

        @cached_property
        def student_overbookings(self):
            """1 malus point"""
            if self.student_overbookings_input is None:
                return self.verifier.aggregate(self.verifier.student_overbooked, self.schedule.students)
            else:
                return self.student_overbookings_input

        @cached_property
        def students_unbooked(self):
            """Amount of students missing timeslots for activities."""
            return self.verifier.aggregate(self.verifier.students_unbooked, self.schedule.activities)

        @cached_property
        def timeslot_overbookings(self):
            """Hard constraint"""
            if self.timeslot_overbookings_input is None:
                return self.verifier.aggregate(self.verifier.timeslot_overbooked, self.schedule.timeslots)
            else:
                return self.timeslot_overbookings_input

        @cached_property
        def score_vector(self):
            return np.array(
                [self.solved, self.student_overbookings, self.timeslot_overbookings, self.students_unbooked]
            )

        @cached_property
        def score(self) -> float:
            return self.score_matrix.dot(self.score_vector)

    def get_statistics(self, schedule: Schedule, iterations: int | None = None, solved: bool | None = None):
        """Wrapper function to retrieve statistics as `Result` object."""
        score_vector = self.Result(
            schedule,
            iterations=iterations,
            solved=solved,
        )
        return score_vector

    # def score(self, schedule: Schedule):
    #     """Shortcut to get score from `ScoreVector`."""
    #     score_vector = self.statistics(schedule)
    #     return score_vector.score()
