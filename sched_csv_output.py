"""Output for schedule in .csv file"""

import csv
import random
from code.classes.schedule import Schedule

def main(
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv",
    courses_path: str = "data/vakken_subset.csv",
    rooms_path: str = "data/zalen.csv",
):
    """Interface for executing scheduling program."""

    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)

    # link random course to random room
    # schedule.connect_nodes(random.choice(list(schedule.courses)), random.choice(list(schedule.rooms)))

    # 'dag', 'tijdslot' add when implemented elsewhere
    field_names = ['student', 'vak', 'activiteit', 'zaal']

    with open('output/Schedule_output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data

        # extract students
        studenten = [student.name for student in schedule.students.values()]
        # extract courses
        student_courses = [student.courses for student in schedule.students.values()]
        # extract activities
        course_activities = [course.activities for course in schedule.courses.values()]
        # extract rooms
        all_rooms = list(schedule.rooms.values())

        for i in range(4):
            ran_course = random.choice(list(student_courses[i].values()))
            data = [studenten[i],ran_course.name, random.choice(list(ran_course.activities.values())).type, random.choice(all_rooms).name]
            writer.writerow(data)


if __name__ == "__main__":
    main()
