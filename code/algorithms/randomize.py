from ..classes.schedule import Schedule
from ..classes.student import Student
from ..classes.activity import Activity
from ..classes.timeslot import Timeslot
from ..classes.node import Node
from typing import Type, Callable
import random


class Randomize:
    def connect_random(self, schedule: Schedule, i_max: int = 5):
        """Make a completely random schedule"""
        for _ in range(i_max):
            student: Student = random.choice(list(schedule.students.values()))

            activity: Activity = random.choice(list(student.activities.values()))
            timeslot: Timeslot = random.choice(list(schedule.timeslots.values()))
            schedule.connect_nodes(student, timeslot)
            schedule.connect_nodes(activity, timeslot)

    def can_book_student(self, student: Student, timeslot: Timeslot):
        new_moment = (timeslot.day, timeslot.period)
        for booked_timeslot in student.timeslots.values():
            booked_moment = (booked_timeslot.day, booked_timeslot.period)
            if booked_moment == new_moment:
                return False
        return True

    def uniform_strict(self, schedule: Schedule, i_max: int = 200):
        """Make a completely random schedule"""

        # Make shuffled list of timeslots so they will be picked randomly
        timeslots_shuffled = list(schedule.timeslots.values())
        random.shuffle(timeslots_shuffled)

        # Hard constraint to never double book a timeslot, so iterate over them
        for i, timeslot in enumerate(timeslots_shuffled):
            activity: Activity = random.choice(list(schedule.activities.values()))
            schedule.connect_nodes(activity, timeslot)

        # Try making connections for i_max iterations
        for i in range(i_max):
            print("===============================")
            print(i)

            # Choose random timeslot
            timeslot = random.choice(timeslots_shuffled)

            # Should be only one activity
            assert len(timeslot.activities.values()) <= 1, "Hard constraint broken: one activity per timeslot."
            for activity in timeslot.activities.values():
                # Skip if timeslot has reached capacity
                bookings = len(timeslot.students)
                if bookings == activity.capacity or bookings == timeslot.room.capacity:
                    continue

                students = list(activity.students.values())

                # TODO: prevent drawing if student already has assigned timeslot for this

                draw = self.condition_draw_uniform(students, [timeslot], self.can_book_student)  # type: ignore
                if not draw:
                    continue

                student = draw[0]
                schedule.connect_nodes(student, timeslot)

    def condition_draw_uniform(
        self,
        nodes1: list[Node],
        nodes2: list[Node],
        condition: Callable[
            [Node, Node],
            bool,
        ],
        recursion_limit=10,
        _combination_set: set | None = None,
    ):
        assert recursion_limit > 0, "Reached recursion limit"

        # Initialization
        if not _combination_set:
            _combination_set = set()

        max_combinations = len(nodes1) * len(nodes2)

        if len(_combination_set) == max_combinations:
            # Reached all possible combinations
            print("reached all combinations")
            return False

        node1 = random.choice(nodes1)
        node2 = random.choice(nodes2)

        combination = (node1.id, node2.id)
        print(f"comb: {combination}")

        # TODO: Possibly faster to generate all combinations and iterate?
        if combination in _combination_set:
            # Combination already tried, try again with different combination
            return self.condition_draw_uniform(
                nodes1, nodes2, condition, recursion_limit=recursion_limit - 1, _combination_set=_combination_set
            )
        elif not condition(node1, node2):
            _combination_set.add(combination)
            assert len(_combination_set) <= max_combinations
            return self.condition_draw_uniform(
                nodes1, nodes2, condition, recursion_limit=recursion_limit - 1, _combination_set=_combination_set
            )

        return node1, node2
