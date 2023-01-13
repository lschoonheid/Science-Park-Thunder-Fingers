from csv import DictReader


def csv_to_dicts(input_file: str):
    with open(input_file, "r") as file:
        return [row for row in DictReader(file)]
