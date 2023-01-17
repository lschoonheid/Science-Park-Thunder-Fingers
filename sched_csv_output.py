"""Output for schedule in .csv file"""

import csv
from code.classes.schedule import Schedule


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
            for timeslot in student.timeslots.values():
                for activity in timeslot.activities.values():
                    for course in activity.courses.values():
                        data = [
                            student.name,
                            course.name,
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

    schedule = Schedule(stud_prefs_path, courses_path, rooms_path)

    schedule_to_csv(schedule)
