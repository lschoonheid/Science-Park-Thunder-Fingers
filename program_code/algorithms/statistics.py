from typing import Callable
import operator
import numpy as np
from ..classes import *


class Statistics:
    """
    Class for verifying constraints and retrieving statistics of a schedule.

    Check for hard constraints:
     * overbooked timeslots (more than one activity linked)
     * overbooked timeslots (over room capacity)
     * overbooked timeslots (over tutorial/practical capacity)
     * activities (eg lectures) surplus timeslots
     * activities have time conflicts (eg: lectures at the same time as practica/tutorials of course)
     * students missing timeslots for activities
     * students with multiple timeslots for 1 activity
     * student should only follow each class once (eg: one wc1 and one wc2 in student schedule)

     Check for soft constraints:
     * using evening timeslot
     * students with double booked hours
     * One gap period on a day
     * Two gap periods on a day
     * Three gap periods on a day (not allowed)
    """

    @staticmethod
    def sort_objects(objects, attr: str, reverse=False):
        """Sort objects on attribute."""
        return sorted(objects, key=operator.attrgetter(attr), reverse=reverse)

    @staticmethod
    def aggregate(count_function: Callable[[NodeSC], int], nodes_dict: dict[int, NodeSC]):
        """Return sum of `count_function` for all `Node` in `nodes_dict`."""
        count = 0
        for node in nodes_dict.values():
            count += count_function(node)
        return count

    @staticmethod
    def node_has_activity(node):
        """Verify whether node has any activities assigned."""
        if len(node.activities) > 0:
            return True
        return False

    @staticmethod
    def node_has_period(node, timeslot: Timeslot):
        """Verify if `node` already has period of `timeslot` booked"""
        new_moment = timeslot.moment
        for booked_timeslot in node.timeslots.values():
            if booked_timeslot.moment == new_moment:
                return True
        return False

    def moment_conflicts(self, nodes1, nodes2):
        """Find if any bookings between `nodes1` and `nodes2` conflict."""
        for node1 in nodes1:
            for node2 in nodes2:
                if node1.id == node2.id:
                    continue
                for timeslot1 in node1.timeslots.values():
                    for timeslot2 in node2.timeslots.values():
                        if timeslot1.moment == timeslot2.moment:
                            return True
        return False

    def student_has_activity_assigned(self, student: Student, activity: Activity):
        """Verify whether `student` already has a timeslot for `activity`."""
        for assigned_timeslot in student.timeslots.values():
            for activity_timeslot in activity.timeslots.values():
                if assigned_timeslot.id == activity_timeslot.id:
                    # Student already has assigned timeslot for activity
                    return True
        return False

    def student_timeslots_for_activity(self, student: Student, activity: Activity):
        """Count `student`'s assigned `timeslot`s for `activity`."""
        timeslots_assigned = 0
        for assigned_timeslot in student.timeslots.values():
            for assigned_activity in assigned_timeslot.activities.values():
                if assigned_activity == activity:
                    timeslots_assigned += 1
        return timeslots_assigned

    def timeslot_student_overbooked(self, timeslot: Timeslot):
        """Count surplus of students booked for timeslot."""
        return max(timeslot.enrolled_students - timeslot.capacity, 0)

    def can_assign_timeslot_activity(self, timeslot: Timeslot, activity: Activity):
        """Verify if a timeslot can be added to activity."""
        # Can never assign two activities to one timeslot
        if self.node_has_activity(timeslot):
            return False

        # Check whether timeslot is already taken by a lecture of the same course
        for bound_activity in activity.course.bound_activities.values():
            if self.node_has_period(bound_activity, timeslot):
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

        # Verify `activity` doesn't already have its maximum amount of timeslots assigned (max=1 for lectures)
        return len(activity.timeslots) < activity.max_timeslots

    def can_assign_student_timeslot(self, student: Student, timeslot: Timeslot):
        """Verify if a `student` can be added to `timeslot`."""
        if timeslot.enrolled_students >= timeslot.capacity:
            return False
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

    def evening_bookings(self, room: Room):
        """Count booked evening timeslots for `room`."""
        # Evening timeslot is the 4th period
        evening_period = 4
        evening_bookings = 0
        for timeslot in room.timeslots.values():
            if timeslot.period == evening_period and timeslot.enrolled_students > 0:
                evening_bookings += len(timeslot.activities)
        return evening_bookings

    def student_overbooked(self, student: Student):
        """Count overbooked periods for `student`."""
        bookings = set()
        double_bookings: int = 0
        for timeslot in student.timeslots.values():
            # See if moment had already been booked once
            if timeslot.moment in bookings:
                double_bookings += 1
            else:
                bookings.add(timeslot.moment)
        return double_bookings

    def sort_to_day(self, timeslots) -> dict[int, list[Timeslot]]:
        """Sorts `timeslots` per day to dict[day, timeslots]."""

        timeslot_day: dict[int, list[Timeslot]] = {}
        # Sort timeslots in buckets per day
        day = -1
        for timeslot in timeslots:
            if timeslot.day not in timeslot_day:
                timeslot_day[timeslot.day] = [timeslot]
            else:
                timeslot_day[timeslot.day].append(timeslot)

        # Sort timeslots in periods per day
        for day_index in timeslot_day:
            if len(timeslot_day[day_index]) == 1:
                continue
            timeslot_day[day_index] = self.sort_objects(timeslot_day[day_index], "moment")  # type: ignore
        return timeslot_day

    def gaps_on_day(self, day: list[Timeslot]):
        """Count gaps on `day` between timeslots in day.
        Assumes list `day` only includes timeslots of one day."""

        # Sort timeslots to day and period
        day_sorted = self.sort_objects(day, "moment")  # type: ignore

        # Initial counters
        gaps_today = 0
        previous_period = -1

        # Iterate over timeslots per day
        for i, timeslot in enumerate(day_sorted):
            if i == 0:
                # New day, reset
                previous_period = timeslot.period - 1
            current_period = timeslot.period
            # Gap is difference between current and last period - 1, if the timeslots are simultaneous take gap = 0
            gaps_today += max(current_period - previous_period - 1, 0)
            previous_period = timeslot.period
        assert gaps_today >= 0, "Cannot have negative gaps."
        return gaps_today

    def timeslot_gives_gaps(self, student: Student, timeslot: Timeslot, limit=3):
        """See if adding `timeslot` to `student` results in  `student` having `limit` or more gaps on that day."""
        # gaps_on_day will never be smaller than 0
        if limit == 0:
            return True

        # Pretend timeslot is assigned to student
        if len(student.timeslots.values()) == 0:
            return False

        # Only consider timeslots on same day as `timeslot`
        day: list[Timeslot] = []
        day_index = timeslot.day
        for booked_timeslot in student.timeslots.values():
            if booked_timeslot.day == day_index:
                day.append(booked_timeslot)
        if len(day) == 0:
            return False

        # Count gaps on day of new timeslot if timeslot was added
        day.append(timeslot)
        gaps_on_day = self.gaps_on_day(day)
        if gaps_on_day >= limit:
            return True
        return False

    def student_day_gaps_frequency(self, student: Student, day_index: int):
        """DEPRECATED: Count frequency of 1-gap, 2-gap and >2-gaps on day."""
        if len(student.timeslots.values()) == 0:
            return False

        # Only consider timeslots on same day as `timeslot`
        day: list[Timeslot] = []
        for booked_timeslot in student.timeslots.values():
            if booked_timeslot.day == day_index:
                day.append(booked_timeslot)
        if len(day) == 0:
            return 0

        gap_frequency = np.zeros((4,), dtype=int)
        gaps_today = self.gaps_on_day(day)
        # Count gaps on day of new timeslot if timeslot was added
        if gaps_today >= 3:
            gap_frequency[3] += 1
        else:
            gap_frequency[gaps_today] += 1

        return gap_frequency

    def gap_periods_student(self, student: Student):
        """Count free periods per day in between the first and last active period of `student`. Sort to buckets of gaps per day."""
        timeslot_day = self.sort_to_day(student.timeslots.values())
        # Index is the gaps on a day, value is the number of occurences
        gap_frequency = np.zeros((4,), dtype=int)
        for day in timeslot_day.values():
            gaps_today = self.gaps_on_day(day)
            if gaps_today >= 3:
                gap_frequency[3] += 1
            else:
                gap_frequency[gaps_today] += 1

        return gap_frequency
