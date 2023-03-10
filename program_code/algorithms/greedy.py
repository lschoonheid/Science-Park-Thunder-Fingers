import random
import operator
from tqdm import tqdm
from typing import Callable
from warnings import warn

from program_code.algorithms.randomizer import Randomizer
from .generate import make_prototype
from .solver import Solver

from ..classes import *
from ..classes.result import Result


class Greedy(Solver):
    def assign_hoorcollege_to_room(self, schedule: Schedule):
        """Seperate the activities into hoorcollege and werkcollege and practica and
        assign hoorcolleges to timeslot.
        pre: schedule
        post: seperated activities
        """
        activities = list(schedule.activities.values())
        timeslots = list(schedule.timeslots.values())

        # Activities with max timeslots
        activities_bound: list[Activity] = []
        # Activitities with unbound number of timeslots
        activities_free: list[Activity] = []

        # Sort activities into bound and unbound max_timeslots
        for activity in activities:
            if activity.max_timeslots:
                # Hoorcolleges
                activities_bound.append(activity)
            else:
                # Werkcolleges en practica activiteiten
                activities_free.append(activity)

        # assign hoorcolleges with max timeslots most efficiently on capacity
        self.assign_activities_timeslots_greedy(schedule, activities_bound, timeslots, reverse=True)

        return activities_bound, activities_free

    def assign_students_to_hc(self, schedule: Schedule, activities_bound: list[Activity]):
        """Assign students to the timeslots of the hoorcollege activities
        pre: schedule, list of activities (hoorcollege)
        """
        # Get a list of all the students
        aviable_student: list[Student] = list(schedule.students.values())

        # Go trough all HC activities
        for activity in activities_bound:
            # Get timeslot for the HC activity
            timeslots_linked = list(activity.timeslots.values())
            # Go trough al students
            for student in aviable_student:
                # Check for every student if they have the Hc activity
                if activity in student.activities.values():
                    # Connect timeslot of activity to the student
                    schedule.connect_nodes(student, timeslots_linked[0])

    def assign_students_wc_p(self, schedule: Schedule, activities_free: list[Activity]):
        """Assign students to the timeslots of the werkcollege and practicum activities without using
        draw uniform recursive. Uniform recursive works better.
        pre: schedule, list of activities (werkcollege and practicum)
        post: schedule
        """
        edges = set()
        # Necassary for the solve
        i = 1000

        for activity in activities_free:

            # Build index on students that don't yet have a timeslot assigned for this activity
            if not hasattr(activity, "_unassigned_students"):
                setattr(activity, "_unassigned_students", set(activity.students.values()))

            # Get the students and timeslots linked to the activity
            available_students_linked = list(getattr(activity, "_unassigned_students"))
            timeslots_linked = list(activity.timeslots.values())

            # Go trough al students
            for student in available_students_linked:
                timeslot_list = []
                # Go trough the timeslot of the activity
                for timeslot_chose in timeslots_linked:
                    # Check if student already has activity during current activity
                    if self.node_has_period(student, timeslot_chose) == False:
                        timeslot_list.append(timeslot_chose)

                    # Current activity does not have a timeslot that allows for no course conflicts
                    if len(timeslot_list) == 0:
                        # Pick a random timeslot
                        timeslot = random.choice(timeslots_linked)
                    else:
                        # Pick a random timeslot which has no course conflicts for student
                        timeslot = random.choice(timeslot_list)

                    # Skip if timeslot is already linked to student
                    edge = (student.id, timeslot.id)
                    if edge in edges:
                        if self.verbose:
                            warn("ERROR: attempted adding same edge twice.")
                        continue

                    # Success: found a pair of student, timeslot that meet all requirements and can be booked
                    schedule.connect_nodes(student, timeslot)
                    edges.add(edge)
        return Result(schedule=schedule, iterations=i, solved=True)

    def assign_students_wc_p_uniform(self, schedule: Schedule, activities_free: list[Activity]):
        """Assign students to the timeslots of the werkcollege and practicum activities without using
        draw uniform recursive. Uniform recursive works better.
        pre: schedule, list of activities (werkcollege and practicum)
        post: schedule
        """
        i_max = 10000
        available_activities = activities_free

        # Remember students that have already been assigned a timeslot for activities
        # Uses tuples of (activity.id, student.id)
        activity_students_assigned: set[tuple[int, int]] = set()

        # Try making connections for i_max iterations
        edges = set()
        for i in tqdm(range(i_max), disable=not self.verbose, desc="Trying connections:"):
            if len(available_activities) == 0:
                # Solver has come to completion: all activities have its students assigned to timeslots
                return Result(schedule=schedule, iterations=i, solved=True)

            # Take random unfinished activity
            activity = random.choice(available_activities)

            # Build index on students that don't yet have a timeslot assigned for this activity
            if not hasattr(activity, "_unassigned_students"):
                setattr(activity, "_unassigned_students", set(activity.students.values()))

            # Get the students linked to the current activity
            available_students_linked = list(getattr(activity, "_unassigned_students"))
            timeslots_linked = list(activity.timeslots.values())

            # Pick student that does not have a timeslot for this activity
            draw_student = Randomizer.draw_uniform(
                [activity], available_students_linked, lambda a, s: s in getattr(a, "_unassigned_students")  # type: ignore
            )

            # No available students means this activity has been assigned to all its students, it's finished.
            if not draw_student:
                # Remove activity from available activities
                for index, test_activity in enumerate(available_activities):
                    if activity == test_activity:
                        available_activities.pop(index)
                # Remove index
                delattr(activity, "_unassigned_students")
                continue
            student: Student = draw_student[1]  # type: ignore

            timeslot_list = []
            # Go trough the timeslot of the activity
            for timeslot_chose in timeslots_linked:
                # Check if the student already has an activity in the current timeslot
                if self.node_has_period(student, timeslot_chose) == False:
                    timeslot_list.append(timeslot_chose)

            # Activity does not have timeslot that causes no course conflict for the student
            if len(timeslot_list) == 0:
                # Pick a random timeslot
                timeslot = random.choice(timeslots_linked)
            else:
                # Pick a timeslot that causes no course conflict
                timeslot = random.choice(timeslot_list)

            # Skip if timeslot is already linked to student
            edge = (student.id, timeslot.id)
            if edge in edges:
                if self.verbose:
                    warn("ERROR: attempted adding same edge twice.")
                continue

            # Success: found a pair of student, timeslot that meet all requirements and can be booked
            schedule.connect_nodes(student, timeslot)
            edges.add(edge)
            # Remove student from index of unassigned students for this activity
            getattr(activity, "_unassigned_students").remove(student)
            activity_students_assigned.add((activity.id, student.id))
        activities_finished = len(available_activities) == 0

        if not activities_finished:
            if self.verbose:
                warn(
                    f"ERROR: could not finish schedule within {i_max} iterations. Unfinished activities: {available_activities}"
                )

        # Return Result
        return Result(schedule=schedule, iterations=i_max, solved=activities_finished)

    def rate_timeslots_activity(self, schedule: Schedule, aviable_activity: list[Activity]):
        """Rate the timeslots for the werkcollege and practicum activities and assign the
        highest rates timeslots to the activites
        pre: schedule, list of activities (werkcollege and practicum)
        post: schedule
        """
        # Get a list of timeslots and students
        available_timeslots: list[Timeslot] = list(schedule.timeslots.values())
        aviable_student: list[Student] = list(schedule.students.values())
        rating = {}

        # Go trough all activities in the activity list (only Wc and P)
        for activity in aviable_activity:
            # Get the amount of enrolled students for the activity
            activity_enrolments = activity.enrolled_students
            # Set total capacity on 0
            total_capacity = 0
            # Go trough all timeslots
            for timeslot in available_timeslots:
                # Skip timeslot if it already has activity
                if self.node_has_activity(timeslot):
                    continue
                # Set rate to 0
                rate = 0
                # Go trough all students
                for student in aviable_student:
                    # Check if the students has the activity
                    if activity in student.activities.values():
                        # Check if the student already has activity in the current period
                        if self.node_has_period(student, timeslot) == False:
                            # If studens has no activity in current period increase rating
                            rate += 1
                # Save the total rating for every timeslot
                rating[timeslot] = rate

            # Get the max rated timeslots
            max_val = max(rating.values())
            max_keys = [k for k in rating if rating[k] == max_val]

            # Keep adding activities until the total_capacity is higher then the enrolment
            while total_capacity < activity_enrolments:
                # Randomly chose on of the highest rated timeslots
                highest_timeslots: Timeslot = random.choice(max_keys)
                # Remove the selected timeslot from the list and dictionary
                max_keys.remove(highest_timeslots)
                del rating[highest_timeslots]
                # Connect the nodes of activity and timeslot
                schedule.connect_nodes(activity, highest_timeslots)
                # Change total capacity
                if activity.capacity_input != None:
                    total_capacity += min(activity.capacity_input, highest_timeslots.capacity)
                # If the lenght of the list with the highest timeslot is 0 make new list
                if len(max_keys) == 0:
                    max_val = max(rating.values())
                    max_keys = [k for k in rating if rating[k] == max_val]

        return Result(schedule=schedule, solved=True)

    def greedy_random(self, schedule: Schedule, i_max: int):
        """Perform the greedy algorithm
        pre: schedule
        post: schedule (solved)
        """
        activities_bound, activities_free = self.assign_hoorcollege_to_room(schedule)

        self.assign_students_to_hc(schedule, activities_bound)

        self.rate_timeslots_activity(schedule, activities_free)

        return self.assign_students_wc_p_uniform(schedule, activities_free)

    def solve(self, schedule: Schedule | None = None, i_max: int | None = None, method=None, strict=True):
        """Solve function for the algorithm
        pre: schedule
        post: schedule (solved)
        """
        if schedule is None:
            schedule = make_prototype(self.students_input, self.courses_input, self.rooms_input)
        if i_max is None:
            # Program on average has to iterate over each activity once, which with a random distribution it takes more iterations
            i_min = 100 * len(schedule.activities)
            guess_required_edges = 0
            for activity in schedule.activities.values():
                guess_required_edges += activity.enrolled_students
            i_max = max(guess_required_edges, i_min)

        return self.greedy_random(schedule, i_max)  # type: ignore
