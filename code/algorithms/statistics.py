from ..classes.schedule import Schedule
from ..classes.node import NodeSC
from ..classes.student import Student
from ..classes.timeslot import Timeslot
from ..classes.activity import Activity
from typing import Callable


# TODO: #15 Implement objective function which couples a score to a schedule
# TODO: #27 see if some functions can be cached
class Statistics:
    # TODO: #26 complete list below
    """
    Check for:
     - overbooked timeslots (over room capacity)
     - overbooked timeslots (over tutorial/practical capacity)
     - double booked timeslots
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

    class ScoreVector:
        def __init__(
            self, student_overbookings, timeslot_overbookings, iterations: int | None, solved: bool | None = None
        ):
            self.student_overbookings = student_overbookings
            self.timeslot_overbookings = timeslot_overbookings
            self.iterations = iterations
            self.solved = solved

        def is_solved(self):
            if type(self.solved) is bool:
                return self.solved
            # TODO
            return None

        def norm(self) -> float:
            # TODO
            return 0

        def score(self) -> float:
            # TODO
            # Something like weightsmatrix * scorevector
            return 0

    def statistics(self, schedule: Schedule, iterations: int, solved: bool | None = None) -> ScoreVector:
        """Wrapper function to retrieve statistics as `ScoreVector` object."""
        score_vector = self.ScoreVector(
            student_overbookings=self.aggregate(self.student_overbooked, schedule.students),
            timeslot_overbookings=self.aggregate(self.timeslot_overbooked, schedule.timeslots),
            iterations=iterations,
            solved=solved,
        )
        return score_vector

    # def score(self, schedule: Schedule):
    #     """Shortcut to get score from `ScoreVector`."""
    #     score_vector = self.statistics(schedule)
    #     return score_vector.score()
