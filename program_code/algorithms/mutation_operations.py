"""
Individual part
All functions required for applying employed mutations to schedule.

Student: Laszlo Schoonheid
Course: Algoritmen en Heuristieken 2023
"""

import random
from program_code.algorithms.statistics import Statistics
from program_code.algorithms.randomizer import Randomizer
from program_code.classes.result import Result
from ..classes import NodeSC, Node, Schedule, Timeslot, Student, Activity
from .randomizer import Randomizer
import copy


def fast_swap(node1: Timeslot, node2: Timeslot):
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
            raise NotImplementedError

    # Swap metadata
    node1.__dict__.update(meta2)
    node2.__dict__.update(meta1)
    return node1, node2


def swap_neighbors(
    schedule: Schedule,
    node1: Node | NodeSC,
    node2: Node | NodeSC,
    skip: list[str] | None = None,
):
    """Swap neighbors of `node1` with neighbors of `node2`."""
    assert type(node1) == type(node2), "Can only swap nodes of same type."
    # Define types of neigbors to leave as is
    if not skip:
        skip = []

    # Copy index of both sets of neighbors
    neighbors_1 = copy.copy(node1.neighbors)
    neighbors_2 = copy.copy(node2.neighbors)

    # Disconnect all old eighbors
    for neighbor in neighbors_1.values():
        if type(neighbor).__name__ in skip:
            continue
        schedule.disconnect_nodes(node1, neighbor)
    for neighbor in neighbors_2.values():
        if type(neighbor).__name__ in skip:
            continue
        schedule.disconnect_nodes(node2, neighbor)

    # Connect all new neighbors
    for neighbor in neighbors_1.values():
        if type(neighbor).__name__ in skip:
            continue
        schedule.connect_nodes(node2, neighbor)
    for neighbor in neighbors_2.values():
        if type(neighbor).__name__ in skip:
            continue
        schedule.connect_nodes(node1, neighbor)


def move_node(schedule: Schedule, node: Student, neighbor1: Timeslot, neighbor2: Timeslot):
    """Move `node` from `neighbor1` to `neighbor2`."""
    schedule.disconnect_nodes(node, neighbor1)
    schedule.connect_nodes(node, neighbor2)


def swap_score_timeslot(result: Result, timeslot1: Timeslot, timeslot2: Timeslot):
    """Get score difference of swapping two timeslots."""
    # Get current score
    current_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)

    # Pretend to swap
    fast_swap(timeslot1, timeslot2)
    # Get projected score
    projected_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)

    # Revert swap
    fast_swap(timeslot1, timeslot2)

    # Return score difference
    diff_sub_score = projected_sub_score - current_sub_score
    return diff_sub_score


def allow_swap_timeslot(result, timeslot1: Timeslot, timeslot2: Timeslot, score_ceiling=None):
    """Assumes timeslots are already legally assigned."""

    # Cannot swap with itself
    if timeslot1 is timeslot2:
        return False

    # Check whether enough capacity is available for swap
    if timeslot1.room.capacity < timeslot2.enrolled_students:
        return False
    if timeslot2.room.capacity < timeslot1.enrolled_students:
        return False

    # Check for possible booking during lecture
    # Check whether timeslot is already taken by a lecture of the same course, or others if self is lecture
    if timeslot1.moment != timeslot2.moment:
        for activity1 in timeslot1.activities.values():
            if activity1.max_timeslots:
                # Activity 1 is bound, it may not coincide with any activity of same course
                for bound_activity1 in activity1.course.activities.values():
                    if Statistics.node_has_period(bound_activity1, timeslot2):
                        return False
            else:
                # Activity 1 is unbound, it may not coincide with lectures of same course
                for bound_activity1 in activity1.course.bound_activities.values():
                    if Statistics.node_has_period(bound_activity1, timeslot2):
                        return False
        for activity2 in timeslot2.activities.values():
            if activity2.max_timeslots:
                # Activity 2 is bound, it may not coincide with any activity of same course
                for bound_activity2 in activity2.course.activities.values():
                    if Statistics.node_has_period(bound_activity2, timeslot1):
                        return False
            else:
                # Activity 2 is unbound, it may not coincide with lectures of same course
                for bound_activity2 in activity2.course.bound_activities.values():
                    if Statistics.node_has_period(bound_activity2, timeslot1):
                        return False

    if score_ceiling is None:
        if timeslot1.room.capacity == timeslot2.room.capacity:
            return True
        if timeslot1.capacity == timeslot2.capacity:
            return True

    # Check wether swap would be enough of an improvement
    swap_score = swap_score_timeslot(result, timeslot1, timeslot2)
    if swap_score <= score_ceiling:
        return swap_score
    return False


