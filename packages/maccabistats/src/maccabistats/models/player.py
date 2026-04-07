# TODO: can use dataclass
class Player(object):
    def __init__(self, name: str, number: int):
        self.name = name
        self.number = number

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.number == other.number

    def __hash__(self) -> int:
        return hash((self.name, self.number))

    def __repr__(self) -> str:
        return "\nPlayer Name: {self.name}\n" \
               "Player Number: {self.number}\n\n".format(self=self)
