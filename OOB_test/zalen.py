class Room(object):
    """Object to store room information.

    #TODO #3
    Args:
        object (_type_): _description_
    """

    def __init__(self, id: str, capacity: int) -> None:

        self.id = id
        self.capacity = capacity
