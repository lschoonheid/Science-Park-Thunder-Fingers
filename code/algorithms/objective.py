from ..classes.schedule import Schedule
from ..classes.student import Student
from ..classes.timeslot import Timeslot

# TODO: #15 Implement objective function which couples a score to a schedule
class Objective:
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

    # test for students with doubly booked timeslots
    def count_student_doubles(self, student: Student):
        bookings = set()
        double_bookings: int = 0
        for timeslot in student.timeslots.values():
            moment = (timeslot.day, timeslot.period)
            if moment in bookings:
                double_bookings += 1
                print(f"MALUS: doubly booked student {student.name}: {moment} >1 times")
            else:
                bookings.add(moment)

        return double_bookings

    def count_timeslot_overbookings(self, timeslot: Timeslot):
        overbookings = len(timeslot.activities) - 1
        if overbookings > 0:
            bookings = [str(timeslot) for timeslot in timeslot.activities.values()]
            print(f"MALUS: Overbooked timeslot: {timeslot} has {bookings}")
        return overbookings

    def get_score(self):
        student_double_bookings = 0
        for student in self.schedule.students.values():
            student_double_bookings += self.count_student_doubles(student)

        timeslot_overbookings = 0
        for timeslot in self.schedule.timeslots.values():
            timeslot_overbookings += self.count_timeslot_overbookings(timeslot)

        self.statistics["student_double_bookings"] = student_double_bookings
        self.statistics["timeslot_overbookings"] = timeslot_overbookings
        return self.score
