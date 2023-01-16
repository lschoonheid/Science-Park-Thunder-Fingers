"""Output for schedule in .csv file"""

import csv
import random
# from ..modules.helpers import csv_to_dicts
from code.classes.schedule import Schedule

def main(
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv",
    courses_path: str = "data/vakken_subset.csv",
    rooms_path: str = "data/zalen.csv",
):
    """Interface for executing scheduling program."""

    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)

    #link random course to random room
    # first_test_output = schedule.connect_nodes(random.choice(list(schedule.courses)), random.choice(list(schedule.rooms)))

    # 'activiteit', , 'dag', 'tijdslot' add when implemented elsewhere
    field_names = ['student', 'vak', 'zaal']


    print(schedule.nodes)

    with open('output/Schedule_output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data

        # extract students
        studenten = [student.name for student in schedule.students.values()]
        # extract courses
        student_courses = [student.courses for student in schedule.students.values()]
        # extract rooms
        all_rooms = list(schedule.rooms.values())

        for i in range(4):
            data = [studenten[i],random.choice(list(student_courses[i].values())), random.choice(all_rooms)]
            writer.writerow(data)


if __name__ == "__main__":
    main()
