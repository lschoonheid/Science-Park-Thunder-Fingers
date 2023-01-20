from .statistics import Statistics
from ..classes.node import NodeSC
from ..classes.schedule import Schedule
import operator


class Solver:
    def __init__(self, verbose=False):
        self.verifier = Statistics()
        self.verbose = verbose

    def sort_nodes(self, nodes: list[NodeSC], attr: str, reverse=False):
        return sorted(nodes, key=operator.attrgetter(attr), reverse=reverse)

    def assign_activities_timeslots_once(self, schedule: Schedule):
        """Assign each activity the amount of timeslots it requires. Results in non-uniform distribution but ensures each enrolled student can book timeslot for activity."""
        # Use greedy: sort both lists in order of capacity
        activities_sorted = self.sort_nodes(list(schedule.activities.values()), "enrolled_students", reverse=True)
        timeslots_sorted = self.sort_nodes(list(schedule.timeslots.values()), "capacity()", reverse=True)
        for activity in activities_sorted:
            total_capacity = 0
            activity_enrolments = activity.enrolled_students

            for timeslot in timeslots_sorted:
                if total_capacity >= activity_enrolments:
                    # Reached required capacity, continue to next activity
                    break

                if self.verifier.can_assign_timeslot_activity(timeslot, activity):
                    schedule.connect_nodes(activity, timeslot)
                    total_capacity += timeslot.room.capacity

            if self.verbose and total_capacity < activity_enrolments:
                print(f"FAILED: {total_capacity, activity.enrolled_students}")

    # Mockup function only for type hinting
    def solve(self, schedule: Schedule, i_max: int | None = None, method: str = "", strict=True):
        return self.verifier.Result(schedule)