def draw_valid_timeslot_swap(
    result: Result,
    timeslots: list[Timeslot],
    tried_swaps: set | None = None,
    ceiling: int | float | None = None,
):
    """Draw a valid swap. Finds swap that meets requirements of `allow_swap_timeslot`."""
    draw = Randomizer.draw_uniform(
        timeslots,
        timeslots,
        lambda t1, t2: allow_swap_timeslot(result, t1, t2, score_ceiling=ceiling),
        return_value=True,
        _combination_set=tried_swaps,
    )
    if not draw:
        return None
    tA, tB, score = draw  # type: ignore

    # Return tuple of swap and score
    return (tA, tB), score


def get_swap_scores_timeslot(
    result: Result, scope: int, tried_swaps: set[tuple[int, int]], ceiling: int | float | None = 0
):
    """Get scores differences for `scope` possible swaps."""
    swap_scores: dict[tuple[Timeslot, Timeslot], int | float] = {}
    timeslots = list(result.schedule.timeslots.values())
    for i in range(scope):
        draw = draw_valid_timeslot_swap(result, timeslots, tried_swaps, ceiling)

        if not draw:
            break

        # Found allowed swap,
        (tA, tB), score = draw
        # Sort by id so combination is unique
        t1, t2 = sorted([tA, tB], key=lambda t: t.id)
        tried_swaps.add((t1.id, t2.id))

        swap_scores[(t1, t2)] = score
    return swap_scores


def swap_random_timeslots(result: Result, tried_swaps: set | None = None):
    """Swap two timeslots at random, if allowed."""
    timeslots = list(result.schedule.timeslots.values())

    # Draw a pair of timeslots that can be swapped
    draw = draw_valid_timeslot_swap(result, timeslots, tried_swaps)

    if not draw:
        return None

    # Found pair
    (node1, node2), score = draw

    # Apply swap
    swap_neighbors(result.schedule, node1, node2, skip=["Room"])
    return draw


def move_score_student(result: Result, student: Student, timeslot1: Timeslot, timeslot2: Timeslot):
    """Calculate score difference for moving student from `timeslot1` to `timeslot2`."""
    # Get current score
    current_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)
    if timeslot1.period == 4 and timeslot1.enrolled_students == 1:
        # Virtually emptied evening timeslot, remove penalty
        current_sub_score += result.score_matrix.dot([1, 0, 0, 0, 0])

    # Pretend to swap
    move_node(result.schedule, student, timeslot1, timeslot2)

    # Get projected score
    projected_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)

    # Revert move
    move_node(result.schedule, student, timeslot2, timeslot1)

    # Calculate difference
    diff_sub_score = projected_sub_score - current_sub_score
    return diff_sub_score


def allow_move_student(
    result: Result,
    student: Student,
    timeslot1: Timeslot,
    timeslot2: Timeslot,
    score_ceiling=None,
):
    """Check wether moving student to timeslot is allowed."""
    if timeslot1 is timeslot2:
        return False

    # Check timeslot2 has enough capacity
    if timeslot2.enrolled_students >= timeslot2.capacity:
        return False

    # Check wether swap would be improvement
    swap_score = move_score_student(result, student, timeslot1, timeslot2)
    if score_ceiling and swap_score > score_ceiling:
        return False
    return swap_score


