class Team(object):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "Name: {self.name} \n\n".format(self=self)
