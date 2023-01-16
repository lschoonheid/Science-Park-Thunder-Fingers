class Room(object):
    """Object to store room information.

    #TODO #3
    Args:
        object (_type_): _description_
    """

    def __init__(self, uid: int, name: str, capacity: int) -> None:
        self.id = uid
        self.node_type = "Room"
        self.name = name
        self.capacity = capacity

    def __repr__(self) -> str:
        return f"room {self.name}"
