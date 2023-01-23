from .solver import Solver


class Mutations:
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

    # TODO: swap two timeslots of same (room) capacity (in time)
    # TODO: permutate students between activity timeslots
    # TODO: shift timeslot to open timeslot
    # TODO: split timeslot over multiple timeslots (from 1x wc2 -> 2x 2c2)
    # TODO: combine timeslots of same activity to one group/different room

    # TODO: crossover
