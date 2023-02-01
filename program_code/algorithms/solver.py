import warnings
from typing import TypeVar
from .generate import make_prototype
from .statistics import Statistics
from ..classes import Schedule, Activity, Timeslot
from ..classes.result import Result


class Solver(Statistics):
    """Parent class for constructive solver. Includes reusable methods for laying base of schedule solution."""

    def __init__(
        self,
        students_input: dict,
        courses_input: dict,
        rooms_input: dict,
        method: str | None = "uniform",
        verbose=False,
    ):
        # Take input data to build initial graph state from
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
        activities_sorted = Statistics.sort_objects(activities, "enrolled_students", reverse=reverse)
        timeslots_sorted = Statistics.sort_objects(timeslots, "capacity", reverse=reverse)
        for activity in activities_sorted:
            activity_enrolments = activity.enrolled_students
            total_capacity = 0

            # Add timeslots to `activity` until timeslots make up required capacity
            for timeslot in timeslots_sorted:
                if total_capacity >= activity_enrolments:
                    # Reached required capacity, stop looking for timeslots
                    break

                # Check if timeslot can be coupled to activity
                # (max_timeslots not reached, timeslot available, moment doesn't conflict)
                if not self.can_assign_timeslot_activity(timeslot, activity):
                    continue

                # Add timeslot to activity
                schedule.connect_nodes(activity, timeslot)

                if not activity.capacity:
                    # Activity doesn't have a maximum capacity, added capacity is that of room
                    added_capacity = timeslot.capacity
                else:
                    added_capacity = min(activity.capacity, timeslot.capacity)

                total_capacity += added_capacity

            # If distribution was unsuccesful, warn
            if self.verbose and total_capacity < activity_enrolments:
                warnings.warn(f"FAILED: {total_capacity, activity.enrolled_students}")

    def assign_activities_timeslots_prioritized(self, schedule: Schedule, activities, timeslots):
        """Assign leftover timeslots to activities with preference for activities with more enrolments."""
        # Activities with max timeslots
        activities_bound: list[Activity] = []
        # Activitities with unbound number of timeslots
        activities_free: list[Activity] = []

        # Sort activities into bound and unbound `max_timeslots`
        for course in schedule.courses.values():
            activities_bound.extend(course.bound_activities.values())
            activities_free.extend(course.unbound_activities.values())

        # First assign activities with max timeslots most efficiently, such as lectures
        self.assign_activities_timeslots_greedy(schedule, activities_bound, timeslots, reverse=True)
        self.assign_activities_timeslots_greedy(schedule, activities_free, timeslots, reverse=True)

    def solve(
        self,
        schedule: Schedule | None = None,
        i_max: int | None = None,
        method: str | None = None,
        strict=True,
    ):
        """Construct schedule solution. Mockup function only for type hinting"""
        if schedule is None:
            schedule = make_prototype(self.students_input, self.courses_input, self.rooms_input)
        return Result(schedule)


# class Node or subclass of Node
SolverSC = TypeVar("SolverSC", bound=Solver)
