"""
Program to convert a schedule object into a csv file.
Used in main.py
"""

import csv
from program_code import Schedule, prepare_path

def schedule_to_csv(schedule: Schedule, output_path: str = "output/Schedule_output.csv"):
    """Interface for executing scheduling program."""

    # columns
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
