"""
Individual part
Class for general mutation that can be applied to schedule.

Student: Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""


from typing import Callable

from program_code.algorithms.mutation_operations import (
    draw_valid_student_move,
    draw_valid_student_swap,
    draw_valid_timeslot_swap,
    move_node,
    swap_neighbors,
    swap_students_timeslots,
)
from ..classes.result import Result


class Mutation:
    """General mutations class. Finds available mutation, calculates score and returns operator to be applied."""

    def __init__(
        self,
        action: Callable,
        drawer: Callable,
        result: Result,
        targets: list,
        ceiling: int | None = None,
        tried_mutations: set | None = None,
        arguments: dict | None = None,
        inverse: Callable | None = None,
    ):
        self.type = action.__name__
        # Mutation to apply
        self.action = action
        self.inverse = inverse
        # Parent schedule to calculate score
        self.result = result
        # Arguments for mutation
        self.arguments = arguments

        # Draw available mutation
        draw = drawer(result, targets, tried_mutations, ceiling)
        if draw:
            self.subjects, self.score = draw

    def apply(self):
        """Apply mutation to schedule."""
        if self.arguments:
            return self.action(self.result.schedule, *self.subjects, **self.arguments)
        return self.action(self.result.schedule, *self.subjects)

    def revert(self):
        """Revert mutation."""
        if self.inverse:
            if self.arguments:
                return self.inverse(self.result.schedule, *self.subjects, **self.arguments)
            return self.inverse(self.result.schedule, *self.subjects)

        raise NotImplementedError


class MoveStudent(Mutation):
    """Mutation that moves student from one timeslot to another."""

    def __init__(
        self,
        result: Result,
        targets: list,
        ceiling: int | None = None,
        tried_mutations: set | None = None,
    ):
        super().__init__(move_node, draw_valid_student_move, result, targets, ceiling, tried_mutations)


class SwapStudents(Mutation):
    """Mutation that swaps two students between two timeslots."""

    def __init__(
        self,
        result: Result,
        targets: list,
        ceiling: int | None = None,
        tried_mutations: set | None = None,
        arguments: dict | None = None,
        inverse: Callable | None = None,
    ):
        super().__init__(
            swap_students_timeslots,
            draw_valid_student_swap,
            result,
            targets,
            ceiling,
            tried_mutations,
            arguments,
            inverse,
        )


class SwapTimeslots(Mutation):
    """Mutation that swaps two timeslots."""

    def __init__(
        self,
        result: Result,
        targets: list,
        ceiling: int | None = None,
        tried_mutations: set | None = None,
    ):
        super().__init__(
            swap_neighbors, draw_valid_timeslot_swap, result, targets, ceiling, tried_mutations, {"skip": "Room"}
        )
