from ..classes.schedule import Schedule
from ..classes.student import Student
from ..classes.course import Course
from ..classes.activity import Activity
from ..classes.timeslot import Timeslot
import random


def connect_random(schedule: Schedule, i_max: int = 5):
    for i in range(i_max):
        student: Student = random.choice(list(schedule.students.values()))

        activity: Activity = random.choice(list(student.activities.values()))

        timeslot: Timeslot = random.choice(list(schedule.timeslots.values()))
        schedule.connect_nodes(student, timeslot)
        schedule.connect_nodes(activity, timeslot)

        # print(student, activity, timeslot)
