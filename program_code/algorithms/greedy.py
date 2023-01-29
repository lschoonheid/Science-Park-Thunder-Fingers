import random
import operator
from tqdm import tqdm
from typing import Callable
from warnings import warn
from .solver import Solver
from ..classes import *
from ..classes.result import Result

class Greedy(Solver):
    def draw_uniform_recursive(
            self,
            nodes1: list[NodeSC],
            nodes2: list[NodeSC],
            condition: Callable[
                [NodeSC, NodeSC],
                bool,
            ],
            negation=False,
            _recursion_limit=10000,
            _combination_set: set | None = None,
        ):
            """Recursively try to pick two random nodes to satisfy `condition(node1, node2) == True`."""
            # assert _recursion_limit > 0, "Reached recursion limit"
            if _recursion_limit == 0:
                print("ERROR: reached recursion depth limit!")
                return None

            # Initialization
            if not _combination_set:
                _combination_set = set()

            max_combinations = len(nodes1) * len(nodes2)
            # print(f"{1000 - _recursion_limit}/{max_combinations}")

            if len(_combination_set) == max_combinations:
                # Reached all possible combinations
                return None

            node1 = random.choice(nodes1)
            node2 = random.choice(nodes2)

            combination = (node1.id, node2.id)
            condition_value = condition(node1, node2)
            if negation:
                # If boolean has to be mirrored, mirror it
                condition_value = not condition_value

            # TODO: Possibly faster to generate all combinations and iterate?
            if combination in _combination_set:
                # Combination already tried, try again with different combination
                return self.draw_uniform_recursive(
                    nodes1,
                    nodes2,
                    condition,
                    negation=negation,
                    _recursion_limit=_recursion_limit - 1,
                    _combination_set=_combination_set,
                )
            elif not condition_value:
                _combination_set.add(combination)
                assert len(_combination_set) <= max_combinations, "Combination set out of order"

                return self.draw_uniform_recursive(
                    nodes1,
                    nodes2,
                    condition,
                    negation=negation,
                    _recursion_limit=_recursion_limit - 1,
                    _combination_set=_combination_set,
                )

            return node1, node2

    def sort_nodes(self, nodes, attr: str, reverse=False):
        return sorted(nodes, key=operator.attrgetter(attr), reverse=reverse)

    def assign_hoorcollege_to_room(self, schedule: Schedule):
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
        # self.rate_timeslots_activity(schedule, activities_free)

        return activities_bound, activities_free

    def assign_students_to_hc(self, schedule: Schedule, activities_bound: list[Activity]):
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

    def assign_students_wc_en_p(self, schedule: Schedule, i_max=10000):
        available_activities = list(schedule.activities.values())

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

            available_students_linked = list(getattr(activity, "_unassigned_students"))
            timeslots_linked = list(activity.timeslots.values())

            # Pick student that does not have a timeslot for this activity
            draw_student = self.draw_uniform_recursive(
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

            draw_timeslot = self.draw_uniform_recursive([student], timeslots_linked, self.verifier.can_assign_student_timeslot)  # type: ignore
            if not draw_timeslot:
                if self.verbose:
                    warn(f"ERROR: Could no longer find available timeslots for {activity} after {i} iterations.")
                continue
            timeslot = draw_timeslot[1]

            # TODO: #30 improvement would be to first see if there is an available one, but it wouldn't necessarily be uniform (see commented code)

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
            # TODO: #31 reassign timeslots with no connected students and try again (allowed to ignore non uniform redraw to permit solution)

        # Return Result
        return Result(schedule=schedule, iterations=i_max, solved=activities_finished)

    def assign_students_try(self, schedule: Schedule, i_max=10000, activities_free: list[Activity]):

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

            available_students_linked = list(getattr(activity, "_unassigned_students"))
            timeslots_linked = list(activity.timeslots.values())

            # Pick student that does not have a timeslot for this activity
            draw_student = self.draw_uniform_recursive(
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

            draw_timeslot = self.draw_uniform_recursive([student], timeslots_linked, self.verifier.can_assign_student_timeslot)  # type: ignore
            if not draw_timeslot:
                if self.verbose:
                    warn(f"ERROR: Could no longer find available timeslots for {activity} after {i} iterations.")
                continue
            timeslot = draw_timeslot[1]

            # TODO: #30 improvement would be to first see if there is an available one, but it wouldn't necessarily be uniform (see commented code)

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
            # TODO: #31 reassign timeslots with no connected students and try again (allowed to ignore non uniform redraw to permit solution)

        # Return Result
        return Result(schedule=schedule, iterations=i_max, solved=activities_finished)


    def rate_timeslots_activity(self, schedule: Schedule, aviable_activity: list[Activity]):
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
                if self.verifier.node_has_activity(timeslot):
                    continue
                # Set rate to 0
                rate = 0
                # Go trough all students
                for student in aviable_student:
                    # Check if the students has the activity
                    if activity in student.activities.values():
                        # Check if the student already has activity in the current period
                        if self.verifier.student_has_period(student, timeslot):
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
                total_capacity += min(activity.capacity, highest_timeslots.capacity)
                # If the lenght of the list with the highest timeslot is 0 make new list
                if len(max_keys) == 0:
                    max_val = max(rating.values())
                    max_keys = [k for k in rating if rating[k] == max_val]

        return Result(schedule=schedule, solved=True)

    def greedy_random(self, schedule: Schedule, i_max: int):
        activities_bound, activities_free = self.assign_hoorcollege_to_room(schedule)

        self.assign_students_to_hc(schedule, activities_bound)

        self.rate_timeslots_activity(schedule, activities_free)

        self.assign_students_try(schedule, i_max, activities_free)

        return self.assign_students_wc_en_p(schedule, i_max)


    def solve(self, schedule: Schedule, i_max: int | None = None, method="uniform", strict=True):
        if i_max is None:
            # Program on average has to iterate over each activity once, which with a random distribution it takes more iterations
            i_min = 100 * len(schedule.activities)
            guess_required_edges = 0
            for activity in schedule.activities.values():
                guess_required_edges += activity.enrolled_students
            i_max = max(guess_required_edges, i_min)

        if method == "uniform" and strict:
            return self.greedy_random(schedule, i_max)  # type: ignore
        raise ValueError("Did not recognize solver.")