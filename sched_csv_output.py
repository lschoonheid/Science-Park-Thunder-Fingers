"""Output for schedule in .csv file"""

import csv
import random
from code.classes.schedule import Schedule
from code.classes.student import Student


def schedule_to_csv(schedule: Schedule, output_path: str = "output/Schedule_output.csv"):
    """Interface for executing scheduling program."""
    # link random course to random room
    # schedule.connect_nodes(random.choice(list(schedule.courses)), random.choice(list(schedule.rooms)))

    # 'dag', 'tijdslot' add when implemented elsewhere
    field_names = ["student", "vak", "activiteit", "zaal", "dag", "tijdslot"]

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for student in schedule.students.values():
            for activity in student.activities.values():
                for timeslot in student.timeslots.values():
                    data = [
                        student.name,
                        activity.course.name,
                        activity.type,
                        timeslot.room.name,
                        timeslot.day_names[timeslot.day],
                        timeslot.period_names[timeslot.period],
                    ]
                    writer.writerow(data)

        # # extract students
        # students = [student.name for student in schedule.students.values()]
        # # extract courses
        # student_courses = [student.courses for student in schedule.students.values()]
        # # extract activities
        # course_activities = [course.activities for course in schedule.courses.values()]
        # # extract rooms
        # all_rooms = list(schedule.rooms.values())

        # for i in range(4):
        #     ran_course = random.choice(list(student_courses[i].values()))
        #     data = [
        #         students[i],
        #         ran_course.name,
        #         random.choice(list(ran_course.activities.values())).type,
        #         random.choice(all_rooms).name,
        #     ]
        #     writer.writerow(data)


if __name__ == "__main__":
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv"
    courses_path: str = "data/vakken_subset.csv"
    rooms_path: str = "data/zalen.csv"

    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)

    schedule_to_csv(schedule)
