from .solver import Solver
from ..classes import NodeSC, Node, Schedule, Timeslot
from .randomize import Randomize
import copy


class Mutations(Randomize):
    def __init__(
        self,
        numberOfCrossoverPoints=2,
        mutationSize=2,
        crossoverProbability=80,
        mutationProbability=3,
    ):
        self.mutationSize = mutationSize
        self.numberOfCrossoverPoints = numberOfCrossoverPoints
        self.crossoverProbability = crossoverProbability
        self.mutationProbability = mutationProbability

    def fast_swap(self, node1: Node | NodeSC, nodes2: Node | NodeSC):
        """Only swap metadata; virtual swap."""
        pass

    def swap_neighbors(
        self,
        schedule: Schedule,
        node1: Node | NodeSC,
        node2: Node | NodeSC,
        skip: list[str] | None = None,
    ):
        if not skip:
            skip = []

        neighbors_1 = copy.copy(node1.neighbors)
        neighbors_2 = copy.copy(node2.neighbors)

        for neighbor in neighbors_1.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.disconnect_nodes(node1, neighbor)
            schedule.connect_nodes(node2, neighbor)

        for neighbor in neighbors_2.values():
            if type(neighbor).__name__ in skip:
                continue
            schedule.disconnect_nodes(node2, neighbor)
            schedule.connect_nodes(node1, neighbor)

    def allow_timeslot_swap(self, timeslot1: Timeslot, timeslot2: Timeslot):
        """Assumes timeslots are already legally assigned."""
        # For timeslot swap:
        # TODO: Check capacity is still valid

        if timeslot1 is timeslot2:
            return False

        if timeslot1.room.capacity == timeslot2.room.capacity:
            return True
        if timeslot1.capacity == timeslot2.capacity:
            return True

        if timeslot1.room.capacity < timeslot2.enrolled_students:
            return False
        if timeslot2.room.capacity < timeslot1.enrolled_students:
            return False

        return True

    def swap_random_timeslots(self, schedule: Schedule):
        """Swap two timeslots at random, if allowed."""
        timeslots = list(schedule.timeslots.values())
        draw = self.draw_uniform_recursive(timeslots, timeslots, self.allow_timeslot_swap)  # type: ignore
        if not draw:
            return None

        self.swap_neighbors(schedule, *draw, skip=["Room"])
        return draw

    # TODO: swap two timeslots of same (room) capacity (in time)
    # TODO: check legal/illegal timeslot/room swaps
    # TODO: permutate students between activity timeslots
    # TODO: shift timeslot to open timeslot
    # TODO: split timeslot over multiple timeslots (from 1x wc2 -> 2x 2c2)
    # TODO: combine timeslots of same activity to one group/different room

    # TODO: crossover
