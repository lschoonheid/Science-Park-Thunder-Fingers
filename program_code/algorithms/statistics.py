from typing import Callable
from ..classes.schedule import Schedule
from ..classes.node import NodeSC
from ..classes.student import Student
from ..classes.timeslot import Timeslot
from ..classes.activity import Activity

# from ..classes.result import Result


# TODO: #15 Implement objective function which couples a score to a schedule
# TODO: #27 see if some functions can be cached
class Statistics:
    # TODO: #26 complete list below
    """
    Check for hard constraints:
     - lectures only happen once
     * overbooked timeslots (more than one activity linked)
     * overbooked timeslots (over room capacity)
     * overbooked timeslots (over tutorial/practical capacity)
     * activities (eg lectures) surplus timeslots
     * students missing timeslots for activities
     * students with multiple timeslots for 1 activity
     * student should only follow each class once (eg: one wc1 and one wc2 in student schedule)

     Check for soft constraints:
     * students with double booked hours
     - timeslots without assigned students
     - free periods for student (max three is hard constraint)
     - using evening timeslot

     Optional:
     - least amount of unique classes (wc1 only given once etc.)
    """

    # def __init__(self) -> None:
    #     self.statistics: dict = {}
    #     self.score: float = 0

    def node_has_activity(self, node: NodeSC):
        if len(node.activities) > 0:
            return True
        return False

    def student_has_period(self, student: Student, timeslot: Timeslot):
        """Verify if `student` already has period of `timeslot` booked"""
        new_moment = (timeslot.day, timeslot.period)
        for booked_timeslot in student.timeslots.values():
            booked_moment = (booked_timeslot.day, booked_timeslot.period)
            if booked_moment == new_moment:
                return False
        return True

    def student_has_activity_assigned(self, student: Student, activity: Activity):
        """Verify whether `student` already has a timeslot for `activity`."""
        for assigned_slot in student.timeslots.values():
            for activity_timeslot in activity.timeslots.values():
                if assigned_slot.id == activity_timeslot.id:
                    # Student already has assigned timeslot for activity
                    return True
        return False

    def student_timeslots_for_activity(self, student: Student, activity: Activity):
        """Count `student`'s assigned `timeslot`s for `activity`."""
        timeslots_assigned = 0
        for assigned_slot in student.timeslots.values():
            for activity_timeslot in activity.timeslots.values():
                if assigned_slot.id == activity_timeslot.id:
                    timeslots_assigned += 1
        return timeslots_assigned

    def timeslot_activity_overbooked(self, timeslot: Timeslot, verbose=False):
        """Count overbooked `activity` for `timeslot`."""
        overbookings = max(len(timeslot.activities) - 1, 0)
        if overbookings > 0:
            bookings = [str(activity) for activity in timeslot.activities.values()]

            if verbose:
                print(f"HARD CONSTRAINT: Overbooked timeslot: {timeslot.id} {timeslot} has {bookings}")
        return overbookings

    def room_overbooked(self, timeslot: Timeslot):
        """Count timeslot (chair) capacity surplus."""
        return max(timeslot.enrolled_students - timeslot.room.capacity, 0)

    def timeslot_student_overbooked(self, timeslot: Timeslot):
        """Count surplus of students booked for timeslot."""
        return max(timeslot.enrolled_students - timeslot.capacity, 0)

    def can_assign_timeslot_activity(self, timeslot: Timeslot, activity: Activity):
        """Verify if a timeslot can be added to activity."""
        # Can never assign two activities to one timeslot
        if self.node_has_activity(timeslot):
            return False

        # Can always assign timeslots to tutorials/practicals
        if activity.max_timeslots is None:
            return True

        # Can't assign more timeslots than max_timeslots
        if len(activity.timeslots) >= activity.max_timeslots:
            return False

        # One instance of activity means all students must fit in room
        if activity.max_timeslots == 1 and timeslot.room.capacity >= activity.enrolled_students:
            return True
        return len(activity.timeslots) < activity.max_timeslots

    def can_assign_student_timeslot(self, student: Student, timeslot: Timeslot):
        """Verify if a `student` can be added to `timeslot`."""
        if timeslot.enrolled_students >= timeslot.capacity:
            return False
        # TODO also check if student already has activity assigned
        return True

    def activity_overbooked(self, activity: Activity):
        """Count surplus timeslots linked to `activity`."""
        if activity.max_timeslots is None:
            return 0
        return max(len(activity.timeslots) - activity.max_timeslots, 0)

    def students_unbooked(self, activity: Activity):
        """Count how many enrolled students of `activity` don't have a timeslot for it assigned."""
        unbooked_students = 0
        for student in activity.students.values():
            unbooked_students += int(not self.student_has_activity_assigned(student, activity))
        return unbooked_students

    def student_overbooked(self, student: Student, verbose=False):
        """Count overbooked periods for `student`."""
        bookings = set()
        double_bookings: int = 0
        for timeslot in student.timeslots.values():
            moment = (timeslot.day, timeslot.period)
            if moment in bookings:
                double_bookings += 1

                if verbose:
                    print(f"MALUS: overbooked period for {student.name}: {moment} >1 times")
            else:
                bookings.add(moment)
        return double_bookings

    def aggregate(self, count_function: Callable[[NodeSC], int], nodes_dict: dict[int, NodeSC]):
        """Return sum of `count_function` for all `Node` in `nodes_dict`."""
        count = 0
        for node in nodes_dict.values():
            count += count_function(node)
        return count
