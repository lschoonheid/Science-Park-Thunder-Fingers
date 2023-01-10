# First test program to make lesroosters with OOB

import csv
from vakken import Lecture
from zalen import Room
from studenten import Student

# load csv files

class Schedule():
    def __init__(self) -> None:
        # Lectures is a dictionary that holds lecture name with corresponding info
        self.lectures: dict[str: Lecture] = {}

        # Rooms is a dictionary that hold all rooms with corresponding capacity
        self.rooms: dict[str: Room] = {}

        # Students is a dictionary that hold all students by student number with corresponding info
        self.students: dict[int: Student] = {}

        # Load lecture structures
        self.load_lectures("OOB_data/vakken.csv")

        # Load room structures
        self.load_rooms("OOB_data/zalen.csv")

        # Load student structures
        self.load_students("OOB_data/studenten_en_vakken.csv")


    def load_lectures(self, filename) -> None:
        with open(filename) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            # skip header
            next(csv_reader)
            for row in csv_reader:
                subject = row[0]
                num_hc = row[1]
                num_wc = row[2]
                max_stud_wc = row[3]
                num_prac = row[4]
                max_stud_prac = row[5]
                expected_stud = row[6]
                lecture = {subject: Lecture(subject, num_hc, num_wc, max_stud_wc, num_prac, max_stud_prac,expected_stud)}
                self.lectures.update(lecture)


    def load_rooms(self, filename) -> None:
        with open(filename) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            # skip header
            next(csv_reader)
            for row in csv_reader:
                room_id = row[0]
                room_capacity = row[1]
                room = {room_id: Room(room_id, room_capacity)}
                self.rooms.update(room)


    def load_students(self, filename) -> None:
        with open(filename) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            # skip header
            next(csv_reader)
            for row in csv_reader:
                surname = row[0]
                firstname = row[1]
                std_id = row[2]
                courses = [i for i in row[3:7] if i]
                student = {std_id: Student(surname,firstname,std_id,courses)}
                self.students.update(student)


if __name__ == "__main__":
    schedule = Schedule()