from .room import Room


class Timeslot:
    def __init__(self, uid: int, activity: str, room: Room, day: int, period: int) -> None:
        self.id = uid
        self.node_type = "Timeslot"
        period_names = [i for i in range(9, 21, 2)]
