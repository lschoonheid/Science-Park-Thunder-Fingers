from ..classes.schedule import Schedule
from ..classes.node import Node, NodeSC
from ..classes.student import Student
from ..classes.timeslot import Timeslot
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

    def __init__(self, schedule: Schedule) -> None:
        self.statistics: dict = {}
        self.score: float = 0
        self.schedule = schedule

    def student_overbooked(self, student: Student, quiet=False):
        """Test for students with overbooked booked periods."""
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

    def timeslot_overbooked(self, timeslot: Timeslot, quiet=False):
        """Test for timeslots with multiple activities linked"""
        overbookings = len(timeslot.activities) - 1
        if overbookings > 0:
            bookings = [str(timeslot) for timeslot in timeslot.activities.values()]

            if not quiet:
                print(f"HARD CONSTRAINT: Overbooked timeslot: {timeslot} has {bookings}")
        return overbookings

    def count_all(self, nodes_dict: dict[int, NodeSC], count_function: Callable[[NodeSC], int]):
        count = 0
        for node in nodes_dict.values():
            count += count_function(node)

    def get_score(self):
        student_overbookings = self.count_all(self.schedule.students, self.student_overbooked)
        timeslot_overbookings = self.count_all(self.schedule.timeslots, self.timeslot_overbooked)

        self.statistics["student_double_bookings"] = student_overbookings
        self.statistics["timeslot_overbookings"] = timeslot_overbookings
        return self.score
