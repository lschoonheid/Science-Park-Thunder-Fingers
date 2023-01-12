class Room(object):
    """Object to store room information.

    #TODO #3
    Args:
        object (_type_): _description_
    """

    def __init__(self, uid: str, capacity: int) -> None:

        self.id = uid
        self.capacity = capacity
