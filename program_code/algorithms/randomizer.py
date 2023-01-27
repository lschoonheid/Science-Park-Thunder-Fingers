import random
from tqdm import tqdm
from typing import Callable
from warnings import warn
from .solver import Solver
from .generate import make_prototype
from ..classes import *
from ..classes.result import Result


class Randomizer(Solver):
    def connect_random(self, schedule: Schedule, i_max: int = 5):
        """Make a completely random schedule."""
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
        return_value=False,
        _recursion_limit=10000,
        _combination_set: set | None = None,
    ):
        """Recursively try to pick two random nodes to satisfy `condition(node1, node2) == True`."""
        # assert _recursion_limit > 0, "Reached recursion limit"
        if _recursion_limit == 0:
            raise RecursionError("Recursion depth exceeded")

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

        combination = tuple(sorted([node1.id, node2.id]))
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
                return_value=return_value,
                _recursion_limit=_recursion_limit - 1,
                _combination_set=_combination_set,
            )
        elif condition_value is False:
            _combination_set.add(combination)
            assert len(_combination_set) <= max_combinations, "Combination set out of order"

            return self.draw_uniform_recursive(
                nodes1,
                nodes2,
                condition,
                negation=negation,
                return_value=return_value,
                _recursion_limit=_recursion_limit - 1,
                _combination_set=_combination_set,
            )
        if return_value:
            return node1, node2, condition_value
        return node1, node2

    def assign_activities_timeslots_once(self, schedule: Schedule):
        """Assign each activity the amount of timeslots it requires. Results in non-uniform distribution but ensures each enrolled student can book timeslot for activity."""

        activities = list(schedule.activities.values())
        timeslots = list(schedule.timeslots.values())

        random.shuffle(activities)
        random.shuffle(timeslots)

        self.assign_activities_timeslots_prioritized(schedule, activities, timeslots)

    def assign_activities_timeslots_uniform(self, schedule: Schedule):
        # Make shuffled list of timeslots so they will be picked randomly
        timeslots_shuffled = list(schedule.timeslots.values())
        random.shuffle(timeslots_shuffled)

        activities = list(schedule.activities.values())

        # Hard constraint to never double book a timeslot, so iterate over them
        for timeslot in timeslots_shuffled:
            # Skip timeslot if it already has activity
            if self.node_has_activity(timeslot):
                continue

            # Draw an activity that doesnt already have its max timeslots
            draw = self.draw_uniform_recursive([timeslot], activities, lambda t, a: self.can_assign_timeslot_activity(t, a) and a.course.enrolled_students != 0)  # type: ignore

            if draw:
                activity: Activity = draw[1]  # type: ignore
                schedule.connect_nodes(activity, timeslot)

    def assign_students_timeslots(self, schedule: Schedule, i_max=10000, method="uniform"):
        available_activities = list(schedule.activities.values())

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

            # No available students means this activity has been assigned to all its students, it's finished.
            if len(available_students_linked) == 0:
                # Remove activity from available activities
                for index, test_activity in enumerate(available_activities):
                    if activity == test_activity:
                        available_activities.pop(index)
                # Remove local index
                delattr(activity, "_unassigned_students")
                continue

            # Pick student that does not have a timeslot for this activity
            student = random.choice(available_students_linked)

            timeslots_linked = list(activity.timeslots.values())

            # TODO: #30 improvement would be to first see if there is an available timeslot for student, but it wouldn't necessarily be uniform (see commented code)
            draw_timeslot = None
            match method:
                case "min_overlap":
                    draw_timeslot = self.draw_uniform_recursive(
                        [student],
                        timeslots_linked,
                        lambda s, t: self.can_assign_student_timeslot(s, t) and not self.node_has_period(s, t),
                    )
                case "min_gaps":
                    for limit in range(1, 4):
                        draw_timeslot = self.draw_uniform_recursive(
                            [student],
                            timeslots_linked,
                            lambda s, t: self.can_assign_student_timeslot(s, t)
                            and not self.timeslot_gives_gaps(s, t, limit=limit),
                        )
                        if draw_timeslot:
                            break
                case "min_gaps_overlap":
                    # Give priority to absence of gaps, then to overlap

                    # Try meeting requirements: no overlap AND no gap of size `limit` for increasing limit
                    for limit in range(1, 4):
                        draw_timeslot = self.draw_uniform_recursive(
                            [student],
                            timeslots_linked,
                            lambda s, t: self.can_assign_student_timeslot(s, t)
                            and not self.node_has_period(s, t)
                            and not self.timeslot_gives_gaps(s, t, limit=limit),
                        )
                        if draw_timeslot:
                            break

                    # If failed, try meeting requirements: no gaps of size `limit` for increasing limit
                    if not draw_timeslot:
                        for limit in range(1, 4):
                            draw_timeslot = self.draw_uniform_recursive(
                                [student],
                                timeslots_linked,
                                lambda s, t: self.can_assign_student_timeslot(s, t)
                                and not self.timeslot_gives_gaps(s, t, limit=limit),
                            )
                            if draw_timeslot:
                                break

                    # If still failed, try meeting requirement: no overlap
                    if not draw_timeslot:
                        draw_timeslot = self.draw_uniform_recursive(
                            [student],
                            timeslots_linked,
                            lambda s, t: self.can_assign_student_timeslot(s, t) and not self.node_has_period(s, t),
                        )

                    # If still failed, just draw a random available timeslot
                case _:
                    draw_timeslot = None
            # Draw a random timeslot if method="uniform" or if method's restrictions did not result in a succesful draw.
            if not draw_timeslot:
                draw_timeslot = self.draw_uniform_recursive(
                    [student], timeslots_linked, self.can_assign_student_timeslot
                )

            if not draw_timeslot:
                if self.verbose:
                    warn(f"ERROR: Could no longer find available timeslots for {activity} after {i} iterations.")
                continue
            timeslot = draw_timeslot[1]

            # Skip if timeslot is already linked to student
            edge = (student.id, timeslot.id)
            if edge in edges:
                if self.verbose:
                    warn("ERROR: attempted adding same edge twice.")
                continue

            # Success: found a pair of student, timeslot that meet all requirements and can be booked
            schedule.connect_nodes(student, timeslot)
            # Remove student from index of unassigned students for this activity
            getattr(activity, "_unassigned_students").remove(student)
        activities_finished = len(available_activities) == 0

        if not activities_finished:
            if self.verbose:
                warn(
                    f"ERROR: could not finish schedule within {i_max} iterations. Unfinished activities: {available_activities}"
                )
            # TODO: #31 reassign timeslots with no connected students and try again (allowed to ignore non uniform redraw to permit solution)

        # Return Result
        return Result(schedule=schedule, iterations=i_max, solved=activities_finished)

    def solve(self, schedule: Schedule | None = None, i_max: int | None = None, method=None, strict=True):
        if schedule is None:
            schedule = make_prototype(self.students_input, self.courses_input, self.rooms_input)

        if method is None:
            method = self.method

        assert method in ["uniform", "min_gaps", "min_overlap", "min_gaps_overlap", "min_overlap_gaps"]

        if i_max is None:
            # Program on average has to iterate over each activity once, which with a random distribution it takes more iterations
            i_min = 1000 * len(schedule.activities)
            guess_required_edges = 0
            for activity in schedule.activities.values():
                guess_required_edges += activity.enrolled_students
            i_max = max(guess_required_edges, i_min)

        # First make sure each activity has a timeslot
        self.assign_activities_timeslots_once(schedule)
        # Divide leftover timeslots over activities
        self.assign_activities_timeslots_uniform(schedule)

        return self.assign_students_timeslots(schedule, i_max, method=method)


# TODO try sudoku algorithm