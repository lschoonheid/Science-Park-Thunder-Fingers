from .statistics import Statistics
from ..classes.node import NodeSC
from ..classes.schedule import Schedule
from ..classes.activity import Activity
from ..classes.timeslot import Timeslot
import operator


class Solver:
    def __init__(self, verbose=False):
        self.verifier = Statistics()
        self.verbose = verbose

    def sort_nodes(self, nodes: list[NodeSC], attr: str, reverse=False):
        return sorted(nodes, key=operator.attrgetter(attr), reverse=reverse)

    def assign_activities_timeslots_greedy(
        self, schedule: Schedule, activities: list[Activity], timeslots: list[Timeslot], reverse=True
    ):
        activities_sorted = self.sort_nodes(activities, "enrolled_students", reverse=reverse)
        timeslots_sorted = self.sort_nodes(timeslots, "capacity", reverse=reverse)
        for activity in activities_sorted:
            activity_enrolments = activity.enrolled_students
            total_capacity = 0

            for timeslot in timeslots_sorted:
                if total_capacity >= activity_enrolments:
                    # Reached required capacity, stop looking for timeslots
                    break

                # Check if timeslot can be coupled to activity (max_timeslots, timeslot available)
                if self.verifier.can_assign_timeslot_activity(timeslot, activity):
                    schedule.connect_nodes(activity, timeslot)
                    total_capacity += min(activity.capacity, timeslot.capacity)

            if total_capacity < activity_enrolments:
                if self.verbose:
                    print(f"FAILED: {total_capacity, activity.enrolled_students}")
            else:
                if self.verbose:
                    print("Success")

    def assign_activities_timeslots_once(self, schedule: Schedule):
        """Assign each activity the amount of timeslots it requires. Results in non-uniform distribution but ensures each enrolled student can book timeslot for activity."""
        # Use greedy: sort both lists in order of capacity

        activities = list(schedule.activities.values())
        timeslots = list(schedule.timeslots.values())

        # Activities with max timeslots
        activities_bound: list[Activity] = []
        # Activitities with unbound number of timeslots
        activities_free: list[Activity] = []

        # Sort activities into bound and unbound max_timeslots
        for activity in activities:
            if activity.max_timeslots:
                activities_bound.append(activity)
            else:
                activities_free.append(activity)

        # first assign activities with max timeslots most efficiently
        self.assign_activities_timeslots_greedy(schedule, activities_bound, timeslots, reverse=True)
        self.assign_activities_timeslots_greedy(schedule, activities_free, timeslots, reverse=True)

    # Mockup function only for type hinting
    def solve(self, schedule: Schedule, i_max: int | None = None, method: str = "", strict=True):
        return self.verifier.Result(schedule)
