import warnings
from typing import TypeVar
from .generate import make_prototype
from .statistics import Statistics
from ..classes import Schedule, Activity, Timeslot
from ..classes.result import Result


class Solver(Statistics):
    def __init__(
        self,
        students_input,
        courses_input,
        rooms_input,
        method: str | None = "uniform",
        verbose=False,
    ):
        self.students_input = students_input
        self.courses_input = courses_input
        self.rooms_input = rooms_input

        self.verbose = verbose
        if method is None:
            method = "baseline"
        self.method = method

    def assign_activities_timeslots_greedy(
        self, schedule: Schedule, activities: list[Activity], timeslots: list[Timeslot], reverse=True
    ):
        # Use greedy: sort both lists in order of capacity
        activities_sorted = self.sort_objects(activities, "enrolled_students", reverse=reverse)
        timeslots_sorted = self.sort_objects(timeslots, "capacity", reverse=reverse)
        for activity in activities_sorted:
            activity_enrolments = activity.enrolled_students
            total_capacity = 0

            for timeslot in timeslots_sorted:
                if total_capacity >= activity_enrolments:
                    # Reached required capacity, stop looking for timeslots
                    break

                # Check if timeslot can be coupled to activity (max_timeslots, timeslot available)
                if not self.can_assign_timeslot_activity(timeslot, activity):
                    continue

                # Check if moment is already taken by course lecture
                for bound_activity in activity.course.bound_activities.values():
                    if self.node_has_period(bound_activity, timeslot):
                        continue
                schedule.connect_nodes(activity, timeslot)
                total_capacity += min(activity.capacity, timeslot.capacity)

            if self.verbose and total_capacity < activity_enrolments:
                warnings.warn(f"FAILED: {total_capacity, activity.enrolled_students}")

    def assign_activities_timeslots_sorted(self, schedule, activities, timeslots):
        # Activities with max timeslots
        activities_bound: list[Activity] = []
        # Activitities with unbound number of timeslots
        activities_free: list[Activity] = []

        # Sort activities into bound and unbound max_timeslots
        # TODO: these lines are degenerate of course.bound_activities
        for activity in activities:
            if activity.max_timeslots:
                activities_bound.append(activity)
            else:
                activities_free.append(activity)

        # first assign activities with max timeslots most efficiently
        self.assign_activities_timeslots_greedy(schedule, activities_bound, timeslots, reverse=True)
        # TODO: #42 - lectures never at the same time as practica/tutorials of same course
        self.assign_activities_timeslots_greedy(schedule, activities_free, timeslots, reverse=True)

    # Mockup function only for type hinting
    def solve(
        self,
        schedule: Schedule | None = None,
        i_max: int | None = None,
        method: str | None = None,
        strict=True,
    ):
        if schedule is None:
            schedule = make_prototype(self.students_input, self.courses_input, self.rooms_input)
        return Result(schedule)


# class Node or subclass of Node
SolverSC = TypeVar("SolverSC", bound=Solver)
