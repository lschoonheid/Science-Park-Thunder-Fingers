class Room(object):
    """Object to store room information.

    #TODO #3
    Args:
        object (_type_): _description_
    """

    def __init__(self, uid: int, name: str, capacity: int) -> None:
        self.id = uid
        self.name = name
        self.capacity = capacity
