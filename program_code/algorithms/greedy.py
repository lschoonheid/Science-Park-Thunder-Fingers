import random
import operator
from tqdm import tqdm
from typing import Callable
from warnings import warn
from .solver import Solver
from ..classes import *
from ..classes.result import Result

class Greedy(Solver):
    def check_test(self, schedule: Schedule, timeslot: Timeslot):
        timeslots_sorted: list[Timeslot] = self.sort_nodes(schedule.timeslots.values(), "moment")
        timeslots_sorted = self.sort_nodes(timeslots_sorted, "capacity", reverse = True)
        print(timeslot.day)
    
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

    def seperate_activities(self, schedule: Schedule):
        activities = list(schedule.activities.values())

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
        return activities_bound, activities_free

    def assign_hoorcollege_to_room(self, schedule: Schedule):
        # Make shuffled list of timeslots so they will be picked randomly
        timeslots_shuffled = list(schedule.timeslots.values())
        random.shuffle(timeslots_shuffled)

        # Get the seperated hoorcolleges and Werkcolleges en practica activities
        activities_bound, activities_free = self.seperate_activities(schedule)

        # Hard constraint to never double book a timeslot, so iterate over them
        for timeslot in timeslots_shuffled:
            # Skip timeslot if it already has activity
            if self.verifier.node_has_activity(timeslot):
                continue

            # Draw an activity that doesnt already have its max timeslots
            draw = self.draw_uniform_recursive([timeslot], activities_bound, self.verifier.can_assign_timeslot_activity)  # type: ignore

            if draw:
                activities_bound = draw[1]
                schedule.connect_nodes(activities_bound, timeslot)

    def rate_timeslots(self, student: Student, schedule: Schedule):
        new_moment = ()
        for booked_timeslot in student.timeslots.values():
            booked_moment = (booked_timeslot.day, booked_timeslot.period)
            if booked_moment == new_moment:
                return False
        return True