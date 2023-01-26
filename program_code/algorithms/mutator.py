import warnings
from program_code.classes.result import Result
from .solver import Solver
from ..classes import NodeSC, Node, Schedule, Timeslot
from .randomizer import Randomizer
import copy


class Mutator(Randomizer):
    # TODO implement for all node types
    def fast_swap(self, node1: Timeslot, node2: Timeslot):
        """Only swap metadata; virtual swap."""
        assert type(node1) == type(node2), "Can only swap nodes of same type."
        match type(node1).__name__:
            case "Timeslot":
                meta1 = {
                    "id": node1.id,
                    "day": node1.day,
                    "period": node1.period,
                    "moment": node1.moment,
                }
                meta2 = {
                    "id": node2.id,
                    "day": node2.day,
                    "period": node2.period,
                    "moment": node2.moment,
                }
            case _:
                warnings.warn("fast_swap not implemented for this node type.")
                return
        node1.__dict__.update(meta2)
        node2.__dict__.update(meta1)
        return node1, node2

    def swap_neighbors(
        self,
        schedule: Schedule,
        node1: Node | NodeSC,
        node2: Node | NodeSC,
        skip: list[str] | None = None,
    ):
        assert type(node1) == type(node2), "Can only swap nodes of same type."
        if not skip:
            skip = []

        neighbors_1 = copy.copy(node1.neighbors)
        neighbors_2 = copy.copy(node2.neighbors)

        solved_before = Result(schedule).check_solved()
        if not solved_before:
            pass

        # Disconnect all neighbors
        for neighbor in neighbors_1.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.disconnect_nodes(node1, neighbor)
        for neighbor in neighbors_2.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.disconnect_nodes(node2, neighbor)

        # Connect all neighbors
        for neighbor in neighbors_1.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.connect_nodes(node2, neighbor)
        for neighbor in neighbors_2.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.connect_nodes(node1, neighbor)

    def allow_swap_timeslot(self, result, timeslot1: Timeslot, timeslot2: Timeslot, score_ceiling=None):
        """Assumes timeslots are already legally assigned."""
        # For timeslot swap:
        # TODO: Check capacity is still valid
        # TODO: #44 constraint relaxation for local minima

        # Cannot swap with itself
        if timeslot1 is timeslot2:
            return False

        # Check for possible booking during lecture
        # Check whether timeslot is already taken by a lecture of the same course, or others if self is lecture
        if timeslot1.moment != timeslot2.moment:
            for activity1 in timeslot1.activities.values():
                if activity1.max_timeslots:
                    # Activity 1 is bound, it may not coincide with any activity of same course
                    for bound_activity1 in activity1.course.activities.values():
                        if self.node_has_period(bound_activity1, timeslot2):
                            return False
                else:
                    # Activity 1 is unbound, it may not coincide with lectures of same course
                    for bound_activity1 in activity1.course.bound_activities.values():
                        if self.node_has_period(bound_activity1, timeslot2):
                            return False
            for activity2 in timeslot2.activities.values():
                if activity2.max_timeslots:
                    # Activity 2 is bound, it may not coincide with any activity of same course
                    for bound_activity2 in activity2.course.activities.values():
                        if self.node_has_period(bound_activity2, timeslot1):
                            return False
                else:
                    # Activity 2 is unbound, it may not coincide with lectures of same course
                    for bound_activity2 in activity2.course.bound_activities.values():
                        if self.node_has_period(bound_activity2, timeslot1):
                            return False

        if score_ceiling is None:
            if timeslot1.room.capacity == timeslot2.room.capacity:
                return True
            if timeslot1.capacity == timeslot2.capacity:
                return True

        if timeslot1.room.capacity < timeslot2.enrolled_students:
            return False
        if timeslot2.room.capacity < timeslot1.enrolled_students:
            return False

        # Check wether swap would be improvement
        swap_score = self.swap_score_timeslot(result, timeslot1, timeslot2)
        if swap_score <= score_ceiling:
            return swap_score
        return False

    def swap_score_timeslot(self, result: Result, timeslot1: Timeslot, timeslot2: Timeslot):
        """Get score difference of swapping two timeslots."""
        # TODO: constraint relaxation for local minimas

        # Get current score
        current_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)
        # Pretend to swap
        self.fast_swap(timeslot1, timeslot2)
        # Get projected score
        projected_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)
        diff_sub_score = projected_sub_score - current_sub_score
        self.fast_swap(timeslot1, timeslot2)

        return diff_sub_score

    def draw_valid_timeslot_swap(
        self,
        result: Result,
        timeslots: list[Timeslot],
        tried_swaps: set[tuple[int, int]],
        ceiling: int | float | None = 0,
    ):
        """Draw a valid swap."""
        draw = self.draw_uniform_recursive(
            timeslots,
            timeslots,
            lambda t1, t2: self.allow_swap_timeslot(result, t1, t2, score_ceiling=ceiling),
            return_value=True,
            # TODO: remember illegal swaps in between tries
            _combination_set=tried_swaps,
        )  # type: ignore
        if not draw:
            return None
        tA, tB, score = draw  # type: ignore

        # Sort by id, make sure swap_scores has no duplicates
        id1, id2 = sorted([tA.id, tB.id])
        return (id1, id2), score

    def get_swap_scores_timeslot(
        self, result: Result, scope: int, tried_swaps: set[tuple[int, int]], ceiling: int | float | None = 0
    ):
        """Get scores differences for `scope` possible swaps."""
        swap_scores: dict[tuple[int, int], int | float] = {}
        timeslots = list(result.schedule.timeslots.values())
        for i in range(scope):
            draw = self.draw_valid_timeslot_swap(result, timeslots, tried_swaps, ceiling)
            if not draw:
                break
            (id1, id2), score = draw
            if ceiling is not None and score > ceiling:
                continue

            swap_scores[(id1, id2)] = score
        return swap_scores

    def swap_random_timeslots(self, result: Result, tried_swaps: set | None = None):
        """Swap two timeslots at random, if allowed."""
        timeslots = list(result.schedule.timeslots.values())
        # TODO: steepest decent, try 100 swaps and see which were most effective
        draw = self.draw_valid_timeslot_swap(result, timeslots, tried_swaps or set())
        if not draw:
            return None
        (id1, id2), score = draw  # type: ignore

        nodes = result.schedule.timeslots
        self.swap_neighbors(result.schedule, nodes[id1], nodes[id1], skip=["Room"])

        # TODO remove TEST
        # if not Result(schedule).check_solved():
        #     self.swap_neighbors(schedule, *draw, skip=["Room"])
        #     self.allow_swap_timeslot(*draw)
        #     self.swap_neighbors(schedule, *draw, skip=["Room"])
        return draw

    # TODO: swap two timeslots of same (room) capacity (in time)
    # TODO: check legal/illegal timeslot/room swaps
    # TODO: permutate students between activity timeslots
    # TODO: shift timeslot to open timeslot
    # TODO: split timeslot over multiple timeslots (from 1x wc2 -> 2x 2c2)
    # TODO: combine timeslots of same activity to one group/different room

    # TODO: crossover
