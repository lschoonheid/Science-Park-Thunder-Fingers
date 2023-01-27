import random
import operator
from tqdm import tqdm
from typing import Callable
from warnings import warn
from .solver import Solver
from ..classes import *
from ..classes.result import Result

class Greedy(Solver):
    def connect_random(self, schedule: Schedule, i_max: int = 5):
        """Make a completely random schedule"""
        for _ in range(i_max):
            student: Student = random.choice(list(schedule.students.values()))

            activity: Activity = random.choice(list(student.activities.values()))
            timeslot: Timeslot = random.choice(list(schedule.timeslots.values()))
            schedule.connect_nodes(student, timeslot)
            schedule.connect_nodes(activity, timeslot)

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

        return activities_bound, activities_free

    # def assign_hoorcollege_to_room(self, schedule: Schedule):
    #     # Make shuffled list of timeslots so they will be picked randomly
    #     timeslots_shuffled = list(schedule.timeslots.values())
    #     random.shuffle(timeslots_shuffled)

    #     # Get the seperated hoorcolleges and Werkcolleges en practica activities
    #     activities_bound, activities_free = self.seperate_activities(schedule)

    #     # Hard constraint to never double book a timeslot, so iterate over them
    #     for timeslot in timeslots_shuffled:
    #         # Skip timeslot if it already has activity
    #         if self.verifier.node_has_activity(timeslot):
    #             continue

    #         # Draw an activity that doesnt already have its max timeslots
    #         draw = self.draw_uniform_recursive([timeslot], activities_bound, self.verifier.can_assign_timeslot_activity)  # type: ignore

    #         if draw:
    #             activities_bound = draw[1]
    #             schedule.connect_nodes(activities_bound, timeslot)

    def assign_students_hoorcollege(self, schedule: Schedule, i_max=10000):
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

    def rate_timeslots(self, schedule: Schedule):
        available_timeslots = list(schedule.timeslots.values())
        student = list(schedule.students.values())
        rating = {}

        for timeslot in available_timeslots:
            # Skip timeslot if it already has activity
            if self.verifier.node_has_activity(timeslot):
                continue

            rate = 0
            for student_timeslots in student:
                if self.verifier.student_has_period(student_timeslots, timeslot):
                    rate += 1
            rating[timeslot] = rate

        print(rating)

    def hoorcollege(self, schedule: Schedule, i_max: int):
        """Make a completely random schedule solution"""

        # First make sure each activity has a timeslot
        self.assign_hoorcollege_to_room(schedule)

        self.rate_timeslots(schedule)

        return self.assign_students_hoorcollege(schedule, i_max)


    def solve(self, schedule: Schedule, i_max: int | None = None, method="uniform", strict=True):
        if i_max is None:
            # Program on average has to iterate over each activity once, which with a random distribution it takes more iterations
            i_min = 100 * len(schedule.activities)
            guess_required_edges = 0
            for activity in schedule.activities.values():
                guess_required_edges += activity.enrolled_students
            i_max = max(guess_required_edges, i_min)

        if method == "uniform" and strict:
            return self.hoorcollege(schedule, i_max)  # type: ignore
        raise ValueError("Did not recognize solver.")


    # def rate_timeslots(self, student: Student, schedule: Schedule):
    #     for day in range(5):
    #         for period in range(5):
    #             new_moment = (day, period)
    #             for booked_timeslot in student.timeslots.values():
    #                 booked_moment = (booked_timeslot.day, booked_timeslot.period)
    #                 if booked_moment == new_moment:
    #                     return False
    #             return True