def draw_valid_student_move(
    result: Result,
    timeslots: list[Timeslot],
    tried_swaps: set | None = None,
    ceiling: int | float | None = None,
):
    """Draw a valid move of node `student` from `timeslot1` to `timeslot2`."""
    timeslot1 = random.choice(timeslots)
    # If current timeslot has no students to move, retry
    if timeslot1.enrolled_students == 0:
        return draw_valid_student_move(result, timeslots, tried_swaps)

    # Assuming hard constraint timeslot only has 1 activity
    activity: Activity = list(timeslot1.activities.values())[0]

    # Check timeslot2 has enough capacity
    draw = Randomizer.draw_uniform(
        list(timeslot1.students.values()),
        list(activity.timeslots.values()),
        lambda s, t2: allow_move_student(result, s, timeslot1, t2, ceiling),  # type: ignore
        return_value=True,
        symmetric_condition=False,
        _combination_set=tried_swaps,
    )

    # Retry
    if not draw:
        return draw_valid_student_move(result, timeslots, tried_swaps, ceiling)

    # Succesful
    student, timeslot2, score = draw  # type: ignore
    return (student, timeslot1, timeslot2), score


def swap_students_timeslots(
    schedule: Schedule,
    student1: Student,
    student2: Student,
    timeslot1: Timeslot,
    timeslot2: Timeslot,
):
    """Swap students between two timeslots."""
    schedule.disconnect_nodes(student1, timeslot1)
    schedule.disconnect_nodes(student2, timeslot2)
    schedule.connect_nodes(student1, timeslot2)
    schedule.connect_nodes(student2, timeslot1)


def swap_score_student(
    result: Result,
    student1: Student,
    student2: Student,
    timeslot1: Timeslot,
    timeslot2: Timeslot,
):
    """Calculate score difference for swapping `student1` and `student2` between `timeslot1` and `timeslot2`."""
    # Get current score
    current_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)

    # Try swap
    swap_students_timeslots(result.schedule, student1, student2, timeslot1, timeslot2)

    # Calculate projected score
    projected_sub_score = result.sub_score(timeslot1) + result.sub_score(timeslot2)

    # Revert swap
    swap_students_timeslots(result.schedule, student1, student2, timeslot2, timeslot1)

    # Calculate difference
    diff_sub_score = projected_sub_score - current_sub_score
    return diff_sub_score


def allow_swap_student(
    result: Result,
    student1: Student,
    student2: Student,
    timeslot1: Timeslot,
    timeslot2: Timeslot,
    ceiling: int | float | None = None,
):
    """Verify whether swapping students is allowed."""
    if timeslot1 is timeslot2:
        return False

    # Cannot swap from empty list of students
    if timeslot1.enrolled_students == 0 or timeslot2.enrolled_students == 0:
        return False

    # Can only swap in timeslots of same activity
    if list(timeslot1.activities.values())[0] != list(timeslot2.activities.values())[0]:
        return False

    # Check what score difference swap would make
    swap_score = swap_score_student(result, student1, student2, timeslot1, timeslot2)
    if ceiling is not None and swap_score > ceiling:
        return False
    return swap_score


def draw_valid_student_swap(
    result: Result,
    timeslots: list[Timeslot],
    tried_swaps: set | None = None,
    ceiling: int | float | None = None,
):
    """Draw a valid swap of two students."""
    timeslot1 = random.choice(timeslots)

    # Assuming hard constraint timeslot only has 1 activity
    activity: Activity = list(timeslot1.activities.values())[0]

    # Check wether another timeslot for activity and a student for swap are available
    if activity.timeslots.values() == 1 or timeslot1.enrolled_students == 0:
        return draw_valid_student_swap(result, timeslots, tried_swaps, ceiling)

    # Pick a second timeslot to swap students with
    timeslot2 = random.choice(list(activity.timeslots.values()))
    if timeslot2 is timeslot1:
        return draw_valid_student_swap(result, timeslots, tried_swaps, ceiling)

    # Find students available for swap
    draw = Randomizer.draw_uniform(
        list(timeslot1.students.values()),
        list(timeslot2.students.values()),
        lambda s1, s2: allow_swap_student(result, s1, s2, timeslot1, timeslot2, ceiling),  # type: ignore
        return_value=True,
        _combination_set=tried_swaps,
    )

    # Retry
    if not draw:
        return draw_valid_student_swap(result, timeslots, tried_swaps, ceiling)

    # Succesful
    student1, student2, score = draw  # type: ignore
    return (student1, student2, timeslot1, timeslot2), score
