"""Output for schedule in .csv file"""

import csv
from program_code import Data, Schedule, prepare_path


def schedule_to_csv(schedule: Schedule, output_path: str = "output/Schedule_output.csv"):
    """Interface for executing scheduling program."""
    # link random course to random room
    # schedule.connect_nodes(random.choice(list(schedule.courses)), random.choice(list(schedule.rooms)))

    # 'dag', 'tijdslot' add when implemented elsewhere
    field_names = ["student", "vak", "activiteit", "zaal", "dag", "tijdslot"]

    prepare_path(output_path)

    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)

        # write the header
        writer.writerow(field_names)

        # write the data
        for student in schedule.students.values():
            for timeslot in student.timeslots.values():
                for activity in timeslot.activities.values():
                    data = [
                        student.name,
                        activity.course.name,
                        activity.act_type,
                        timeslot.room.name,
                        timeslot.day_names[timeslot.day],
                        timeslot.period_names[timeslot.period],
                    ]
                    writer.writerow(data)

        print(f"output saved to {output_path}")


if __name__ == "__main__":
    stud_prefs_path: str = "data/studenten_en_vakken_subset.csv"
    courses_path: str = "data/vakken_subset.csv"
    rooms_path: str = "data/zalen.csv"

    input_data = Data(stud_prefs_path, courses_path, rooms_path)

    students_input = input_data.students
    courses_input = input_data.courses
    rooms_input = input_data.rooms

    schedule = Schedule(students_input, courses_input, rooms_input)

    schedule_to_csv(schedule)
