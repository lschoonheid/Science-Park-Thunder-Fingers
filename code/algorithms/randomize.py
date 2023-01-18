from ..classes.schedule import Schedule
from ..classes.student import Student
from ..classes.activity import Activity
from ..classes.timeslot import Timeslot
from ..classes.node import Node
import random
from tqdm import tqdm
from typing import Callable

# TODO: move constraint checks to Objective
class Randomize:
    def connect_random(self, schedule: Schedule, i_max: int = 5):
        """Make a completely random schedule"""
        for _ in range(i_max):
            student: Student = random.choice(list(schedule.students.values()))

            activity: Activity = random.choice(list(student.activities.values()))
            timeslot: Timeslot = random.choice(list(schedule.timeslots.values()))
            schedule.connect_nodes(student, timeslot)
            schedule.connect_nodes(activity, timeslot)

    def timeslot_has_activity(self, timeslot: Timeslot):
        if len(timeslot.activities) > 0:
            return True
        return False

    def can_book_student(self, student: Student, timeslot: Timeslot):
        new_moment = (timeslot.day, timeslot.period)
        for booked_timeslot in student.timeslots.values():
            booked_moment = (booked_timeslot.day, booked_timeslot.period)
            if booked_moment == new_moment:
                return False
        return True

    def student_has_activity_assigned(self, student: Student, activity: Activity):
        for assigned_slot in student.timeslots.values():
            for activity_timeslot in activity.timeslots.values():
                if assigned_slot.id == activity_timeslot.id:
                    # Student already has assigned timeslot for activity
                    return True
        # print(student, activity)
        return False

    def draw_uniform_recursive(
        self,
        nodes1: list[Node],
        nodes2: list[Node],
        condition: Callable[
            [Node, Node],
            bool,
        ],
        negation=False,
        _recursion_limit=10000,
        _combination_set: set | None = None,
    ):
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
                nodes1, nodes2, condition, _recursion_limit=_recursion_limit - 1, _combination_set=_combination_set
            )
        elif not condition_value:
            _combination_set.add(combination)
            assert len(_combination_set) <= max_combinations, "Combination set out of order"

            return self.draw_uniform_recursive(
                nodes1, nodes2, condition, _recursion_limit=_recursion_limit - 1, _combination_set=_combination_set
            )

        # print(f"found condition: {condition_value} for{node1, node2} with {_recursion_limit} recursions left")
        return node1, node2

    def assign_activities_timeslots_once(self, schedule: Schedule):
        # Make shuffled list of timeslots so they will be picked randomly
        activities_shuffled = list(schedule.activities.values())
        random.shuffle(activities_shuffled)
        timelots = list(schedule.timeslots.values())
        for activity in activities_shuffled:
            draw = self.draw_uniform_recursive([activity], timelots, lambda a, t: self.timeslot_has_activity(t), negation=True)  # type: ignore
            if draw:
                timeslot = draw[1]
                schedule.connect_nodes(activity, timeslot)

    def assign_activities_timeslots_uniform(self, schedule: Schedule):
        # Make shuffled list of timeslots so they will be picked randomly
        timeslots_shuffled = list(schedule.timeslots.values())
        random.shuffle(timeslots_shuffled)

        # Hard constraint to never double book a timeslot, so iterate over them
        for timeslot in timeslots_shuffled:
            activity: Activity = random.choice(list(schedule.activities.values()))
            schedule.connect_nodes(activity, timeslot)

    def assign_students_timeslots(self, schedule: Schedule, i_max=1000):
        available_activities = list(schedule.activities.values())

        # Try making connections for i_max iterations
        edges = set()
        for i in tqdm(range(i_max)):
            # print(i)
            if len(available_activities) == 0:
                print("Finished!")
                break

            # Take random unfinished activity
            activity = random.choice(available_activities)

            students_linked = list(activity.students.values())
            timeslots_linked = list(activity.timeslots.values())

            # Filter timeslots for available capacity
            timeslots_available: list[Timeslot] = []
            for timeslot in timeslots_linked:
                # Skip if timeslot has reached capacity
                bookings = len(timeslot.students)
                if bookings == activity.capacity or bookings == timeslot.room.capacity:
                    continue
                timeslots_available.append(timeslot)

            if len(timeslots_available) == 0:
                print(f"ERROR: Could no longer find available timeslots for {activity} after {i} iterations.")
                break

            # TODO: fix this part
            # Pick student that does not have a timeslot for this activity
            draw_student = self.draw_uniform_recursive(
                students_linked, [activity], self.student_has_activity_assigned, negation=True  # type: ignore
            )

            if not draw_student:
                # No available students means this activity has been assigned to all its students, it's finished.
                for index, test_activity in enumerate(available_activities):
                    if activity == test_activity:
                        # TODO: triple check if this is rightfully removed from list, as this brings algorithm closer to completion
                        available_activities.pop(index)
                continue

            student: Student = draw_student[0]  # type: ignore
            # print(student)

            # TODO: improvement would be to first see if there is an available one (see commented code)
            """
            # Pick timeslot that student has still available
            draw_timeslot = self.draw_uniform_recursive([student], timeslots_available, self.can_book_student, negation=False)  # type: ignore

            # if not draw_timeslot:
            #     print(
            #         f"ERROR: Could no longer find available timeslots for {activity} for {student} after {i} iterations."
            #     )
                # TODO: draw anyway as second option
            #     continue
            timeslot: Timeslot = draw_timeslot[1]  # type: ignore

            """

            # student = random.choice(students_linked)
            timeslot = random.choice(timeslots_available)

            # TODO: prevent drawing if student already has assigned timeslot for this
            # TODO: somehow some students still pass this test
            if self.student_has_activity_assigned(student, activity):
                # print("made it through still?")
                continue

            # Skip if timeslot is already linked to student
            edge = (student.id, timeslot.id)
            if edge in edges:
                # print("made it through?")
                continue

            # Success
            schedule.connect_nodes(student, timeslot)
            edges.add(edge)
        if len(available_activities) > 0:
            print(f"ERROR: could not finish schedule within {i_max} iterations.")
            print(f"ERROR: unfinished activities: {available_activities}")
            return False
        return True

    def uniform_strict(self, schedule: Schedule, i_max: int = 1000):
        """Make a completely random schedule solution"""

        self.assign_activities_timeslots_once(schedule)
        # TODO Check if each activity has at least one timeslot

        got_solution = self.assign_students_timeslots(schedule, i_max)
        # if not got_solution:
        #     self.uniform_strict(schedule, i_max)
        return got_solution


# TODO try pseudo-ku algorithm
