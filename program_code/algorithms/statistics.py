from typing import Callable
import operator
import numpy as np
from ..classes.nodes import *

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
     - Een tussenslot voor een student op een dag levert één maluspunt op.
     - Twee tussensloten op één dag voor een student levert drie maluspunten op.
     - Drie tussensloten op één dag is niet toegestaan. De kans op verzuim bij meerdere tussensloten is namelijk aanzienlijk groter dan bij één tussenslot.

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

    def sort_nodes(self, nodes: list[NodeSC], attr: str, reverse=False):
        return sorted(nodes, key=operator.attrgetter(attr), reverse=reverse)

    def node_has_activity(self, node):
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

    # Soft constraints:
    def evening_bookings(self, room: Room):
        """Count booked evening timeslots for `room`."""
        # Evening timeslot
        evening_period = 4
        evening_bookings = 0
        for timeslot in room.timeslots.values():
            if timeslot.period == evening_period:
                evening_bookings += len(timeslot.activities)
        return evening_bookings

    def student_overbooked(self, student: Student, verbose=False):
        """Count overbooked periods for `student`."""
        bookings = set()
        double_bookings: int = 0
        for timeslot in student.timeslots.values():
            if timeslot.moment in bookings:
                double_bookings += 1

                if verbose:
                    print(f"MALUS: overbooked period for {student.name}: {timeslot.moment} >1 times")
            else:
                bookings.add(timeslot.moment)
        return double_bookings

    def gap_periods(self, student: Student):
        """Count free periods in between the first and last active period of `student`."""
        timeslots_sorted: list[Timeslot] = self.sort_nodes(student.timeslots.values(), "moment")  # type: ignore

        timeslot_day: dict[int, list[Timeslot]] = {}
        # Sort timeslots in buckets per day
        day = -1
        for timeslot in timeslots_sorted:
            if timeslot.day > day:
                day = timeslot.day
                timeslot_day[timeslot.day] = [timeslot]
            else:
                timeslot_day[timeslot.day].append(timeslot)

        # Index is the gaps on a day, value is the number of occurences
        gap_frequency = np.zeros(4)
        previous_period = -1
        for day in timeslot_day.values():
            gaps_today = 0
            for i, timeslot in enumerate(day):
                if i == 0:
                    previous_period = timeslot.period - 1
                current_period = timeslot.period
                # Gap is difference between current and last period - 1, if the timeslots are simultaneous take gap = 0
                gaps_today += max(current_period - previous_period - 1, 0)
                previous_period = timeslot.period
            # TODO: #38 differentiate between:
            # 1 gap -> 1 malus point
            # 2 gaps -> 3 malus points
            # >2 gaps -> hard constraint
            assert gaps_today >= 0, "Cannot have negative gaps."
            if gaps_today >= 3:
                gap_frequency[3] += 1
            else:
                gap_frequency[gaps_today] += 1

        return gap_frequency

    def aggregate(self, count_function: Callable[[NodeSC], int], nodes_dict: dict[int, NodeSC]):
        """Return sum of `count_function` for all `Node` in `nodes_dict`."""
        count = 0
        for node in nodes_dict.values():
            count += count_function(node)
        return count
